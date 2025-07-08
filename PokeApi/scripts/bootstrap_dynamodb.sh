#!/bin/bash

set -e

ENDPOINT_URL=${DYNAMODB_ENDPOINT:-http://localhost:4566}
REGION=us-east-1

echo "🔧 Creating 'Posts' table..."
aws dynamodb create-table \
  --table-name Posts \
  --attribute-definitions AttributeName=id,AttributeType=S \
  --key-schema AttributeName=id,KeyType=HASH \
  --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
  --region $REGION \
  --endpoint-url $ENDPOINT_URL || echo "⚠️ 'Posts' table already exists or failed to create"

echo "🔧 Creating 'Comments' table with GSI 'post_id-index'..."
aws dynamodb create-table \
  --table-name Comments \
  --attribute-definitions \
    AttributeName=id,AttributeType=S \
    AttributeName=post_id,AttributeType=S \
  --key-schema AttributeName=id,KeyType=HASH \
  --global-secondary-indexes '[
    {
      "IndexName": "post_id-index",
      "KeySchema": [{"AttributeName":"post_id","KeyType":"HASH"}],
      "Projection": {"ProjectionType":"ALL"},
      "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5}
    }
  ]' \
  --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
  --region $REGION \
  --endpoint-url $ENDPOINT_URL || echo "⚠️ 'Comments' table already exists or failed to create"

echo "✅ DynamoDB tables ready!"
