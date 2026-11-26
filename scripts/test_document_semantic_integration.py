from src.document_processing.document_processor import DocumentProcessor
from src.models.semantic_matcher import SemanticMatcher

# Initialize both components
processor = DocumentProcessor()
matcher = SemanticMatcher()

# Original contract
original_text = """
1. Payment Terms

The customer shall pay INR 50,000 every month.

2. Confidentiality

Both parties must protect confidential information.
"""

# Amendment
amendment_text = """
1. Revised Payment Terms

The monthly subscription charge is INR 60,000.

2. Data Protection

Both parties must keep shared information confidential.
"""

# Extract clauses from both documents
original_clauses = processor.extract_clauses(
    original_text,
    "contract-001",
    "original"
)

amendment_clauses = processor.extract_clauses(
    amendment_text,
    "amendment-001",
    "amendment"
)

print("\nDOCUMENT SEMANTIC INTEGRATION")
print("==============================")

# Compare every original clause with every amendment clause
for original in original_clauses:
    for amendment in amendment_clauses:

        similarity = matcher.calculate_similarity(
            original["clause_text"],
            amendment["clause_text"]
        )

        print("\nOriginal:", original["clause_number"])
        print("Amendment:", amendment["clause_number"])
        print("Similarity:", round(similarity, 4))

