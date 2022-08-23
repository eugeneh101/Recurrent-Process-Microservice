from constructs import Construct
from aws_cdk import (
    # BundlingOptions,
    Duration,
    RemovalPolicy,
    SecretValue,
    Size,
    Stack,
    aws_dynamodb as dynamodb,
    aws_events as events,
    aws_events_targets as events_targets,
    aws_lambda as _lambda,
    aws_secretsmanager as secretsmanager,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as sfn_tasks,
)


class OracleStack(Stack):  # later move code into constructs.py
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Secrets Manager
        self.secret = secretsmanager.Secret(
            self,
            "MyFavoriteSecret",
            # in real life, you would not put the secret in plaintext in CDK
            secret_object_value={"my_secret": SecretValue.unsafe_plain_text("SUPER_SECRET_VALUE")},
        )

        # DynamoDB table
        self.dynamodb_table = dynamodb.Table(self, "RandomIntegers",
            partition_key=dynamodb.Attribute(name="datetime_utc", type=dynamodb.AttributeType.STRING),
            # CDK wil not automatically deleted DynamoDB during `cdk destroy`
            # (as DynamoDB is a stateful resource) unless explicitly specified by the following line
            removal_policy=RemovalPolicy.DESTROY,
        )

        # Lambdas
        self.get_next_minute_lambda = _lambda.Function(
            self,
            "NextMinuteLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset(
                path="source/get_next_minute_lambda",
                exclude=[".venv/*"],  # exclude virtualenv
            ),
            handler="handler.lambda_handler",
            timeout=Duration.seconds(1),  # should be effectively instantenous
            memory_size=128,  # in MB
            ephemeral_storage_size=Size.mebibytes(512),
        )
        self.update_db_lambda = _lambda.Function(
            self,
            "UpdateDatabaseLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset(
                path="source/update_database_lambda",
                exclude=[".venv/*"],  # exclude virtualenv
                ### couldn't figure out how to get this working
                # bundling=BundlingOptions(
                #     image=_lambda.Runtime.PYTHON_3_9.bundling_image,  # use the same Python version number
                #     command=[  # install requirements.txt
                #         "bash", "-c",
                #         "ls"
                #         #"pip install --no-cache -r requirements.txt -t /asset-output && cp -au . /asset-output"
                #     ],
                # ),
            ),
            handler="handler.lambda_handler",
            timeout=Duration.seconds(3),
            memory_size=128,  # in MB
            ephemeral_storage_size=Size.mebibytes(512),
        )

        # build Step Function definition
        get_next_minute = sfn_tasks.LambdaInvoke(
            self,
            "get_next_minute",
            lambda_function=self.get_next_minute_lambda,
            payload=sfn.TaskInput.from_text("null"),
            payload_response_only=True,  # don't want Lambda invocation metadata
        )
        sleep_to_next_minute = sfn.Wait(self, "sleep_to_next_minute", time=sfn.WaitTime.timestamp_path("$"))
        initialize_sleeps = sfn.Pass(self, "initialize_sleeps", result=sfn.Result.from_array([2] * 30))  ### hard coded
        for_loop = sfn.Map(self, id="for loop", items_path="$", max_concurrency=1)

        sleep_seconds = sfn.Wait(self, "sleep_seconds", time=sfn.WaitTime.seconds_path("$"))
        update_database = sfn_tasks.LambdaInvoke(
            self,
            "update_database",
            lambda_function=self.update_db_lambda,
            payload=sfn.TaskInput.from_text("null"),
            invocation_type=sfn_tasks.LambdaInvocationType.EVENT,
        )
        map_state_tasks = sfn.Chain.start(sleep_seconds).next(update_database)
        for_loop.iterator(map_state_tasks)
        sfn_definition = get_next_minute.next(sleep_to_next_minute).next(initialize_sleeps).next(for_loop)
        self.state_machine = sfn.StateMachine(self, "RecurrentInvocations", definition=sfn_definition)

        # Eventbridge scheduled rule: needs Step Function
        self.eventbridge_minute_scheduled_event = events.Rule(
            self,
            "run_every_minute",
            event_bus=None,  # "default" bus
            schedule=events.Schedule.rate(Duration.minutes(1)),
        )

        # dependencies: lambda layer, environment variable, permissions, Eventbridge rule target
        powertools_layer = _lambda.LayerVersion.from_layer_version_arn(
            self,
            "aws_lambda_powertools",
            layer_version_arn="arn:aws:lambda:us-east-1:017000801446:layer:AWSLambdaPowertoolsPython:29",  # might consider getting latest layer
        )
        self.get_next_minute_lambda.add_layers(powertools_layer)
        self.update_db_lambda.add_layers(powertools_layer)
        self.update_db_lambda.add_environment(key="SECRET_NAME", value=self.secret.secret_name)
        self.update_db_lambda.add_environment(key="DYNAMODB_TABLE", value=self.dynamodb_table.table_name)
        self.dynamodb_table.grant_read_write_data(self.update_db_lambda)
        self.secret.grant_read(self.update_db_lambda.role)
        self.eventbridge_minute_scheduled_event.add_target(
            target=events_targets.SfnStateMachine(
                machine=self.state_machine,
                input=None,
                # dead_letter_queue=dlq,  # might consider for high availability
            )
        )



