# message-listener

This module can be used for listening to the messages from aws sqs.

### Requirements

1. install module `pip install py-message-listener`

Follow bellow steps for using this module

1. Add `@Listener` decorator to method or function where do you want to receive the message, for that method/function
   add single parameter, This parameter is set whenever the message is received and method will be called and message
   will be passed as argument.
2. In decorator pass queue name in `destination`   argument
3. set these environment variables: `AWS_REGION`, `AWS_ACCOUNT_ID`, `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`
4. Added kwargs for configuring listener `visibility_timeout`, `wait_time_seconds` and  `max_number_of_messages`
5. `poll_after_seconds` this argument specify how much time to wait before requesting for the messages
6. `delete_on_exception` this argument specifies , whether to delete the message if any exception occurs while
   processing the message
7. To delete the message return `True` from the message processing method
> `AWS_ACCOUNT_ID` this will be used for generating the queue url

#### Sample Code

```python
from listener import Listener


@Listener(destination='test.fifo')
def fun(msg: str):
    print(msg)
    return True
```
