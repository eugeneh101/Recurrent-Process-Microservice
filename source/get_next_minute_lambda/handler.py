from datetime import datetime, timedelta

from aws_lambda_powertools.utilities.typing import LambdaContext


def lambda_handler(event: None, context: LambdaContext) -> str:
    now = datetime.utcnow()
    delta = timedelta(minutes=1)
    next_minute = (now + delta).replace(second=0, microsecond=0)
    # wait_seconds = (next_minute - now).total_seconds()
    return next_minute.strftime("%Y-%m-%dT%H:%M:%SZ")
