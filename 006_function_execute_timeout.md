## 如何给一个函数执行加上timeout，指定时间内运行不完，就抛出异常

1. 使用第三方库 ```timeout-decorator``` 提供基于 signal 和 进程超时的解决方法

```bash
pip install timeout-decorator
```

实例代码:

```Python

import time
import timeout_decorator


@timeout_decorator.timeout(5)
def mytest():
    print("Start")
    for i in range(1, 10):
        time.sleep(1)
        print("%d seconds have passed" % i)

if __name__ == '__main__':
    mytest()

```

2. 使用信号 不通用 不是线程安全的

```Python
import signal
from contextlib import contextmanager
from time import sleep


class TimeoutException(Exception):
    pass


@contextmanager
def time_limit(seconds):

    def signal_handler(signum, frame):
        raise TimeoutException("Timed out!")

    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)

    try:
        yield
    finally:
        signal.alarm(0)


def long_function_call():
    sleep(5)

try:
    with time_limit(3):
        long_function_call()
except TimeoutException as e:
    print("Timed out!")

```

关于信号是否线程安全：

```
Signals generated for a process are delivered to only one thread.
Thus, if more than one thread is eligible to receive a signal, one has to be chosen.
The choice of threads is left entirely up to the implementation both to allow the widest possible
range of conforming implementations and to give implementations the freedom to deliver the signal to the
"easiest possible" thread should there be differences in ease of delivery between different threads.
```

3. 使用线程 `Timer` 实现, 使用Timer指定时间后执行一段代码

这个实现，也不适用于多线程程序，会终止掉主线程

```
from contextlib import contextmanager
import threading
import _thread

class TimeoutException(Exception):
    def __init__(self, msg=''):
        self.msg = msg

@contextmanager
def time_limit(seconds, msg=''):
    timer = threading.Timer(seconds, lambda: _thread.interrupt_main())
    timer.start()
    try:
        yield
    except KeyboardInterrupt:
        raise TimeoutException("Timed out for operation {}".format(msg))
    finally:
        # if the action ends in specified time, timer is canceled
        timer.cancel()

import time
# ends after 5 seconds
with time_limit(5, 'sleep'):
    for i in range(10):
        time.sleep(1)
```

使用线程的实现：

```

```


4. celery 中可以使用  soft_time_limit 参数定义任务超时时间

参考：

https://stackoverflow.com/questions/492519/timeout-on-a-function-call

https://unix.stackexchange.com/questions/225687/what-happens-to-a-multithreaded-linux-process-if-it-gets-a-signal

https://stackoverflow.com/questions/366682/how-to-limit-execution-time-of-a-function-call-in-python
