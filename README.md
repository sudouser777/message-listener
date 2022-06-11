# message-listener
This module can be used for listening to the messages from aws sqs.

Follow bellow steps for using this module
1. Add `@Listener` decorator to method or function where do you want to recieve the message, for that method/function add single parameter, This parameter is set whenever the message is recieved and  method will be called and message will be passed as argument.
2. In decorator pass `destination` value as queue name 
```python
@Listener(destination='event_queue.fifo')
def fun(msg: str):
    print(msg)
```
