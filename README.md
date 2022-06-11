# message-listener
This module can be used for listening to the messages from aws sqs.

### Requirements
1. install `boto3` module `pip install boto3`

Follow bellow steps for using this module
1. Add `@Listener` decorator to method or function where do you want to recieve the message, for that method/function add single parameter, This parameter is set whenever the message is recieved and  method will be called and message will be passed as argument.
2. In decorator pass  queue name in `destination`   argument
3. set these environment variables: `AWS_REGION`, `AWS_ACCOUNT_ID`, `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`

>`AWS_ACCOUNT_ID` this will be used for generating the queue url

#### Sample Code
```python

@Listener(destination='test.fifo')
def fun(msg: str):
    print(msg)
```
