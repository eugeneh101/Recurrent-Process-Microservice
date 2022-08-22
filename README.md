# Deploy this Microservice
Deploying on AWS Cloudshell is easiest because it already has a sufficiently updated version of AWS CLI, node (at least v16), CDK Toolkit (at least v2) already installed.
* `git clone THIS_REPO`
* `cd Recurrent-Process-Microservice`
* `python3 -m venv .venv`  # create virtualenv
* `source .venv/bin/activate`  # activate virtualenv
* `pip install -r requirements.txt`  # install Python CDK
* `cdk bootstrap`  # 1-time step up for AWS account
* `cdk deploy`  # deploy this microservice


If you want to run this on your laptop, then you can install AWS CLI, node.js, and CDK Toolkit by following the instructions here: https://cdkworkshop.com/15-prerequisites.html
* To see the version of node, run `node --version`
* To see the version of CDK toolkit, run `cdk --version`


# TODO
* add unit tests if requested