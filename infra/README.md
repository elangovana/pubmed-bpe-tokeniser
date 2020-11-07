
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

### Deploy the stacks in `CDK.out` once you run CDK Synth

#### Continous integration stack 
    
1. Deploy the cdk.out/bpe-tokeniser-1-CI.template.json 

1. Once you deploy the Continous integration stack , enable the github connections on AWS Codepipeline
    ![docs/connections.png](docs/connections.png)
    
    
#### SageMaker 
    
1. Deploy the cdk.out/bpe-tokeniser-2-sagemaker.template.json, this deploys the Sagemaker role and bucket.

     ![docs/sagemakerstack_input.png](docs/sagemakerstack_input.png) 
     
     Make a note of the output role
     
     ![docs/sagemakerstack_output.png](docs/sagemakerstack_output.png) 

