## 简述 Python命令行选项

Python的命令行参数，提供了很多有用的功能，可以方便调试和运行，通过 `man python` 就能查看，
以下是一些常用参数使用实例和场景:

1. -B参数，在import时候，不产生pyc或者pyo文件:
比如有a.py，内容如下:

```python
def hello():
  pass
```

main.py，会引用a.py中的hello函数:

```python
from a import hello

if __name__ == '__main__':
  print(hello)
```

使用python -B main.py就不会产生a.pyc文件

2. -c 参数，直接运行python语句，比如:

```shell
python -c "print 'Hello world'"
```

或者测试安装的包是否可以成功引用，可以使用import语句尝试:

```shell
python -c "import requests;print dir(requests)"
```

3. -i 参数，运行完python脚本文件以后打开一个python环境，方便查看运行结果，比如:

```python
from a import hello

a = 1

if __name__ == '__main__':
  print hello
```

使用-i参数:

```bash
python -i main.py
<function hello at 0x101409c08>
>>> a
1
```

4. -m 参数，将模块按照脚本执行，最常见的用法是:

```python
python -m SimpleHTTPServer 8081
```

在打开浏览器的8081端口，可以用于局域网的简单文件下载服务。


5. -V 参数，输出Python的版本，或者--version:

```python
python -V      
Python 2.7.10
python --version
Python 2.7.10
```

6. -O 参数，产生一个优化的pyo文件（和-B 参数一起使用无效）:

```
python -O main.py 
<function hello at 0x10abb7c08>
```

这时候会有一个a.pyo文件


7. -v 参数，会输出每一个模块引用信息，包括从何处引用的，以及何时被清除的

8. -u 参数，在print记录时候很有用，使用这个参数 会强制 stdin, stdout 和 stderr变为无缓冲的，会立刻输出出来，而不是等缓冲区满了才会打印数据。

比如如下代码:

```python
from time import sleep

for i in range(10):
  print i
  sleep(1)
```

运行时候重定向到一个文件:

```
python main.py > ok.log
```

会等到缓冲区满了，或者程序退出了才会真正写入到ok.log
这时候使用 python -u main.py > ok.log 执行，就会每次print后立刻写入文件。
