from docx import Document as WordDocument
from src.document_processing.document_processor import DocumentProcessor

# Create a sample Word document
document = WordDocument()

document.add_heading("Service Agreement", level=1)

document.add_heading("1. Definitions", level=2)
document.add_paragraph(
    "This agreement establishes the terms between the parties."
)

document.add_heading("2. Payment Terms", level=2)
document.add_paragraph(
    "The customer shall pay INR 50,000 every month."
)

document.add_heading("3. Confidentiality", level=2)
document.add_paragraph(
    "Both parties shall maintain confidentiality of all shared information."
)

document.add_heading("4. Termination", level=2)
document.add_paragraph(
    "Either party may terminate this agreement with 30 days written notice."
)

document.save("dataset/sample_contract.docx")


# Process the Word document
processor = DocumentProcessor()

result = processor.process_document(
    file_path="dataset/sample_contract.docx",
    document_id="contract-docx-001",
    document_type="original"
)


# Display results
print("\nDOCX PROCESSING RESULTS")
print("=======================")

print("Document ID:", result["document_id"])
print("Document Type:", result["document_type"])
print("Total Clauses:", result["total_clauses"])

for clause in result["clauses"]:
    print("\n-----------------------")
    print("Clause:", clause["clause_number"])
    print("Text:", clause["clause_text"])
