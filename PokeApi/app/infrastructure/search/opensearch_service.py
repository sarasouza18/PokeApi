# app/infrastructure/search/opensearch_service.py
from opensearchpy import OpenSearch
import os

class OpenSearchService:
    def __init__(self):
        self.client = OpenSearch(
            hosts=[{"host": os.getenv("OPENSEARCH_HOST"), "port": int(os.getenv("OPENSEARCH_PORT", 9200))}],
            http_auth=(os.getenv("OPENSEARCH_USER"), os.getenv("OPENSEARCH_PASS")),
            use_ssl=False,
            verify_certs=False
        )
        self.index_name = "posts"

        if not self.client.indices.exists(index=self.index_name):
            self.client.indices.create(index=self.index_name)

    def index_post(self, post_id: str, body: dict):
        self.client.index(index=self.index_name, id=post_id, body=body)
