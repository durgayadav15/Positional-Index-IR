
import json
import os
import sqlite3
import argparse


def build_index(input_file, index_folder):

    os.makedirs(index_folder, exist_ok=True)

    database_path = os.path.join(index_folder, "temporary.db")
    postings_path = os.path.join(index_folder, "postings.jsonl")
    vocabulary_path = os.path.join(index_folder, "vocabulary.json")

    if os.path.exists(database_path):
        os.remove(database_path)

    vocabulary = {}

    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE postings (
            term TEXT,
            doc_id INTEGER,
            positions TEXT
        )
    """)

    print("Building positional index...")

    with open(input_file, "r", encoding="utf-8") as source:

        for line in source:

            document = json.loads(line)
            doc_id = document["doc_id"]

            positions_by_term = {}

            for position, term in enumerate(document["tokens"], start=1):

                if term not in positions_by_term:
                    positions_by_term[term] = []

                positions_by_term[term].append(position)

            for term, positions in positions_by_term.items():

                cursor.execute(
                    "INSERT INTO postings VALUES (?, ?, ?)",
                    (term, doc_id, json.dumps(positions))
                )

                if term not in vocabulary:
                    vocabulary[term] = {
                        "cf": 0,
                        "df": 0,
                        "offset": 0,
                        "length": 0
                    }

                vocabulary[term]["cf"] += len(positions)
                vocabulary[term]["df"] += 1

    connection.commit()

    print("Writing postings to disk...")

    with open(postings_path, "wb") as postings_file:

        for term in sorted(vocabulary):

            cursor.execute(
                """
                SELECT doc_id, positions
                FROM postings
                WHERE term = ?
                ORDER BY doc_id
                """,
                (term,)
            )

            term_postings = [
                {
                    "doc_id": row[0],
                    "positions": json.loads(row[1])
                }
                for row in cursor.fetchall()
            ]

            record = {
                "term": term,
                "postings": term_postings
            }

            line = (
                json.dumps(record, ensure_ascii=False) + "\n"
            ).encode("utf-8")

            offset = postings_file.tell()
            postings_file.write(line)

            vocabulary[term]["offset"] = offset
            vocabulary[term]["length"] = len(line)

    with open(vocabulary_path, "w", encoding="utf-8") as vocab_file:

        json.dump(
            vocabulary,
            vocab_file,
            ensure_ascii=False,
            indent=2
        )

    connection.close()
    os.remove(database_path)

    print("\nIndex construction completed!")
    print("Total unique terms:", len(vocabulary))
    print("Vocabulary file:", vocabulary_path)
    print("Postings file:", postings_path)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Telugu Positional Inverted Index Builder"
    )

    parser.add_argument("--input", required=True)
    parser.add_argument("--index-folder", default="index")

    args = parser.parse_args()

    build_index(args.input, args.index_folder)
