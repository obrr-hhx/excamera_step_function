#!/bin/bash

find . -name "deploy.sh" -type f -print0 | while read -d $'\0' file; 
do
    echo "Processing $file"
    chmod +x $file
    $file
done