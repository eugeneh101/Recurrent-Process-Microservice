#!/usr/bin/env python3

import aws_cdk as cdk

from cdk_infrastructure import OracleStack


app = cdk.App()
environment = app.node.try_get_context("environment")
stack = OracleStack(
    app,
    "OracleStack",
    env=cdk.Environment(region=environment["AWS_REGION"]),
    environment=environment,
)
app.synth()
