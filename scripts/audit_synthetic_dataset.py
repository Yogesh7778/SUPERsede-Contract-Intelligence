"""Audit held-out synthetic pack labels and evidence without training on them."""
import json
from collections import Counter
from pathlib import Path

def main():
    ground_truth = json.loads(Path("dataset/synthetic/annotations/ground_truth.json").read_text())
    missing = []
    for pack in ground_truth["packs"]:
        for comparison in pack["comparisons"]:
            for evidence in comparison["evidence"]:
                candidates = list(Path("dataset/synthetic").glob(f"**/{evidence['document_id']}.md"))
                if not candidates or evidence["text"] not in candidates[0].read_text():
                    missing.append({"pack_id": pack["pack_id"], "document_id": evidence["document_id"], "clause_id": evidence["clause_id"]})
    summary = {"packs": len(ground_truth["packs"]), "labels": Counter(pack["expected_label"] for pack in ground_truth["packs"]), "evidence_reference_failures": missing, "note": "This is a data-integrity audit, not a performance claim. Use the held-out packs only for final pipeline evaluation."}
    output = Path("reports/evaluation/synthetic_audit.json"); output.parent.mkdir(parents=True, exist_ok=True); output.write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    if missing: raise SystemExit(1)
if __name__ == "__main__": main()
