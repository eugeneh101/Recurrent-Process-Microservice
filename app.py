#!/usr/bin/env python3

import aws_cdk as cdk

from cdk_infrastructure import OracleStack


app = cdk.App()
stack = OracleStack(app, "OracleStack")
app.synth()
