from src.models.semantic_matcher import SemanticMatcher


def main():
    matcher = SemanticMatcher()

    clause_a = (
        "The monthly service fee payable by the customer "
        "shall be INR 50,000."
    )

    candidate_clauses = [
        "The customer must pay INR 50,000 every month.",
        "The agreement shall remain valid for three years.",
        "The monthly subscription charge is INR 60,000."
    ]

    print("\nSource clause:")
    print(clause_a)

    print("\nSimilar clauses:")

    results = matcher.find_similar_clauses(
        clause_a,
        candidate_clauses,
        threshold=0.40
    )

    for result in results:
        print("\nClause:", result["clause"])
        print("Similarity:", round(result["similarity"], 4))


if __name__ == "__main__":
    main()
