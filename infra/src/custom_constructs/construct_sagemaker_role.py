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
from aws_cdk.aws_iam import IManagedPolicy, ServicePrincipal


class ConstructSageMakerRole(aws_iam.Role):
    """
    Custom SageMaker role construct , with minimum permissions required to run the preprocessor
    """

    def __init__(self, scope: core.Construct, id: str, managed_policy: IManagedPolicy):
        # S3 Bucket for SageMaker internal access
        s3_sagemaker_bucket_access = aws_iam.PolicyDocument(
            statements=[

                # S3 SageMaker Internal access
                aws_iam.PolicyStatement(actions=["s3:GetObject",
                                                 "s3:PutObject",
                                                 "s3:ListBucket"],
                                        resources=["arn:aws:s3:::*sagemaker*"])
            ]

        )

        # SageMaker Cloud Watch Access
        cloudwatch_access = aws_iam.PolicyDocument(
            statements=[aws_iam.PolicyStatement(actions=["cloudwatch:PutMetricData",
                                                         "cloudwatch:GetMetricData",
                                                         "cloudwatch:GetMetricStatistics",
                                                         "cloudwatch:ListMetrics",
                                                         "logs:CreateLogGroup",
                                                         "logs:CreateLogStream",
                                                         "logs:DescribeLogStreams",
                                                         "logs:PutLogEvents",
                                                         "logs:GetLogEvents"],
                                                resources=["*"])
                        ])

        super().__init__(scope, id,
                         assumed_by=ServicePrincipal("sagemaker.amazonaws.com"),
                         description="The sagemaker role to access the data and ecr",
                         inline_policies={

                             "S3SageMakerBucketAccess": s3_sagemaker_bucket_access,
                             "CloudWatchAccess": cloudwatch_access

                         },
                         managed_policies=[managed_policy]
                         )
