#!/bin/bash

aws lambda add-permission --function-name <function-name> --statement-id "AllowEventBridgeInvoke" --action "lambda:InvokeFunction" --principal events.amazonaws.com --source-arn arn:aws:events:<region>:<account-id>:rule/*

aws-encryption-cli --encrypt --input secret1.txt --wrapping-keys key=$keyArn --metadata-output ~/metadata --encryption-context purpose=test --commitment-policy require-encrypt-require-decrypt --output ~/output/.

aws-encryption-cli --decrypt --input secret1.txt.encrypted --wrapping-keys key=$keyArn --commitment-policy require-encrypt-require-decrypt --encryption-context purpose=test --metadata-output ~/metadata --max-encrypted-data-keys 1 --buffer --output .