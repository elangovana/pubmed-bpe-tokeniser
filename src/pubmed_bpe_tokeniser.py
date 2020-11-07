import argparse
import glob
import json
import logging
import os
import sys
import tempfile
from typing import List

from tokenizers import CharBPETokenizer


class PubmedBPETokenisor:

    def __init__(self, vocab_size=10000, min_frequency=2, lower_case=False):
        self.min_frequency = min_frequency
        self.vocab_size = vocab_size
        self._tokenizer = CharBPETokenizer(unk_token="<UNK>", lowercase=lower_case)
        self._special_tokens = ["<PAD>"]

    @property
    def _logger(self):
        return logging.getLogger(__name__)

    def train(self, pubmed_json_files: List[str], dest_token_file_json, tempdir=None):
        tempdir = tempdir or tempfile.mkdtemp()

        self._logger.info("Extracting title and abstract..")
        temp_textfiles = []
        # Extract text only and write to temp
        for f in pubmed_json_files:
            temp_textfiles.append(self._extract_text_file(f, tempdir))

        # Train tokeniser
        self._logger.info("Running tokeniser with vocab size {}".format(self.vocab_size))
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
        self._logger.info("Training using pubmed json files in  {}".format(pubmed_json_files_dir))

        json_files = list(glob.glob("{}/*.json".format(pubmed_json_files_dir.rstrip(os.sep))))

        self._logger.info("Starting training using {} files".format(len(json_files)))

        self.train(json_files, dest_token_file_json, tempdir)

        self._logger.info("Training complete".format(len(json_files)))


    def _clean_up_temp_files(self, textfiles):
        self._logger.info("Cleaning up temp files")
        for f in textfiles:
            os.remove(f)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--datadir",
                        help="The input train  dir", required=True)
    parser.add_argument("--outputfile",
                        help="The output vocab file", default="vocab.json")

    parser.add_argument("--vocabsize",
                        help="The vocab size", default=20000, type=int)

    parser.add_argument("--log-level", help="Log level", default="INFO", choices={"INFO", "WARN", "DEBUG", "ERROR"})
    args = parser.parse_args()

    # Set up logging
    logging.basicConfig(level=logging.getLevelName(args.log_level), handlers=[logging.StreamHandler(sys.stdout)],
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    print(args.__dict__)

    # Run
    tokenisor = PubmedBPETokenisor(vocab_size=args.vocabsize)
    tokenisor.train_from_dir(args.datadir, args.outputfile)
