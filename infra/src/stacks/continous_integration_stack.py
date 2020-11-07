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

from aws_cdk import (
    core,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    aws_codebuild,
    aws_ecr,
    aws_iam,
    aws_codestarconnections)
from aws_cdk.aws_iam import PolicyStatement, AccountPrincipal
from aws_cdk.core import Aws


class ContinousIntegrationStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # CFN parameters - Source repo
        source_repo_parameter = core.CfnParameter(self, "githubUrl", type="String",
                                                  default="elangovana/pubmed-bpe-tokeniser",
                                                  description="The github repo url")
        source_repo = source_repo_parameter.value_as_string

        # CFN parameters - buildspec repo
        build_spec_parameter = core.CfnParameter(self, "buildSpec", type="String",
                                                 description="The buildspec file",
                                                 default="ci_build/buildspec.build.yml")
        build_spec = build_spec_parameter.value_as_string

        # CFN parameters - build image
        build_image_parameter = core.CfnParameter(self, "buildImage", type="String",
                                                  description="The build image param",
                                                  default="aws/codebuild/standard:4.0")
        build_image = build_image_parameter.value_as_string

        # CFN parameters - build image
        branch_name_parameter = core.CfnParameter(self, "branchName", type="String",
                                                  description="The branch name",
                                                  default="main")
        branch_name = branch_name_parameter.value_as_string

        # CFN parameters - docker repo
        docker_repo_name_parameter = core.CfnParameter(self, "dockerRepo", type="String",
                                                       description="The docker image repo to create in ecr",
                                                       default="bpe-tokeniser")
        docker_repo_name = docker_repo_name_parameter.value_as_string

        # Docker
        docker_repo = aws_ecr.Repository(self, "docker", repository_name=docker_repo_name)

        # Pipeline
        self.pipeline = codepipeline.Pipeline(self, "CI-Pipeline")

        # 1. Code Repo
        source_output = codepipeline.Artifact()
        source_connection = aws_codestarconnections.CfnConnection(self, id="gitrepoconnection",
                                                                  connection_name=Aws.STACK_NAME + "-source-connection",
                                                                  provider_type="GitHub")

        source_action = codepipeline_actions.BitBucketSourceAction(
            action_name="Source",
            connection_arn=source_connection.attr_connection_arn,
            repo=source_repo,
            branch=branch_name,
            output=source_output,
            owner="AWSCodePipeline"

        )
        self.pipeline.add_stage(
            stage_name="Source",
            actions=[source_action]
        )

        # 2. Code Build
        env_variables = {}
        env_variables["docker_image"] = aws_codebuild.BuildEnvironmentVariable(
            value="{}.dkr.ecr.{}.amazonaws.com/{}".format(Aws.ACCOUNT_ID, Aws.REGION,
                                                          docker_repo_name),
            type=aws_codebuild.BuildEnvironmentVariableType.PLAINTEXT)
        build_artifact = codepipeline.Artifact("BuildAndTestArtifacts")
        build_project = aws_codebuild.PipelineProject(
            self,
            "BuildCodeBuild",
            environment=aws_codebuild.BuildEnvironment(
                build_image=aws_codebuild.LinuxBuildImage.from_code_build_image_id(build_image),
                privileged=True),
            build_spec=aws_codebuild.BuildSpec.from_source_filename(build_spec)
        )
        build_action = codepipeline_actions.CodeBuildAction(
            outputs=[build_artifact],
            action_name="BuildAndTest",
            project=build_project,
            input=source_output,
            type=codepipeline_actions.CodeBuildActionType.BUILD,
            run_order=1,
            variables_namespace="BuildTest",
            environment_variables=env_variables
        )
        # Docker push & login permissions
        docker_repo_push = aws_iam.PolicyStatement(actions=["ecr:GetDownloadUrlForLayer",
                                                            "ecr:BatchGetImage",
                                                            "ecr:BatchCheckLayerAvailability",
                                                            "ecr:PutImage",
                                                            "ecr:InitiateLayerUpload",
                                                            "ecr:UploadLayerPart",
                                                            "ecr:CompleteLayerUpload"],
                                                   resources=[docker_repo.repository_arn])
        build_project.add_to_role_policy(docker_repo_push)

        docker_login = aws_iam.PolicyStatement(actions=["ecr:GetAuthorizationToken"], resources=["*"])
        build_project.add_to_role_policy(docker_login)

        self.pipeline.add_stage(
            stage_name="Build",
            actions=[build_action]
        )

        # Add decrypt access so that artifacts can be read
        self.pipeline.artifact_bucket.encryption_key.add_to_resource_policy(
            PolicyStatement(principals=[AccountPrincipal(Aws.ACCOUNT_ID)],
                            actions=["kms:Decrypt"]
                            , resources=["*"]
                            ))

        core.CfnOutput(self, "DockerRepoOutput", value=docker_repo.repository_arn,
                       description="The name of the docker repo created")
