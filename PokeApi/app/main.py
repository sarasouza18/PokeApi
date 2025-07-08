import logging
import os
import time
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import redis

from app.presentation.controllers.social_media_controller import SocialMediaController
from app.infrastructure.persistence.dynamodb_post_repository import DynamoDBPostRepository
from app.infrastructure.persistence.dynamodb_comment_repository import DynamoDBCommentRepository
from app.infrastructure.external.pokeapi_service import PokeAPIService
from app.infrastructure.external.processing_service import ProcessingService
from app.infrastructure.external.dead_letter_queue import DeadLetterQueue
from app.infrastructure.external.circuit_breaker import CircuitBreaker
from app.presentation.error_handling.error_handler import ErrorHandler

# Initialize logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ServiceInitializationError(Exception):
    """Custom exception for service initialization failures"""
    pass


def load_configuration() -> None:
    """Load and validate environment configuration"""
    try:
        load_dotenv()
        required_vars = [
            'REDIS_HOST', 'REDIS_PORT',
            'DYNAMODB_ENDPOINT',
            'DLQ_QUEUE_URL'
        ]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {missing_vars}")
        logger.info("Configuration loaded successfully")
    except Exception as e:
        logger.error("Configuration loading failed: %s", str(e))
        raise


def initialize_redis_connection() -> redis.Redis:
    """Initialize Redis connection with retry logic"""
    max_retries = 3
    retry_delay = 2

    for attempt in range(max_retries):
        try:
            redis_conn = redis.Redis(
                host=os.getenv('REDIS_HOST', 'redis'),
                port=int(os.getenv('REDIS_PORT', '6379')),
                db=int(os.getenv('REDIS_DB', '0')),
                socket_timeout=5,
                socket_connect_timeout=5,
                decode_responses=True,
                health_check_interval=30
            )
            if not redis_conn.ping():
                raise redis.ConnectionError("Redis ping failed")
            logger.info("Redis connection established")
            return redis_conn
        except (redis.ConnectionError, redis.TimeoutError) as e:
            if attempt == max_retries - 1:
                logger.error("Failed to connect to Redis after %s attempts", max_retries)
                raise ServiceInitializationError("Redis connection failed") from e
            logger.warning("Redis connection attempt %s failed, retrying in %s seconds...",
                           attempt + 1, retry_delay)
            time.sleep(retry_delay)


def initialize_services() -> tuple[SocialMediaController, ErrorHandler]:
    """Initialize all application services"""
    try:
        logger.info("Starting service initialization...")

        # Redis & Circuit Breaker
        redis_conn = initialize_redis_connection()
        circuit_breaker = CircuitBreaker(
            redis_client=redis_conn,
            failure_threshold=int(os.getenv("CIRCUIT_BREAKER_THRESHOLD", "5")),
            reset_timeout=int(os.getenv("CIRCUIT_BREAKER_RESET_TIMEOUT", "60"))
        )

        # DynamoDB endpoint config (for LocalStack or custom)
        endpoint_url = os.getenv('DYNAMODB_ENDPOINT', 'http://dynamodb:8000')

        # DLQ
        dlq = DeadLetterQueue(
            queue_url=os.getenv("DLQ_QUEUE_URL"),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )

        # Repositories
        post_repository = DynamoDBPostRepository(
            table_name=os.getenv("DYNAMODB_TABLE_POSTS", "Posts"),
            endpoint_url=endpoint_url
        )
        comment_repository = DynamoDBCommentRepository(
            table_name=os.getenv("DYNAMODB_TABLE_COMMENTS", "Comments"),
            endpoint_url=endpoint_url
        )

        # Services
        pokeapi_service = PokeAPIService(circuit_breaker=circuit_breaker)
        processing_service = ProcessingService(
            dlq=dlq,
            endpoint=os.getenv("PROCESSING_ENDPOINT", "http://httpbin.org/post")
        )

        # Controller
        controller = SocialMediaController(
            post_repository=post_repository,
            comment_repository=comment_repository,
            pokeapi_service=pokeapi_service,
            processing_service=processing_service
        )

        logger.info("All services initialized successfully")
        return controller, ErrorHandler()

    except Exception as e:
        logger.critical("Service initialization failed: %s", str(e), exc_info=True)
        raise ServiceInitializationError("Service initialization failed") from e


def execute_pipeline(controller: SocialMediaController) -> Dict[str, Any]:
    """Execute the main application pipeline"""
    try:
        logger.info("Starting data pipeline execution")
        result = controller.execute_pipeline()
        logger.info("Pipeline execution completed successfully")
        return {
            'status': 'success',
            'data': result,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        logger.error("Pipeline execution failed: %s", str(e), exc_info=True)
        return {
            'status': 'error',
            'error': str(e),
            'type': type(e).__name__,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }


def main() -> int:
    """Application entry point"""
    try:
        load_configuration()
        controller, error_handler = initialize_services()

        @error_handler.wrap_endpoint
        def _execute_pipeline():
            return execute_pipeline(controller)

        result = _execute_pipeline()

        if result['status'] == 'success':
            logger.info("Application completed successfully")
            return 0
        else:
            logger.error("Application completed with errors")
            return 1

    except Exception as e:
        logger.critical("Application failed catastrophically: %s", str(e), exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
