
import json
import unicodedata
import regex
import argparse


# Match Telugu words, including Telugu vowel signs and other marks.
TELUGU_WORD_PATTERN = regex.compile(
    r"[\p{Script=Telugu}\p{M}]+"
)


def tokenize(text):
    """Normalize Telugu text and return its word tokens."""
    text = unicodedata.normalize("NFC", text)
    return TELUGU_WORD_PATTERN.findall(text)


def preprocess_file(input_file, output_file):
    document_count = 0

    with open(input_file, "r", encoding="utf-8") as source:
        with open(output_file, "w", encoding="utf-8") as target:

            for line in source:
                document = json.loads(line)

                tokens = tokenize(document["text"])

                result = {
                    "doc_id": document["doc_id"],
                    "title": document["title"],
                    "tokens": tokens
                }

                target.write(
                    json.dumps(result, ensure_ascii=False) + "\n"
                )

                document_count += 1

                if document_count % 10 == 0:
                    print("Preprocessed documents:", document_count)

    print("\nPreprocessing completed!")
    print("Total documents:", document_count)
    print("Output file:", output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Telugu Text Preprocessor"
    )

    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    preprocess_file(args.input, args.output)
