from src.models.nli_classifier import NLIClassifier


def main():
    classifier = NLIClassifier()

    test_cases = [
        {
            "name": "Contradiction",
            "premise": (
                "The monthly service fee payable by the customer "
                "shall be INR 50,000."
            ),
            "hypothesis": (
                "The monthly service fee payable by the customer "
                "shall be INR 60,000."
            )
        },
        {
            "name": "Entailment",
            "premise": (
                "The customer shall pay INR 50,000 every month "
                "for the services."
            ),
            "hypothesis": (
                "The monthly service fee payable by the customer "
                "is INR 50,000."
            )
        },
        {
            "name": "Neutral",
            "premise": (
                "The monthly service fee payable by the customer "
                "shall be INR 50,000."
            ),
            "hypothesis": (
                "The agreement shall remain valid for three years."
            )
        }
    ]

    for test in test_cases:
        print("\n" + "=" * 60)
        print("TEST:", test["name"])
        print("Premise:", test["premise"])
        print("Hypothesis:", test["hypothesis"])

        result = classifier.predict(
            test["premise"],
            test["hypothesis"]
        )

        print("\nPredicted label:", result["label"])
        print("Confidence:", round(result["confidence"], 4))
        print("Probabilities:")

        for label, score in result["probabilities"].items():
            print(f"  {label}: {score:.4f}")


if __name__ == "__main__":
    main()
