import os
import json
import requests
import rdflib
from pathlib import Path
from difflib import unified_diff
from fuzzy_match_score import fuzzy_match

# Load config
with open("config.json") as f:
    config = json.load(f)

llama_url = config["ollama_base_url"]
llama_model = config["ollama_model"]

# Prompt templates
TO_NL_TEMPLATE = "templates/to_nl_prompt.md"
TO_ODRL_TEMPLATE = "templates/to_odrl_prompt.md"

# Utilities
def read_template(path):
    with open(path) as f:
        return f.read()

def ask_llm(prompt):
    payload = {
        "model": llama_model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False
    }
    try:
        r = requests.post(llama_url, json=payload)
        r.raise_for_status()
        return r.json()["message"]["content"]
    except Exception as e:
        print("❌ Error calling LLM:", e)
        return "ERROR"

def clean_llm_output(response_text):
    for tag in ["```", "```turtle", "```ttl", "```jsonld", "```rdf"]:
        response_text = response_text.replace(tag, "")
    return response_text.strip()

def rdf_to_instruction(graph, template_path):
    # very basic extract and explain
    perms = []
    ns = {"odrl": rdflib.Namespace("http://www.w3.org/ns/odrl/2/")}
    for s, p, o in graph.triples((None, rdflib.RDF.type, ns["odrl"].Policy)):
        for perm in graph.objects(s, ns["odrl"].permission):
            action = graph.value(perm, ns["odrl"].action)
            target = graph.value(perm, ns["odrl"].target)
            assignee = graph.value(perm, ns["odrl"].assignee)
            assigner = graph.value(perm, ns["odrl"].assigner)
            constraint = graph.value(perm, ns["odrl"].constraint)
            perms.append({
                "type": "Permission",
                "action": str(action),
                "target": str(target),
                "assignee": str(assignee),
                "assigner": str(assigner),
                "constraint": str(constraint) if constraint else None
            })
    template = read_template(template_path)
    prompt = template.replace("{{POLICY_JSON}}", json.dumps(perms, indent=2))
    return ask_llm(prompt)

def instruction_to_rdf(text, format, template_path):
    template = read_template(template_path)
    prompt = template.replace("{{INSTRUCTION}}", text).replace("{{FORMAT}}", format)
    return clean_llm_output(ask_llm(prompt))

def round_trip(input_file, format="ttl"):
    g = rdflib.Graph()
    g.parse(input_file, format="turtle" if format == "ttl" else "json-ld")
    
    # Step 1: ODRL → text
    explanation = rdf_to_instruction(g, TO_NL_TEMPLATE)
    print(f"\n📝 Instruction generated:\n{explanation}\n")

    # Step 2: text → ODRL
    regenerated = instruction_to_rdf(explanation, format, TO_ODRL_TEMPLATE)
    
    # Save output
    Path("output/pipeline_test").mkdir(parents=True, exist_ok=True)
    output_path = f"output/pipeline_test/regenerated_policy.{format}"
    with open(output_path, "w") as f:
        f.write(regenerated)
    
    # Step 3: Compare graphs
    g2 = rdflib.Graph()
    g2.parse(data=regenerated, format="turtle" if format == "ttl" else "json-ld")
    
    is_same = g.isomorphic(g2)
    print("✅ Graphs are isomorphic!" if is_same else "⚠️ Graphs differ (non-isomorphic).")
    if not is_same:
        diff = unified_diff(
            g.serialize(format="turtle").splitlines(),
            g2.serialize(format="turtle").splitlines(),
            fromfile='original',
            tofile='regenerated',
            lineterm=''
        )
        print("\n".join(diff))

if __name__ == "__main__":
    input_file = "data/odrl_examples/sample_policy.ttl"  # or .jsonld
    round_trip(input_file, format="ttl")

# Fuzzy match score
print("\n🔍 Fuzzy Match Score:")
score_report = fuzzy_match(
    "data/odrl_examples/sample_policy.ttl",
    "output/pipeline_test/regenerated_policy.ttl",
    format="ttl"
)

print("\n📊 Fuzzy Match Report:\n" + score_report)
