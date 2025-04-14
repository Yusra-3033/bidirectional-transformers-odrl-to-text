# scripts/odrl_to_instructions.py

import json
import rdflib
import openai
from pathlib import Path
import requests
import os

# Load API key
with open("config.json") as f:
    config = json.load(f)

# Load RDF/TTL or JSON-LD file
def load_odrl_rdf(file_path):
    g = rdflib.Graph()
    if file_path.endswith(".ttl"):
        g.parse(file_path, format='turtle')
    elif file_path.endswith(".jsonld"):
        g.parse(file_path, format='json-ld')
    else:
        raise ValueError("Unsupported file format. Please use .ttl or .jsonld")
    return g

# Extract key elements
def extract_policy_elements(graph):
    ns = {
        "odrl": rdflib.Namespace("http://www.w3.org/ns/odrl/2/")
    }

    results = []
    for s, p, o in graph.triples((None, rdflib.RDF.type, ns["odrl"].Policy)):
        perms = graph.objects(subject=s, predicate=ns["odrl"].permission)
        for perm in perms:
            action = graph.value(perm, ns["odrl"].action)
            target = graph.value(perm, ns["odrl"].target)
            assigner = graph.value(perm, ns["odrl"].assigner)
            assignee = graph.value(perm, ns["odrl"].assignee)
            constraint = graph.value(perm, ns["odrl"].constraint)

            results.append({
                "type": "Permission",
                "action": str(action),
                "target": str(target),
                "assigner": str(assigner),
                "assignee": str(assignee),
                "constraint": str(constraint) if constraint else None
            })
    return results

# Generate prompt for LLM
def generate_prompt(policy_data, template_path):
    with open(template_path, 'r') as f:
        template = f.read()
    return template.replace("{{POLICY_JSON}}", json.dumps(policy_data, indent=2))

# Send to OpenAI
def ask_llm(prompt):
    with open("config.json") as f:
        config = json.load(f)

    llama_url = config["ollama_base_url"]
    llama_model = config["ollama_model"]

    payload = {
        "model": llama_model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "stream": False
    }

    try:
        response = requests.post(llama_url, json=payload)
        response.raise_for_status()
        data = response.json()
        return data['message']['content']
    except Exception as e:
        print("❌ Error calling LLAMA:", e)
        return "Error generating response from LLM."

# Main
if __name__ == "__main__":
    input_file = "data/odrl_examples/sample_policy.jsonld"
    output_file = "output/generated_text/sample_output.txt"
    template_file = "templates/to_nl_prompt.md"

    g = load_odrl_rdf(input_file)
    policy = extract_policy_elements(g)
    prompt = generate_prompt(policy, template_file)
    response = ask_llm(prompt)

    Path("output/generated_text/").mkdir(parents=True, exist_ok=True)
    with open(output_file, "w") as f:
        f.write(response)

    print("✅ Explanation generated and saved.")
