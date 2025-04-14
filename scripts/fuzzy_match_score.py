import rdflib
import difflib

def extract_policy_data(graph):
    ns = {"odrl": rdflib.Namespace("http://www.w3.org/ns/odrl/2/")}
    result = {}

    for s, p, o in graph.triples((None, rdflib.RDF.type, ns["odrl"].Policy)):
        perm = next(graph.objects(s, ns["odrl"].permission), None)
        if perm:
            result["action"] = str(graph.value(perm, ns["odrl"].action))
            result["target"] = str(graph.value(perm, ns["odrl"].target))
            result["assigner"] = str(graph.value(perm, ns["odrl"].assigner))
            result["assignee"] = str(graph.value(perm, ns["odrl"].assignee))

            constraint = graph.value(perm, ns["odrl"].constraint)
            if constraint:
                result["constraint"] = {
                    "leftOperand": str(graph.value(constraint, ns["odrl"].leftOperand)),
                    "operator": str(graph.value(constraint, ns["odrl"].operator)),
                    "rightOperand": str(graph.value(constraint, ns["odrl"].rightOperand)),
                }
    return result

def similarity(a, b):
    if a is None or b is None:
        return 0
    return difflib.SequenceMatcher(None, a, b).ratio()

def fuzzy_match(original_file, regenerated_file, format="ttl"):
    g1 = rdflib.Graph()
    g1.parse(original_file, format=format)

    g2 = rdflib.Graph()
    g2.parse(regenerated_file, format=format)

    p1 = extract_policy_data(g1)
    p2 = extract_policy_data(g2)

    report = []
    total_score = 0
    categories = 0

    for key in ["action", "target", "assigner", "assignee"]:
        score = similarity(p1.get(key), p2.get(key)) * 100
        report.append(f"{key.capitalize()}: {score:.1f}%")
        total_score += score
        categories += 1

    # Constraint comparison (nested)
    c1 = p1.get("constraint", {})
    c2 = p2.get("constraint", {})
    for subkey in ["leftOperand", "operator", "rightOperand"]:
        score = similarity(c1.get(subkey), c2.get(subkey)) * 100
        report.append(f"Constraint.{subkey}: {score:.1f}%")
        total_score += score
        categories += 1

    final_score = total_score / categories if categories else 0
    report.append(f"\n💯 Final Fuzzy Match Score: {final_score:.1f}%")
    
    if final_score < 50:
        print("🚨 Major semantic drift detected — regenerated policy differs too much from original.")

    return "\n".join(report)
