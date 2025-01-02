#!/bin/bash

aws lambda add-permission --function-name <function-name> --statement-id "AllowEventBridgeInvoke" --action "lambda:InvokeFunction" --principal events.amazonaws.com --source-arn arn:aws:events:<region>:<account-id>:rule/*