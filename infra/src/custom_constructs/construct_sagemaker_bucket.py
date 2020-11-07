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
from aws_cdk import core, aws_s3, aws_kms


class ConstructSageMakerBucket(aws_s3.Bucket):
    """
    Custom IAM policy construct , with minimum permissions required to run the preprocessor
    """

    def __init__(self, scope: core.Construct, id: str, bucket_name: str,
                 encrypt: bool = False):
        key = None
        encryption = None

        if encrypt:
            key = aws_kms.Key(scope, "bucketkms")
            encryption = aws_s3.BucketEncryption.KMS

        super().__init__(scope, id, bucket_name=bucket_name, encryption_key=key, encryption=encryption)
