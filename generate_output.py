
import os
import json
import argparse
import unicodedata


def is_telugu_term(term):
    """Accept terms containing Telugu letters, not isolated vowel marks."""
    has_telugu_letter = False

    for char in term:
        category = unicodedata.category(char)

        if '\u0C00' <= char <= '\u0C7F':
            # Telugu letters are Unicode categories Lo or Lm.
            if category in ("Lo", "Lm"):
                has_telugu_letter = True
        elif char.isalpha():
            return False

    return has_telugu_letter


def main():
    parser = argparse.ArgumentParser(
        description="Generate Telugu positional index output"
    )
    parser.add_argument("--index-folder", default="index")
    parser.add_argument("--output-folder", default="output")
    args = parser.parse_args()

    vocab_path = os.path.join(
        args.index_folder, "vocabulary.json"
    )
    postings_path = os.path.join(
        args.index_folder, "postings.jsonl"
    )

    os.makedirs(args.output_folder, exist_ok=True)

    # Load vocabulary using UTF-8
    with open(vocab_path, "r", encoding="utf-8") as file:
        vocabulary = json.load(file)

    # Keep only valid Telugu terms
    telugu_terms = [
        (term, metadata)
        for term, metadata in vocabulary.items()
        if is_telugu_term(term)
    ]

    # Select the 10 rarest Telugu terms
    rare_terms = sorted(
        telugu_terms,
        key=lambda item: (
            item[1]["df"],
            item[1]["cf"],
            item[0]
        )
    )[:10]

    if len(rare_terms) < 10:
        print(
            "Warning: Only",
            len(rare_terms),
            "valid Telugu terms were found."
        )

    output_path = os.path.join(
        args.output_folder, "output.txt"
    )

    results = []

    # Read positional postings from secondary storage
    with open(postings_path, "rb") as postings_file:
        with open(
            output_path,
            "w",
            encoding="utf-8",
            newline="\n"
        ) as output:

            output.write("TELUGU POSITIONAL INVERTED INDEX\n")
            output.write("=" * 55 + "\n\n")

            output.write("10 RARE TERMS WITH POSITIONAL INDEX\n\n")

            for term, metadata in rare_terms:
                offset = metadata["offset"]
                length = metadata["length"]

                postings_file.seek(offset)

                raw_record = postings_file.read(length)
                record = json.loads(raw_record.decode("utf-8"))

                postings = record.get("postings", [])

                results.append((term, metadata, postings))

                output.write(f"Term: {term}\n")
                output.write(
                    f"Collection Frequency (CF): {metadata['cf']}\n"
                )
                output.write(
                    f"Document Frequency (DF): {metadata['df']}\n"
                )
                output.write("Positional Postings:\n")

                for posting in postings:
                    output.write(
                        f"  Document ID: {posting['doc_id']} | "
                        f"Positions: {posting['positions']}\n"
                    )

                output.write("-" * 55 + "\n\n")

            # Five test cases, two terms per test case
            output.write("\nFIVE TEST CASES\n")
            output.write("=" * 55 + "\n\n")

            for case_number in range(5):
                output.write(
                    f"Test Case {case_number + 1}\n"
                )

                selected = results[
                    case_number * 2:case_number * 2 + 2
                ]

                for term, metadata, postings in selected:
                    output.write(f"Search Term: {term}\n")
                    output.write(
                        f"CF: {metadata['cf']} | "
                        f"DF: {metadata['df']}\n"
                    )
                    output.write(
                        "Matching positional postings:\n"
                    )

                    for posting in postings:
                        output.write(
                            f"  Document ID: {posting['doc_id']} | "
                            f"Positions: {posting['positions']}\n"
                        )

                    output.write("\n")

                output.write("-" * 55 + "\n\n")

    print("Output generated successfully.")
    print("Output file:", output_path)
    print("Valid Telugu rare terms:", len(rare_terms))
    print("Test cases generated: 5")


if __name__ == "__main__":
    main()
