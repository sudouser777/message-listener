import logging
import os
import time
from logging import NullHandler
from threading import Thread

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger('message.listener')
logger.addHandler(NullHandler())


class Listener:
    def __init__(self, destination: str, **kwargs):
        region = kwargs.get('region_name', os.getenv('AWS_REGION'))
        aws_account_id = kwargs.get('aws_account_id', os.getenv('AWS_ACCOUNT_ID'))
        self.destination = f'https://sqs.{region}.amazonaws.com/{aws_account_id}/{destination}'
        self.delete_on_exception = kwargs.get('delete_on_exception', False)
        self.poll_after_seconds = kwargs.get('poll_after_seconds', 1)
        self.client = boto3.client(
            'sqs', region_name=region,
            aws_access_key_id=kwargs.get('aws_access_key_id', os.getenv('AWS_ACCESS_KEY_ID')),
            aws_secret_access_key=kwargs.get('aws_secret_access_key', os.getenv('AWS_SECRET_ACCESS_KEY'))
        )

    def __call__(self, *args) -> None:
        thread = Thread(target=self.listen, args=args)
        thread.start()

    def listen(self, handler: callable) -> None:
        while True:
            logger.info('Waiting for messages:_________')
            response = self.client.receive_message(QueueUrl=self.destination)
            logger.debug(response)
            if 'Messages' in response:
                message = response['Messages'][0]
                try:
                    if handler(message['Body']):
                        self.delete_message(message['ReceiptHandle'])

                except Exception as e:
                    if self.delete_on_exception:
                        self.delete_message(message['ReceiptHandle'])
                    logger.error('Error occurred while processing the message', exc_info=e)
            logger.debug(f'Waiting for {self.poll_after_seconds} seconds')
            time.sleep(self.poll_after_seconds)

    def delete_message(self, recept_handle: str) -> None:
        try:
            response = self.client.delete_message(QueueUrl=self.destination, ReceiptHandle=recept_handle)
            logger.debug(response)
            logger.info('Successfully deleted the message')
        except ClientError as e:
            if e.response['Error']['Code'] == 'ReceiptHandleIsInvalid':
                logger.error(f'Message receipt handle is expired: {e.response["Error"]["Message"]}')
            else:
                logger.error(f'Error occurred while deleting the message: {e.response["Error"]["Message"]}')
