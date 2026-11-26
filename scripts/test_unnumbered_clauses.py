from src.document_processing.document_processor import DocumentProcessor

processor = DocumentProcessor()

sample_text = """
PAYMENT TERMS

The customer shall pay INR 50,000 every month.

CONFIDENTIALITY

Both parties must protect confidential information.

TERMINATION

Either party may terminate the agreement with 30 days written notice.
"""

clauses = processor.extract_clauses(
    sample_text,
    document_id="unnumbered-contract-001",
    document_type="original"
)

print("\nUNNUMBERED CLAUSE TEST")
print("======================")

print("Total clauses:", len(clauses))

for clause in clauses:
    print("\nClause:", clause["clause_number"])
    print("Parent:", clause["parent_clause_number"])
    print("Text:", clause["clause_text"])
