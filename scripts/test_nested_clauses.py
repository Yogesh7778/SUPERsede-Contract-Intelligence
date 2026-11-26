from src.document_processing.document_processor import DocumentProcessor

processor = DocumentProcessor()

sample_text = """
1. Payment Terms

The customer must pay the agreed fees.

1.1 Monthly Fees

The customer shall pay INR 50,000 every month.

1.2 Payment Due Date

Payment must be completed by the fifth day of each month.

1.3 Late Payment Charges

Late payments will attract additional charges.

2. Confidentiality

Both parties must protect confidential information.

2.1 Confidential Information

Business and financial information shall remain confidential.
"""

clauses = processor.extract_clauses(
    sample_text,
    document_id="nested-contract-001",
    document_type="original"
)

print("\nNESTED CLAUSE PROCESSING RESULTS")
print("================================")

for clause in clauses:
    print("\nClause:", clause["clause_number"])
    print("Parent:", clause["parent_clause_number"])
    print("Text:", clause["clause_text"])

print("\nTotal clauses:", len(clauses))
