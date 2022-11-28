create_lambda_layer:
	rm -rf __aws_lambda_powertools_layer__
	pip install aws-lambda-powertools -t __aws_lambda_powertools_layer__/python   # machine that `cdk deploy` must have same Python version as deployed Lambdas, ie Python 3.9
	rm -rf __aws_lambda_powertools_layer__/python/*.dist-info
