import json
import requests
from pathlib import Path

# Load config
with open("config.json") as f:
    config = json.load(f)

llama_url = config["ollama_base_url"]
llama_model = config["ollama_model"]

def read_instruction(file_path):
    with open(file_path, "r") as f:
        return f.read().strip()

def build_prompt(instruction, format, template_path):
    with open(template_path, "r") as f:
        template = f.read()
    return template.replace("{{INSTRUCTION}}", instruction).replace("{{FORMAT}}", format)

def ask_llm(prompt):
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
        return response.json()['message']['content']
    except Exception as e:
        print("❌ Error calling LLM:", e)
        return "ERROR"

def save_output(content, path):
    with open(path, "w") as f:
        f.write(content)

def clean_llm_output(response_text):
    # Remove triple backticks and optional language tags
    if "```" in response_text:
        response_text = response_text.strip()
        response_text = response_text.replace("```turtle", "")
        response_text = response_text.replace("```jsonld", "")
        response_text = response_text.replace("```ttl", "")
        response_text = response_text.replace("```rdf", "")
        response_text = response_text.replace("```", "")
    return response_text.strip()

if __name__ == "__main__":
    input_path = "data/instructions/input.txt"
    template_path = "templates/to_odrl_prompt.md"
    ttl_output = "output/generated_odrl/generated_policy.ttl"
    jsonld_output = "output/generated_odrl/generated_policy.jsonld"

    instruction = read_instruction(input_path)

    for fmt, out_file in [("ttl", ttl_output), ("jsonld", jsonld_output)]:
        print(f"🔄 Generating ODRL in {fmt} format...")
        prompt = build_prompt(instruction, fmt, template_path)
        response = ask_llm(prompt)

        if "ERROR" not in response:
            cleaned_response = clean_llm_output(response)
            save_output(cleaned_response, out_file)
            #save_output(response, out_file)
            print(f"✅ Saved to {out_file}")
        else:
            print(f"❌ Failed to generate {fmt} policy.")
