# 🔁 Bidirectional ODRL ↔ Natural Language Transformer (LLM + SHACL)

This project enables **bidirectional transformation** between:
- 📝 Natural language policy instructions → **ODRL (Open Digital Rights Language)**
- 📜 ODRL policies → **Human-readable explanations**

It uses:
- ✅ **Large Language Models** (LLM) via [Ollama](https://ollama.com)
- ✅ **Ontology-aware prompting**
- ✅ **SHACL validation** to ensure policy correctness
- ✅ **Fuzzy matching** for round-trip consistency testing
- ✅ **Gradio UI** for easy interaction
- ✅ Optional: Hugging Face Spaces deployment

---

## 🚀 Features

- 🔄 **Bidirectional pipeline** (text ↔ ODRL)
- ✅ **SHACL policy validation**
- 🧠 **LLM-powered constraint handling**
- 📊 **Round-trip test scoring** (with fuzzy match metric)
- 💻 **Gradio web UI**
- ☁️ Optional **Hugging Face Spaces Deployment**

---

## 📁 Folder Structure
bidirectional-transformers-odrl-to-text/ 
├── scripts/ 
│ ├── odrl_to_instructions.py # ODRL → Text 
│ ├── instructions_to_odrl.py # Text → ODRL (.ttl / .jsonld) 
│ ├── validate_and_fix_odrl.py # SHACL validator 
│ ├── fuzzy_match_score.py # Fuzzy round-trip scoring 
│ ├── round_trip_test.py # Complete round-trip pipeline 
│ └── gradio_ui.py # Gradio web app 
├── templates/ 
│ ├── to_odrl_prompt.md 
│ └── to_nl_prompt.md 
├── data/ 
│ ├── instructions/ # Plain text inputs 
│ └── odrl_examples/ # RDF / JSON-LD files 
├── output/ 
│ ├── generated_odrl/ 
│ ├── generated_text/ 
│ ├── round_trip/ 
│ └── validation_reports/ 
├── odrl_policy_validation_shapes/ 
│ └── odrl_policy_shapes.ttl # SHACL rules 
├── config.json # LLM API configuration 
├── requirements.txt # Python dependencies 
└── README.md


---

## ⚙️ Setup

1. Clone the repo:
```bash
git clone https://github.com/Yusra-3033/bidirectional-transformers-odrl-to-text.git
cd bidirectional-transformers-odrl-to-text
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

3.Install dependencies:
```bash
pip install -r requirements.txt
```

4.Add your LLM config:

```bash
# config.json
{
  "llm_provider": "ollama",
  "ollama_base_url": "http://localhost:11434/api/chat",
  "ollama_model": "llama3.3:70b"
}
```

---
## 🧠 Run the Pipeline
➤ Convert ODRL → Plain Text
```bash
python scripts/odrl_to_instructions.py
```

➤ Convert Instructions → ODRL
```bash
python scripts/instructions_to_odrl.py
```

➤ Run SHACL Validation
```bash
python scripts/validate_and_fix_odrl.py
```

➤ Consistency Test: 🧠 ODRL → text → ODRL again, it checks if they match (or at least are semantically equivalent).
```bash
python scripts/test.py
```
---
## 📊 Fuzzy Matching
Evaluate semantic similarity between original and re-generated ODRL:
```bash
from scripts.fuzzy_match_score import fuzzy_match

report = fuzzy_match("original.ttl", "regenerated.ttl", format="ttl")
print(report)
```
Outputs per-field similarity scores and a final percentage.

---
## 💻 Gradio Web Interface
Launch UI:
```bash
python scripts/gradio_ui.py
```
### Features:

📝 Text → ODRL (choose format)

📂 Upload ODRL → Explanation

🔁 Round-trip tester with side-by-side view

---
## ☁️ Deploy to Hugging Face Spaces
1. Create a new space on huggingface.co/spaces
2. Use Gradio SDK
3. Upload:
  * app.py (rename gradio_ui.py)
  * requirements.txt
  * templates/, config.json, odrl_policy_validation_shapes/

---
## 👩‍🎓 Ideal For
* Master's thesis projects
* Policy transparency research
* LLM+RDF automation
* SHACL + ODRL compliance testing
* Data governance & digital rights systems

---

## 📖 Citation / Inspiration
This work is inspired by:



---
## 🧠 Credits
* Built by Yusra Abdulrahman, 2025
* Supervised by []
* University of Duisburg Essen

---
## 🛡 License
Open for academic and research use.
