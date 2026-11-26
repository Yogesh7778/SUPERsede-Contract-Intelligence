# SUPERSede backend

SUPERSede extracts clauses and metadata from TXT, PDF, and DOCX commercial documents, retrieves related clauses, applies NLI plus temporal/scope/precedence checks, and exposes document-pack comparisons through FastAPI. It is a decision-support system: its conflict and supersession results always require legal review.

## Setup and API

Use the supplied virtual environment or install `./.venv/bin/python -m pip install -r requirements.txt`. Start the backend with `./.venv/bin/python -m uvicorn src.api.main:app --reload`; OpenAPI is at `/docs`. Create `POST /packs`, upload files to `POST /packs/{pack_id}/documents`, then use `POST /packs/{pack_id}/compare`.

## ContractNLI protocol

`scripts/train_contractnli.py` fine-tunes only the supplied train split and chooses the best validation-loss checkpoint. `scripts/evaluate_contractnli.py --model cross-encoder/nli-deberta-v3-small --split test` evaluates either baseline or saved checkpoint using the untouched test split. Positive examples use verified evidence-centered contexts. NotMentioned examples have no evidence and are evaluated through multiple coverage windows plus conservative document aggregation. This is explicitly an approximation to the original document-level task; it does not claim random windows prove absence.

Run tests with `./.venv/bin/python -m pytest tests -q` and the Phase 3 suite with `PYTHONPATH=. ./.venv/bin/python scripts/test_phase3.py`.

Final untouched ContractNLI test results are saved in `reports/evaluation/`: pretrained macro F1 0.342 versus fine-tuned macro F1 0.494. The fine-tuned checkpoint is `models/checkpoints/contractnli-deberta-mps-balanced-96`; it was trained on 96 balanced documents, so it is an MPS-safe practical checkpoint rather than full-corpus fine-tuning. Use `./.venv/bin/python scripts/evaluate_contractnli.py --model models/checkpoints/contractnli-deberta-mps-balanced-96 --split test --batch-size 1 --max-length 256 --device mps --output reports/evaluation/finetuned_test_full.json` to reproduce its final evaluation. Run `./.venv/bin/python scripts/audit_synthetic_dataset.py` to validate all 60 synthetic-pack evidence references.
