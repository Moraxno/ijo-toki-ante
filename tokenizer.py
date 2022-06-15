from argparse import ArgumentParser
import json
import os
import re
import numpy as np

import pandas as pd

TEXT_FILE_EXTENSION = ".txt"
DATAFRAME_COL_NAME_WORDS = "word"
DATAFRAME_COL_NAME_COUNTS = "count"

TOKENIZED_LINEFEED = "<LF>"
TOKENIZED_END_OF_SENTENCE = "<EOS>"

STRING_TRANSLATION = str.maketrans({
    " ": None,
    "\r": None,
    "\n": TOKENIZED_LINEFEED
})

ENGLISH_ATOMIZER = r'[A-Za-z\']+|[^A-Za-z\']'
TOKIPONA_ATOMIZER = r'[A-Za-z]+|[^A-Za-z]'

ATOMIZERS = {
    "english": ENGLISH_ATOMIZER,
    "toki-pona": TOKIPONA_ATOMIZER,
}

def get_args():
    ap = ArgumentParser("tokenizer")

    ap.add_argument("in_dir")
    ap.add_argument("language")
    ap.add_argument("out_file")

    return ap.parse_args()


def tokenize_file(file_path, language, tokens):
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read().lower()
    
    atomizer = ATOMIZERS[language]

    atoms = re.findall(atomizer, text)
    atoms = [str.translate(atom, STRING_TRANSLATION) for atom in atoms]
    atoms = [atom for atom in atoms if atom is not None and len(atom) > 0]

    for word in atoms:
        if word not in tokens:
            tokens[word] = 1
        else:
            tokens[word] += 1

    return tokens
    


def main():
    args = get_args()
    in_dir = args.in_dir
    language = args.language

    tokens = {}

    for path, subdirs, files in os.walk(in_dir):
        for file in files:
            name, ext = os.path.splitext(file)
            if name == language and ext == TEXT_FILE_EXTENSION:
                file_path = os.path.join(path, file)
                tokens = tokenize_file(file_path, language, tokens)

    words = list(tokens.keys())
    counts = np.array(list(tokens.values()))

    rank = np.argsort(counts)[::-1]
    sorted_words = [words[r] for r in rank]
    sorted_counts = counts[rank]

    table = pd.DataFrame({DATAFRAME_COL_NAME_WORDS: sorted_words, DATAFRAME_COL_NAME_COUNTS: sorted_counts})
    table.to_csv(args.out_file, index=False)


if __name__ == "__main__":
    main()