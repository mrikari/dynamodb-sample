import json
from typing import Optional
from uuid import uuid4

import boto3
from aws_lambda_powertools.utilities.parser import BaseModel
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer

serializer = TypeSerializer()
deserializer = TypeDeserializer()

db_client = boto3.client(
    "dynamodb",
    endpoint_url="http://localhost:8000",
    region_name="ap-northeast-1",
)

# UTILITIES


def getHttpResponse(status_code: int = 200, body: BaseModel = None):
    if status_code == 400:
        return {"statusCode": 400, "body": json.dumps({"message": "Bad Request"})}
    elif status_code == 404:
        return {"statusCode": 404, "body": json.dumps({"message": "Not Found"})}

    return {
        "statusCode": 200,
        "body": body.model_dump_json() if body else json.dumps({"message": "OK"}),
    }


def deserializeItem(item: dict[str, dict[str:any]]) -> dict[str, any]:
    return {k: deserializer.deserialize(v) for k, v in item.items()}


def deserializeItems(items: list[dict[str, dict[str:any]]]) -> list[dict[str, any]]:
    return [deserializeItem(item) for item in items]


# MODELS


class Message(BaseModel):
    id: str
    message: Optional[str] = None


# REQUEST SCHEMAS


# RESPONSE SCHEMAS


class MessageListResponse(BaseModel):
    data: list[Message] = []
    next: Optional[str] = None


class MessageResponse(BaseModel):
    data: Message


# HANDLERS


## /messages
### GET
def listMessage(event, context):
    has_next = None
    if (
        "queryStringParameters" in event
        and event["queryStringParameters"]
        and "next" in event["queryStringParameters"]
    ):
        has_next = {"id": serializer.serialize(event["queryStringParameters"]["next"])}

    get_response = (
        db_client.scan(
            TableName="my-table",
            Limit=10,
            ExclusiveStartKey=has_next,
        )
        if has_next
        else db_client.scan(
            TableName="my-table",
            Limit=10,
        )
    )

    return getHttpResponse(
        body=MessageListResponse(
            data=deserializeItems(get_response["Items"]),
            next=deserializeItem(get_response["LastEvaluatedKey"])["id"]
            if "LastEvaluatedKey" in get_response
            else None,
        )
    )


### POST
def createMessage(event, context):
    print(event["body"])
    body = json.loads(event["body"])
    id = str(uuid4())

    item_dynamodb_json = {
        k: serializer.serialize(v)
        for k, v in {
            "id": id,
            "message": body["message"],
        }.items()
    }

    db_client.put_item(TableName="my-table", Item=item_dynamodb_json)
    return getHttpResponse()


## /messages/{id}
### GET
def getMessage(event: dict, context):
    path_params = event.get("pathParameters")

    if not path_params or "id" not in path_params:
        return getHttpResponse(400)

    id = path_params["id"]
    item_dynamodb_json = {k: serializer.serialize(v) for k, v in {"id": id}.items()}
    get_response = db_client.get_item(
        TableName="my-table",
        Key=item_dynamodb_json,
    )

    if "Item" not in get_response:
        return getHttpResponse(404)

    return getHttpResponse(
        body=MessageResponse(data=deserializeItem(get_response["Item"]))
    )


## /messages/{id}
### DELETE
def deleteMessage(event, context):
    path_params = event.get("pathParameters")

    if not path_params or "id" not in path_params:
        return getHttpResponse(400)

    id = path_params["id"]
    item_dynamodb_json = {k: serializer.serialize(v) for k, v in {"id": id}.items()}
    get_response = db_client.get_item(
        TableName="my-table",
        Key=item_dynamodb_json,
    )

    if "Item" not in get_response:
        return getHttpResponse(404)

    db_client.delete_item(
        TableName="my-table",
        Key=item_dynamodb_json,
    )

    return getHttpResponse()
