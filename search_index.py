
import json
import os
import argparse


def load_vocabulary(vocabulary_path):
    with open(vocabulary_path, "r", encoding="utf-8") as file:
        return json.load(file)


def search_term(term, vocabulary, postings_path):
    if term not in vocabulary:
        print("Term not found in the index.")
        return

    information = vocabulary[term]

    print("\nTerm:", term)
    print("Collection Frequency (CF):", information["cf"])
    print("Document Frequency (DF):", information["df"])

    with open(postings_path, "rb") as file:
        file.seek(information["offset"])
        record_bytes = file.read(information["length"])

    record = json.loads(record_bytes.decode("utf-8"))

    print("\nPositional Postings:")

    for posting in record["postings"]:
        print(
            "Document ID:", posting["doc_id"],
            "| Positions:", posting["positions"]
        )


def main(index_folder):
    vocabulary_path = os.path.join(
        index_folder, "vocabulary.json"
    )

    postings_path = os.path.join(
        index_folder, "postings.jsonl"
    )

    if not os.path.exists(vocabulary_path):
        print("Vocabulary file not found. Build the index first.")
        return

    if not os.path.exists(postings_path):
        print("Postings file not found. Build the index first.")
        return

    vocabulary = load_vocabulary(vocabulary_path)

    print("Telugu Positional Index Search")
    print("Vocabulary loaded into RAM.")
    print("Type 'exit' to stop.")

    while True:
        term = input("\nEnter a Telugu search term: ").strip()

        if term.lower() == "exit":
            print("Search ended.")
            break

        search_term(term, vocabulary, postings_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Search Telugu Positional Index"
    )

    parser.add_argument("--index-folder", default="index")

    args = parser.parse_args()

    main(args.index_folder)
