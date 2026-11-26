from src.document_processing.document_processor import DocumentProcessor
processor = DocumentProcessor()

sample_text = """
SERVICE AGREEMENT

Agreement ID: AGR-001
Contract ID: CTR-001
Project ID: PROJ-101
Service Scope: Software Development
Amends Agreement: AGR-001

First Party: ABC Technologies
Second Party: XYZ Solutions

Effective Date: 2026-01-01
Expiry Date: 2026-12-31

Status: Signed

1. Definitions
This agreement is between ABC Technologies and XYZ Solutions.
"""

metadata = processor.extract_metadata(sample_text)

print("\nMETADATA EXTRACTION RESULTS")
print("===========================")

for key, value in metadata.items():
    print(f"{key}: {value}")
