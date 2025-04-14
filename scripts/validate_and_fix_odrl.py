from pyshacl import validate
import rdflib
import os
import sys
from pathlib import Path

def load_graph(file_path):
    g = rdflib.Graph()
    ext = os.path.splitext(file_path)[1]
    if ext == ".ttl":
        g.parse(file_path, format="turtle")
    elif ext == ".jsonld":
        g.parse(file_path, format="json-ld")
    else:
        raise ValueError("Unsupported format. Use .ttl or .jsonld")
    return g

def validate_graph(data_graph, shapes_graph_path):
    shapes_graph = rdflib.Graph()
    shapes_graph.parse(shapes_graph_path, format="turtle")
    
    conforms, report_graph, report_text = validate(
        data_graph,
        shacl_graph=shapes_graph,
        inference='rdfs',
        abort_on_first=False,
        meta_shacl=False,
        debug=False
    )
    return conforms, report_text

if __name__ == "__main__":
    input_file = "output/generated_odrl/generated_policy.ttl"  # or .jsonld
    shape_file = "odrl_policy_validation/odrl_policy_shapes.ttl"
    report_output = "output/validation_reports/validation_report.txt"

    try:
        print(f"🔍 Validating: {input_file}")
        g = load_graph(input_file)
        conforms, report = validate_graph(g, shape_file)

        Path("output/validation_reports").mkdir(exist_ok=True)
        with open(report_output, "w") as f:
            f.write(report)

        if conforms:
            print("✅ Policy is valid according to SHACL shapes.")
        else:
            print("❌ Policy has validation errors. See the report.")
            print(f"📝 Report saved to: {report_output}")

    except Exception as e:
        print("❌ Validation failed:", e)
