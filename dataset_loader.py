
import bz2
import json
import argparse
import re
import mwxml
import mwparserfromhell


def clean_wikipedia_text(text):
    """Remove Wikipedia markup and clean article text."""

    if not text:
        return ""

    parsed_text = mwparserfromhell.parse(text)
    clean_text = parsed_text.strip_code()

    # Remove URLs
    clean_text = re.sub(r'https?://\S+', ' ', clean_text)

    # Normalize whitespace
    clean_text = re.sub(r'\s+', ' ', clean_text)

    return clean_text.strip()


def extract_articles(input_file, output_file, max_docs=None):

    document_count = 0

    print("Starting Telugu Wikipedia extraction...")

    with bz2.open(input_file, "rb") as xml_file:

        dump = mwxml.Dump.from_file(xml_file)

        with open(output_file, "w", encoding="utf-8") as out:

            for page in dump:

                # Only process main Wikipedia articles
                if page.namespace != 0:
                    continue

                latest_text = None

                for revision in page:
                    if revision.text:
                        latest_text = revision.text

                if not latest_text:
                    continue

                clean_text = clean_wikipedia_text(latest_text)

                if not clean_text:
                    continue

                document_count += 1

                document = {
                    "doc_id": document_count,
                    "title": page.title,
                    "text": clean_text
                }

                out.write(
                    json.dumps(document, ensure_ascii=False) + "\n"
                )

                if document_count % 10 == 0:
                    print(f"Extracted {document_count} articles...")

                if max_docs and document_count >= max_docs:
                    break

    print("\nExtraction completed!")
    print("Total documents:", document_count)
    print("Output file:", output_file)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Telugu Wikipedia Article Extractor"
    )

    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--max-docs", type=int, default=None)

    args = parser.parse_args()

    extract_articles(
        args.input,
        args.output,
        args.max_docs
    )
