<!-- 简述Python GIL -->

## 简述Python GIL

```
In CPython, the global interpreter lock, or GIL, is a mutex that protects access to Python objects, preventing multiple threads from executing Python bytecodes at once. This lock is necessary mainly because CPython's memory management is not thread-safe. (However, since the GIL exists, other features have grown to depend on the guarantees that it enforces.)
```

在CPython中，GIL在多个线程同时执行时，只有一个线程可以访问Python对象。之所以需要GIL，是因为CPython的内存管理不是线程安全的。

关于CPython内存管理，使用的是引用计数：

```Python
>>> import sys
>>> a = []
>>> b = a
>>> sys.getrefcount(a)
3
```

这里 变量 a 有三个计数, a, b, sys.getrefcount 方法的参数。

```
The problem was that this reference count variable needed protection from race conditions where two threads increase or decrease its value simultaneously. If this happens, it can cause either leaked memory that is never released or, even worse, incorrectly release the memory while a reference to that object still exists. This can can cause crashes or other "weird" bugs in your Python programs.

This reference count variable can be kept safe by adding locks to all data structures that are shared across threads so that they are not modified inconsistently.

But adding a lock to each object or groups of objects means multiple locks will exist which can cause another problem—Deadlocks (deadlocks can only happen if there is more than one lock). Another side effect would be decreased performance caused by the repeated acquisition and release of locks.

The GIL is a single lock on the interpreter itself which adds a rule that execution of any Python bytecode requires acquiring the interpreter lock. This prevents deadlocks (as there is only one lock) and doesn’t introduce much performance overhead. But it effectively makes any CPU-bound Python program single-threaded.


```

基于引用计数的变量在两个线程同时修改值的时候需要被保护起来。引用计数的变量可以通过加锁来保证数据安全。
但是给每个对象加锁又会造成死锁问题，同时引发性能问题。
GIL是一个单独的锁，它防止了死锁并且不会有太多性能消耗。但是会把CPU密集型的Python程序变成单线程的。

单个线程的CPU密集型实例：

```Python
# single_threaded.py
import time
from threading import Thread

COUNT = 50000000

def countdown(n):
    while n>0:
        n -= 1

start = time.time()
countdown(COUNT)
end = time.time()

print('Time taken in seconds -', end - start)
```

运行耗时：

```bash
Time taken in seconds - 4.367990970611572
```

使用2个线程一起计算：

```Python
# multi_threaded.py
import time
from threading import Thread

COUNT = 50000000

def countdown(n):
    while n>0:
        n -= 1

t1 = Thread(target=countdown, args=(COUNT//2,))
t2 = Thread(target=countdown, args=(COUNT//2,))

start = time.time()
t1.start()
t2.start()
t1.join()
t2.join()
end = time.time()

print('Time taken in seconds -', end - start)
```

运行耗时：

```bash
Time taken in seconds - 5.078229188919067
```

可以看出CPU密集型的代码不适合CPython多线程模式。

对于CPU密集型的代码可以使用多进程，充分利用CPU资源：

```
from multiprocessing import Pool
import time

COUNT = 50000000
def countdown(n):
    while n>0:
        n -= 1

if __name__ == '__main__':
    pool = Pool(processes=2)
    start = time.time()
    r1 = pool.apply_async(countdown, [COUNT//2])
    r2 = pool.apply_async(countdown, [COUNT//2])
    pool.close()
    pool.join()
    end = time.time()
    print('Time taken in seconds -', end - start)
```

运行耗时：

```bash
Time taken in seconds - 2.2619078159332275
```

```
The GIL ensures that only one thread runs in the interpreter at once.
When a thread is running, it holds the GIL.
GIL released on I/O (read,write,send,recv,etc.).
```

当一个线程运行时，它得到GIL，在处理IO时，GIL被释放。

什么是 Tick? 类似时间片轮转中的时间片，表示执行Python字节码指令条数

```Python
>>> import sys; sys.getcheckinterval()
__main__:1: DeprecationWarning: sys.getcheckinterval() and sys.setcheckinterval() are deprecated.  Use sys.getswitchinterval() instead.
100
>>> sys.getswitchinterval()
0.005
>>>
```

Python/ceval.c中的代码：

```C
        if (--_Py_Ticker < 0) {
            if (*next_instr == SETUP_FINALLY) {
                /* Make the last opcode before
                   a try: finally: block uninterruptible. */
                goto fast_next_opcode;
            }
            _Py_Ticker = _Py_CheckInterval;
            tstate->tick_counter++;
#ifdef WITH_TSC
            ticked = 1;
#endif
            if (pendingcalls_to_do) {
                if (Py_MakePendingCalls() < 0) {
                    why = WHY_EXCEPTION;
                    goto on_error;
                }
                if (pendingcalls_to_do)
                    /* MakePendingCalls() didn't succeed.
                       Force early re-execution of this
                       "periodic" code, possibly after
                       a thread switch */
                    _Py_Ticker = 0;
            }
#ifdef WITH_THREAD
            if (interpreter_lock) {
                /* Give another thread a chance */

                if (PyThreadState_Swap(NULL) != tstate)
                    Py_FatalError("ceval: tstate mix-up");
                PyThread_release_lock(interpreter_lock);

                /* Other threads may run now */

                PyThread_acquire_lock(interpreter_lock, 1);
```


```
The operating system has a priority queue of threads/processes ready to run.
```

操作系统有一个线程/进程待运行的优先队列。（进程和线程的运行，阻塞都是系统控制的）


`CPU-bound threads make GIL acquisition difficult for threads that want to handle events.`

CPU密集型的线程，在获取GIL时候很困难，所以运行效率低。

```
There must be some way to separate CPU-bound (low priority) and I/O bound (high priority) threads.
```

分离计算密集型和IO密集型的线程。

参考：

https://wiki.python.org/moin/GlobalInterpreterLock

https://realpython.com/python-gil/

http://dabeaz.com/python/UnderstandingGIL.pdf

https://docs.python.org/3/c-api/init.html#thread-state-and-the-global-interpreter-lock

https://callhub.io/understanding-python-gil/

https://blog.csdn.net/weixin_41594007/article/details/79485847

http://dabeaz.blogspot.com/2010/01/python-gil-visualized.html
