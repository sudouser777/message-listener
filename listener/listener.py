import logging
import os
import time
import uuid
from logging import NullHandler
from threading import Thread
from typing import List

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
        self.visibility_timeout = kwargs.get('visibility_timeout')
        self.wait_time_seconds = kwargs.get('wait_time_seconds')
        self.max_number_of_messages = kwargs.get('max_number_of_messages', 1)
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
            kwargs = {'MaxNumberOfMessages': self.max_number_of_messages}
            if self.visibility_timeout:
                kwargs['VisibilityTimeout'] = self.visibility_timeout
            if self.wait_time_seconds:
                kwargs['WaitTimeSeconds'] = self.wait_time_seconds

            response = self.client.receive_message(QueueUrl=self.destination, **kwargs)
            self.process_message(response, handler)
            logger.debug(f'Waiting for {self.poll_after_seconds} seconds')
            time.sleep(self.poll_after_seconds)

    def process_message(self, response: dict, handler: callable):
        logger.debug(response)
        if 'Messages' in response:
            messages = [msg['Body'] for msg in response['Messages']]
            recept_handles = [msg['ReceiptHandle'] for msg in response['Messages']]
            try:
                if handler(messages[0] if len(messages) == 1 else messages):
                    self.delete_message(recept_handles)
            except Exception as e:
                if self.delete_on_exception:
                    self.delete_message(recept_handles)
                logger.error('Error occurred while processing the message/s', exc_info=e)

    def delete_message(self, recept_handles: List) -> None:
        try:
            if len(recept_handles) == 1:
                response = self.client.delete_message(QueueUrl=self.destination, ReceiptHandle=recept_handles[0])
            else:
                entries = [{'Id': str(uuid.uuid4()), 'ReceiptHandle': handle} for handle in recept_handles]
                response = self.client.delete_message_batch(QueueUrl=self.destination, Entries=entries)
            logger.debug(response)
            logger.info('Successfully deleted the message/s')
        except ClientError as e:
            if e.response['Error']['Code'] == 'ReceiptHandleIsInvalid':
                logger.error(f'Message receipt handle is expired: {e.response["Error"]["Message"]}')
            else:
                logger.error(f'Error occurred while deleting the message/s: {e.response["Error"]["Message"]}')
