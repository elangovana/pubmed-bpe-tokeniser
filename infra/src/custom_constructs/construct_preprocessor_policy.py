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
from aws_cdk import aws_iam, core
from aws_cdk.core import Stack


class ConstructPreprocessorPolicy(aws_iam.ManagedPolicy):
    """
    Custom IAM policy construct , with minimum permissions required to run the preprocessor
    """

    def __init__(self, scope: core.Construct, id: str, s3_src_location: str, s3_dest_location: str,
                 docker_repo_arn: str,
                 kms_key_name: str = None):
        super().__init__(scope, id)

        statements = []
        # S3 Read / Write access to read raw data and write temp/cache files
        statements += [aws_iam.PolicyStatement(actions=["s3:GetObject"
                                                        ],
                                               resources=["arn:aws:s3:::" + s3_src_location]),

                       aws_iam.PolicyStatement(actions=["s3:ListBucket", "s3:GetBucketLocation"],
                                               resources=["arn:aws:s3:::" + core.Fn.select(0,
                                                                                           core.Fn.split("/",
                                                                                                         s3_src_location))]
                                               )
                       ]

        # S3 Write access to write results
        statements += [aws_iam.PolicyStatement(actions=["s3:GetObject",
                                                        "s3:PutObject"
                                                        ],
                                               resources=["arn:aws:s3:::" + s3_dest_location]),

                       aws_iam.PolicyStatement(actions=["s3:ListBucket", "s3:GetBucketLocation"],
                                               resources=["arn:aws:s3:::" + core.Fn.select(0,
                                                                                           core.Fn.split("/",
                                                                                                         s3_dest_location))]
                                               )
                       ]

        # Docker access
        statements += [
            aws_iam.PolicyStatement(
                actions=["ecr:GetDownloadUrlForLayer",
                         "ecr:BatchGetImage",
                         "ecr:BatchCheckLayerAvailability"],
                resources=[docker_repo_arn]),
            aws_iam.PolicyStatement(actions=["ecr:GetAuthorizationToken"],
                                    resources=["*"])]

        # KMS key
        if kms_key_name is not None:
            statements += [aws_iam.PolicyStatement(actions=["kms:Decrypt",
                                                            "kms:DescribeKey",
                                                            "kms:Encrypt",
                                                            "kms:GenerateDataKey*",
                                                            "kms:ReEncrypt*"],
                                                   resources=["arn:aws:kms:{}:{}:key/{}".format(Stack.of(self).region,
                                                                                                Stack.of(self).account,
                                                                                                kms_key_name)])]

        # Add all statements to policy
        for stmt in statements:
            self.add_statements(stmt)
