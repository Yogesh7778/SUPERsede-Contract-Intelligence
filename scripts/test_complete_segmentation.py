from src.document_processing.document_processor import DocumentProcessor

processor = DocumentProcessor()

sample_text = """
1. Payment Terms

The customer must pay the agreed fees.

1.1 Monthly Fees

The customer shall pay INR 50,000 every month.

1.2 Payment Due Date

Payment must be completed by the fifth day.

CONFIDENTIALITY

Both parties must protect confidential information.

2. Termination

Either party may terminate this agreement.

2.1 Notice Period

A written notice of 30 days is required.
"""

clauses = processor.extract_clauses(
    sample_text,
    document_id="complete-contract-001",
    document_type="original"
)

print("\nCOMPLETE CLAUSE SEGMENTATION RESULTS")
print("====================================")

for clause in clauses:
    print(
        f"\nClause: {clause['clause_number']}"
        f" | Parent: {clause['parent_clause_number']}"
    )
    print("Text:", clause["clause_text"])

print("\nTotal clauses:", len(clauses))
