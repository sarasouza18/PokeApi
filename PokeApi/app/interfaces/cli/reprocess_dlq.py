import boto3
import json
import time

sqs = boto3.client("sqs", region_name="us-east-1")
DLQ_URL = "https://sqs.us-east-1.amazonaws.com/YOUR_ACCOUNT_ID/poke-dlq"  # substitua

def process_message(body):
    print(f"Reprocessing: {body}")

def run():
    while True:
        response = sqs.receive_message(
            QueueUrl=DLQ_URL,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=10
        )

        messages = response.get("Messages", [])
        if not messages:
            print("DLQ empty, waiting...")
            time.sleep(30)
            continue

        for msg in messages:
            body = json.loads(msg["Body"])
            process_message(body)
            sqs.delete_message(QueueUrl=DLQ_URL, ReceiptHandle=msg["ReceiptHandle"])
