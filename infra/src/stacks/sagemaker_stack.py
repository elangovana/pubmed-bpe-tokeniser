# *****************************************************************************
# * Copyright 2020 Amazon.com, Inc. and its affiliates. All Rights Reserved.  *
#                                                                             *
# Licensed under the Amazon Software License (the "License").                 *
#  You may not use this file except in compliance with the License.           *
# A copy of the License is located at                                         *
#                                                                             *
#  http://aws.amazon.com/asl/                                                 *
#                                                                             *
#  or in the "license" file accompanying this file. This file is distributed  *
#  on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either  *
#  express or implied. See the License for the specific language governing    *
#  permissions and limitations under the License.                             *
# *****************************************************************************

from aws_cdk import core
from aws_cdk.core import Aws

from custom_constructs.construct_preprocessor_policy import ConstructPreprocessorPolicy
from custom_constructs.construct_sagemaker_bucket import ConstructSageMakerBucket
from custom_constructs.construct_sagemaker_role import ConstructSageMakerRole


class SageMakerStack(core.Stack):
    """
    Deploys necessary permission to run SageMaker Processing Jobs
    """

    def __init__(self, scope: core.Construct, id: str, *, encrypt_buckets=False, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # CFN parameters - docker repo
        docker_repo_arn_parameter = core.CfnParameter(self, "dockerRepoArn", type="String",
                                                      description="The docker image repo for sagemaker image, e.g. arn:aws:ecr:us-east-2:1111:repository/bpe-tokeniser", )
        docker_repo_arn = docker_repo_arn_parameter.value_as_string

        # CFN parameters - bucket src bucket
        s3_src_parameter = core.CfnParameter(self, "s3srcbucketPath", type="String",
                                             description="The s3 path from where sagemaker needs to read, e.g. mybucket/prefix/*")
        s3_src_location = s3_src_parameter.value_as_string

        # CFN parameters - bucket dest bucket
        s3_dest_parameter = core.CfnParameter(self, "s3destbucket", type="String",
                                              description="The s3 bucket to create to write sagemaker results to")
        s3_dest = s3_dest_parameter.value_as_string

        # Create SageMaker bucket
        sagemaker_bucket = ConstructSageMakerBucket(self, "SageMaker-Bucket", bucket_name=s3_dest,
                                                    encrypt=encrypt_buckets)

        # Create min Policy
        fd_policy = ConstructPreprocessorPolicy(
            self, "FraudDetectorPreprocressor", s3_src_location=s3_src_location, s3_dest_location=s3_dest,
            docker_repo_arn=docker_repo_arn,
            kms_key_name=sagemaker_bucket.encryption_key.key_arn)

        # Create Sagemaker Role
        sagemaker_role = ConstructSageMakerRole(
            self, "RoleSageMaker", managed_policy=fd_policy, role_name=Aws.STACK_NAME + "-SageMakerRole")

        core.CfnOutput(self, "SageMakeRoleOutput", description="SageMaker Role Arn", export_name="SageMakerRole",
                       value=sagemaker_role.role_arn)
