from src.document_processing.document_processor import DocumentProcessor
from src.models.semantic_matcher import SemanticMatcher
from src.models.nli_classifier import NLIClassifier

# Initialize components
processor = DocumentProcessor()
matcher = SemanticMatcher()
nli = NLIClassifier()

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

The customer shall pay INR 60,000 every month.

2. Data Protection

Both parties must keep shared information confidential.
"""

# Extract clauses
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

print("\nNLI INTEGRATION RESULTS")
print("=======================")

# Compare clauses
for original in original_clauses:
    for amendment in amendment_clauses:

        similarity = matcher.calculate_similarity(
            original["clause_text"],
            amendment["clause_text"]
        )

        # Only send sufficiently related clauses to NLI
        if similarity >= 0.5:

            result = nli.predict(
                original["clause_text"],
                amendment["clause_text"]
            )

            print("\nOriginal Clause:", original["clause_number"])
            print("Amendment Clause:", amendment["clause_number"])
            print("Similarity:", round(similarity, 4))
            print("NLI Result:", result["label"])
            print("Confidence:", round(result["confidence"], 4))

        else:
            print(
                "\nSkipped unrelated pair:",
                original["clause_number"],
                "vs",
                amendment["clause_number"]
            )
