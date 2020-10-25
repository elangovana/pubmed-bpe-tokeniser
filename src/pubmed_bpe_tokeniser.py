
import glob
import json
import os
import tempfile
from typing import List

from tokenizers import CharBPETokenizer


class PubmedBPETokenisor:

    def __init__(self, vocab_size=10000, min_frequency=2, lower_case=False):
        self.min_frequency = min_frequency
        self.vocab_size = vocab_size
        self._tokenizer = CharBPETokenizer(unk_token="<UNK>", lowercase=lower_case)
        self._special_tokens = ["<PAD>" ]

    def train(self, pubmed_json_files: List[str], dest_token_file_json, tempdir=None):
        tempdir = tempdir or tempfile.mkdtemp()

        temp_textfiles = []
        # Extract text only and write to temp
        for f in pubmed_json_files:
            temp_textfiles.append(self._extract_text_file(f, tempdir))

        # Train tokeniser
        self._tokenizer.train(files=temp_textfiles, vocab_size=self.vocab_size, min_frequency=self.min_frequency,
                              special_tokens=self._special_tokens)

        self._clean_up_temp_files(temp_textfiles)

        # Save tokens
        self._tokenizer.save(dest_token_file_json)

    def _extract_text_file(self, jsonfile, dest_dir):
        dest_file = os.path.join(dest_dir, os.path.basename(jsonfile))

        with open(jsonfile, "r") as f:
            json_docs = json.load(f)

        with open(dest_file, "w") as f:
            for doc in json_docs:
                f.write("{}\n".format(doc["article_title"]))
                f.write("{}\n".format(doc["article_abstract"]))

        return dest_file

    def train_from_dir(self, pubmed_json_files_dir: str, dest_token_file_json, tempdir=None):
        json_files = list(glob.glob("{}/*.json".format(pubmed_json_files_dir.rstrip(os.sep))))
        self.train(json_files, dest_token_file_json, tempdir)

    def _clean_up_temp_files(self, textfiles):
        for f in textfiles:
            os.remove(f)
