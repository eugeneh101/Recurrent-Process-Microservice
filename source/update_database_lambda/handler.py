import json
import os
import random
from datetime import datetime

# from dotenv import load_dotenv
import boto3
from aws_lambda_powertools.utilities.typing import LambdaContext

# load_dotenv()
dynamodb_table = boto3.resource("dynamodb").Table(os.environ["DYNAMODB_TABLE"])
ssm = boto3.client("secretsmanager")
SECRET = json.loads(ssm.get_secret_value(SecretId=os.environ["SECRET_NAME"])["SecretString"])

def lambda_handler(event, context):
    datetime_utc = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S%z")
    random_int = random.randint(0, 1000)
    print(f"At {datetime_utc}, random integer: {random_int}; secret: {SECRET}")  # irl, wouldn't print secret
    dynamodb_table.put_item(Item={"datetime_utc": datetime_utc, "random_int": random_int})
    return

    # figure out how to get pyproject.toml -> requirements.txt -> Lambda Layer or Make install
    ### figure out how to make a Lambda Layer