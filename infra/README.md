
### Prerequisites 

1. Install AWS CDK



## Setup 

```bash

pip install -r infra/src/requirements.txt

```
2. Synth Cloudformation

```bash
export PYTHON_PATH=./infra/src

cdk --app "python infra/src/app.py" synth
```