from src.document_processing.document_processor import DocumentProcessor

processor = DocumentProcessor()

result = processor.process_document(
    file_path="dataset/sample_contract.pdf",
    document_id="contract-001",
    document_type="original"
)

print("\nPDF PROCESSING RESULTS")
print("======================")
print("Document ID:", result["document_id"])
print("Total Clauses:", result["total_clauses"])

for clause in result["clauses"]:
    print("\nClause:", clause["clause_number"])
    print("Text:", clause["clause_text"])


