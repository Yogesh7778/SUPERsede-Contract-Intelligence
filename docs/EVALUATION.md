# Evaluation methodology and recorded results

ContractNLI labels are mapped as Entailment, Contradiction, and NotMentioned. The predefined split is respected: train (7,191), dev (1,037), test (2,091). Evidence integrity was validated for all training records: 0 mismatches between each recorded character span and its text.

For Entailment and Contradiction, the runner forms a context around verified evidence spans. For NotMentioned, it uses several coverage windows and conservative document aggregation; no random chunk is labelled as evidence. This is a practical approximation to the original document-level task, not a claim that all relevant evidence has been observed.

Final untouched-test results (2,091 documents, max length 256, batch size 1, MPS) are: pretrained accuracy 0.389, macro F1 0.342, weighted F1 0.378; fine-tuned accuracy 0.518, macro F1 0.494, weighted F1 0.537. The fine-tuned checkpoint was trained for two epochs on a deterministic balanced 96-document subset (32 per class), with 48 balanced dev documents. Training loss went from 1.390 to 0.602 and dev loss from 0.813 to 0.698. It is a memory-safe partial fine-tune, not a full-corpus result.

Before selecting a model, run the baseline and each saved checkpoint on the untouched test split with `scripts/evaluate_contractnli.py`, save separately named reports, and compare the report fields including class-level metrics, confusion matrix, and listed misclassifications.

The gold-evidence hybrid synthetic evaluation has accuracy 0.383 and macro F1 0.347 across 60 packs. It is intentionally separate from ContractNLI and measures reasoning conditional on gold evidence, not retrieval. The 60 packs have 25 CONSISTENT, 15 CONFLICT, 5 SUPERSEDED, and 15 UNCERTAIN labels. Their evidence-reference audit passed with zero failures. The small synthetic corpus cannot establish real-world accuracy.
