from pathlib import Path
from src.document_processing.document_processor import DocumentProcessor

processor = DocumentProcessor()

# Create a sample contract file.
sample_text = """
SERVICE AGREEMENT

Agreement ID: AGR-001
First Party: ABC Technologies
Second Party: XYZ Solutions

Effective Date: 2026-01-01
Expiry Date: 2026-12-31
Status: Signed

1. Definitions
This agreement establishes the terms between the parties.

2. Payment Terms
The customer shall pay INR 50,000 every month.

3. Confidentiality
Both parties shall maintain confidentiality
of all shared information.

4. Termination
Either party may terminate this agreement
with 30 days written notice.
"""

sample_file = Path("scripts/sample_contract.txt")
sample_file.write_text(sample_text, encoding="utf-8")

# Process the complete document.
result = processor.process_document(
    file_path=sample_file,
    document_id="contract-001",
    document_type="original"
)

print("\nSTRUCTURED DOCUMENT PROCESSING RESULTS")
print("======================================")

print("Document ID:", result["document_id"])
print("Document Type:", result["document_type"])

print("\nMETADATA")
print("--------")

for key, value in result["metadata"].items():
    print(f"{key}: {value}")

print("\nTOTAL CLAUSES:", result["total_clauses"])

for clause in result["clauses"]:
    print("\n---------------------------")
    print("Clause Number:", clause["clause_number"])
    print("Parent Clause:", clause["parent_clause_number"])
    print("Clause Text:", clause["clause_text"])
