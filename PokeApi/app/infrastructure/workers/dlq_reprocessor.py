# app/infrastructure/workers/dlq_reprocessor.py

import boto3
import json
import time
import logging
from app.infrastructure.persistence.dynamodb_post_repository import DynamoDBPostRepository
from app.infrastructure.search.opensearch_service import OpenSearchService
from app.infrastructure.external.processing_service import ProcessingService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sqs = boto3.client("sqs", endpoint_url="http://localstack:4566", region_name="us-east-1")
DLQ_URL = "http://localstack:4566/000000000000/dead-letter-queue"
RETRY_DELAY = 20  # seconds

# Services
post_repo = DynamoDBPostRepository()
opensearch = OpenSearchService()
processor = ProcessingService()

def process_message(item_type: str, payload: dict) -> bool:
    item_id = payload.get("id", "unknown")

    logger.info(f"🔁 Reprocessing {item_type} {item_id}")

    try:
        if item_type == "post":
            result = processor.process_post(payload)
            if result:
                opensearch.index_post(item_id, payload)
                logger.info(f"✅ Post {item_id} reprocessed and reindexed")
                return True

        elif item_type == "comment":
            result = processor.process_comment(payload)
            if result:
                logger.info(f"✅ Comment {item_id} reprocessed successfully")
                return True

        logger.warning(f"❌ Failed to reprocess {item_type} {item_id}")
        return False

    except Exception as e:
        logger.error(f"🔥 Error reprocessing {item_type} {item_id}: {str(e)}")
        return False

def run():
    logger.info("🚀 DLQ worker started")

    while True:
        response = sqs.receive_message(
            QueueUrl=DLQ_URL,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=10
        )

        messages = response.get("Messages", [])
        if not messages:
            logger.info("⏳ DLQ is empty. Waiting before retrying...")
            time.sleep(RETRY_DELAY)
            continue

        for msg in messages:
            try:
                body = json.loads(msg["Body"])
                item_type = body.get("type")  # 'post' or 'comment'
                payload = body.get("payload")

                if not item_type or not payload:
                    logger.warning("⚠️ DLQ message missing 'type' or 'payload'. Skipping.")
                    continue

                if process_message(item_type, payload):
                    sqs.delete_message(QueueUrl=DLQ_URL, ReceiptHandle=msg["ReceiptHandle"])
                    logger.info(f"🗑️ DLQ message for {item_type} {payload.get('id')} deleted")

            except Exception as e:
                logger.error(f"❌ Error handling DLQ message: {str(e)}")
