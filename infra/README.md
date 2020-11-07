
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

3. Deploy the stacks in `CDK.out` once you run CDK Synth

    - cdk.out/bpe-tokeniser-1-CI.template.json - Continous integration stack 
    - cdk.out/bpe-tokeniser-2-sagemaker.template.json - SageMaker 
    
    1. Once you deploy the Continous integration stack , enable the github connections on AWS Codepipeline
    ![docs/connections.png](docs/connections.png)