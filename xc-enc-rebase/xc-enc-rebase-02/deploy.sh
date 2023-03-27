#!/bin/bash

LAMBDA_FUNCTION_NAME="excamera-xc-enc-rebase-02"
LAMBDA_HANDLER="excamera-xc-enc-rebase-02.lambda_handler"
LAMBDA_ROLE="arn:aws:iam::785126971007:role/serverless_role"
LAMBDA_RUNTIME="python3.9"
LAMBDA_MEMORY_SIZE=1024
LAMBDA_TIMEOUT=180
ZIP_FILE="/home/handsonhuang/excamera_step_function/xc-enc-rebase/xc-enc-rebase-02/excamera-xc-enc-rebase-02.zip"
LAMBDA_DESCRIPTION="excamera-xc-enc-rebase-00000002"

# delete the zip file if it already exists
if [ -f $ZIP_FILE ]; then
    rm $ZIP_FILE
    echo "Deleted $ZIP_FILE"
fi

# Create the zip file
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
    # --ephemeral-storage '{"Size": 10240}' 