#!/bin/bash

current_path=$(dirname $(readlink -f $0))

LAMBDA_FUNCTION_NAME="excamera-xc-enc"
LAMBDA_HANDLER="excamera-xc-enc.lambda_handler"
LAMBDA_ROLE=$AWS_ROLE
LAMBDA_RUNTIME="python3.9"
LAMBDA_MEMORY_SIZE=1024
LAMBDA_TIMEOUT=180
ZIP_FILE="$current_path/excamera-xc-enc.zip"
LAMBDA_DESCRIPTION="excamera-xc-enc-reencode-first-frame-00000001"

# delete the zip file if it already exists
if [ -f $ZIP_FILE ]; then
    rm $ZIP_FILE
    echo "Deleted $ZIP_FILE"
fi

# Create the zip file
python3 $current_path/makeZip.py

# if the lambda function already exists, delete it first
if aws lambda get-function --function-name $LAMBDA_FUNCTION_NAME; then
    aws lambda delete-function --function-name $LAMBDA_FUNCTION_NAME
fi

# Create the lambda function

aws lambda create-function \
    --function-name $LAMBDA_FUNCTION_NAME \
    --handler $LAMBDA_HANDLER \
    --runtime $LAMBDA_RUNTIME \
    --role $LAMBDA_ROLE \
    --zip-file fileb://$ZIP_FILE \
    --memory-size $LAMBDA_MEMORY_SIZE \
    --timeout $LAMBDA_TIMEOUT \
    --description $LAMBDA_DESCRIPTION