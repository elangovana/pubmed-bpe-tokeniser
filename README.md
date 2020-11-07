[![Build Status](https://travis-ci.org/elangovana/pubmed-bpe-tokeniser.svg?branch=main)](https://travis-ci.org/elangovana/pubmed-bpe-tokeniser)

# PubMed Byte Pair Encoding (BPE) Tokenisor
PubMed BPE Tokenisor

## Pre requisites

1. Python 3.7

### Set up

```bash
pip install -r tests/requirements.txt
```

To verify set up

```bash
export PYTHONPATH=./src
pytest
```


## How to run

1. Download pubmed json files using https://github.com/elangovana/pubmed-downloader and save to say "data" directory

2. Run tokeniser with sample data in e.g. tests/data

```bash

export PYTHONPATH=./src
python src/pubmed_bpe_tokeniser.py --datadir tests/data --outputfile vocab.json

```


3. To run on Amazon Sagemaker
    
    - Install sagemaker
    
    ```bash
     pip install -r requirements_notebook.txt
    ```
    
    - See notebook [sagemaker.ipynb](sagemaker.ipynb)



