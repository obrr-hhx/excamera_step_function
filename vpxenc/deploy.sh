#!/bin/bash

LAMBDA_FUNCTION_NAME="excamera-vpxenc"
LAMBDA_HANDLER="excamera-vpxenc.lambda_handler"
LAMBDA_ROLE="arn:aws:iam::785126971007:role/serverless_role"
LAMBDA_RUNTIME="python3.9"
LAMBDA_MEMORY_SIZE=1024
LAMBDA_TIMEOUT=180
ZIP_FILE="/home/handsonhuang/excamera_step_function/vpxenc/excamera-vpxenc.zip"
LAMBDA_DESCRIPTION="excamera-vpxenc"

# ir the zip file already exists, delete it first
if [ -f $ZIP_FILE ]; then
    rm $ZIP_FILE
    echo "Deleted $ZIP_FILE"
fi
# Create the zip file using the python script
python3 makeZip.py

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