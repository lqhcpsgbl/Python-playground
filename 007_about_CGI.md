## 简述 CGI 编程

wiki:

```
In computing, Common Gateway Interface (CGI) offers a standard protocol for web servers to execute programs that execute like console applications (also called command-line interface programs) running on a server that generates web pages dynamically. Such programs are known as CGI scripts or simply as CGIs. The specifics of how the script is executed by the server are determined by the server. In the common case, a CGI script executes at the time a request is made and generates HTML.

In brief, an HTTP POST request from the client will send the CGI program HTML form data via standard input. Other data, such as URL paths, and HTTP header data, are presented as process environment variables.

An early use of CGI scripts was to process forms. In the beginning of HTML, HTML forms typically had an "action" attribute and a button designated as the "submit" button. When the submit button is pushed the URI specified in the "action" attribute would be sent to the server with the data from the form sent as a query string. If the "action" specifies a CGI script then the CGI script would be executed and it then produces an HTML page.

If parameters are sent to the script via an HTTP GET request (a question mark appended to the URL, followed by param=value pairs; in the example, ?and=a&query=string), then those parameters are stored in the QUERY_STRING environment variable before the script is called. If parameters are sent to the script via an HTTP POST request, they are passed to the script's standard input. The script can then read these environment variables or data from standard input and adapt to the Web browser's request.
```

通用网关接口提供了一个可执行程序和Web服务器之间的一个标准协议，用来生成动态页面的。这样的可执行程序叫做
CGI脚本或者CGI程序。通常，CGI脚本在请求到来时候执行并得到产生的HTML代码，返回给客户端。
早期，CGI脚本是用来处理表单的。
对于 GET 请求，一般是通过读取环境变量的值来获取请求参数的。
对于 POST请求通过标准输入发送给CGI程序。其他数据，比如URL，HTTP请求头等，通过环境变量传递。

CGI技术，是一种古老的技术，现在很少有使用了，不过看起来QQ邮箱还是在使用的，比如，登录QQ邮箱时看到的还是这样的URL：
https://mail.qq.com/cgi-bin/

了解一下CGI，我们可以了解一下Web的发展历史。

### CGI hello world
现在主流的服务器，比如Nginx, 已经不支持原始的CGI程序了，我们这里使用Apache这种古老的服务器，配置cgi的环境
也比较简单，这里不再赘述，直接看下简单的代码，GGI脚本或者应用可以使用任何语言开发，我们这里可以尝试多种语言，
不过，CGI应用必须要有可执行权限，也就是给脚本或者二进制代码对于的执行权限，不然会报错(500 Internal Server Error)。

看一段perl代码,hello.pl

```perl
#!/usr/bin/perl

print "Content-type: text/plain\n\n";

for my $var ( sort keys %ENV ) {
 printf "%s = \"%s\"\n", $var, $ENV{$var};
}
```

注意，需要加上可以执行权限：

```shell
chmod a+x ./hello.pl
```

测试：
```shell
# curl http://127.0.0.1/cgi-bin/hello.pl?name=hello
DOCUMENT_ROOT = "/var/www/html"
GATEWAY_INTERFACE = "CGI/1.1"
HTTP_ACCEPT = "*/*"
HTTP_HOST = "127.0.0.1"
HTTP_USER_AGENT = "curl/7.19.7 (x86_64-redhat-linux-gnu) libcurl/7.19.7 NSS/3.15.3 zlib/1.2.3 libidn/1.18 libssh2/1.4.2"
PATH = "/sbin:/usr/sbin:/bin:/usr/bin"
QUERY_STRING = "name=hello"
REMOTE_ADDR = "127.0.0.1"
REMOTE_PORT = "57912"
REQUEST_METHOD = "GET"
REQUEST_URI = "/cgi-bin/hello.pl?name=hello"
SCRIPT_FILENAME = "/var/www/cgi-bin/hello.pl"
SCRIPT_NAME = "/cgi-bin/hello.pl"
SERVER_ADDR = "127.0.0.1"
SERVER_ADMIN = "root@localhost"
SERVER_NAME = "127.0.0.1"
SERVER_PORT = "80"
SERVER_PROTOCOL = "HTTP/1.1"
SERVER_SIGNATURE = "<address>Apache/2.2.15 (CentOS) Server at 127.0.0.1 Port 80</address>
"
SERVER_SOFTWARE = "Apache/2.2.15 (CentOS)"
```

这里可以得到GET方法的请求参数，比如 QUERY_STRING 以及 HTTP的一些基本信息，比如 HTTP_USER_AGENT 等信息，
这些都是通过环境变量得到的。

使用 Python 语言也是一样的，都需要加上输出的格式 `Content-type:text/html`

```
#!/usr/bin/env python
# -*- coding: UTF-8 -*-
print "Content-type:text/html"
print
print '<html>'
print '<head>'
print '<title>Hello</title>'
print '</head>'
print '<body>'
print '<h2>Hello Word! This is my first CGI program</h2>'
print '</body>'
print '</html>'
```

看一个计算数字的简单实例：

```html
<!DOCTYPE html>
<html>
 <body>
  <form action="../cgi-bin/add.py" method="POST">
   Enter two numbers to add:<br />
   First Number: <input type="text" name="num1" /><br />
   Second Number: <input type="text" name="num2" /><br />
   <input type="submit" value="Add" />
  </form>
 </body>
</html>
```
这里数据post 给 add.py，通过Python cgi模块的方法得到数据：

```python
#!/usr/bin/env python2

import cgi
import cgitb
cgitb.enable()

input_data = cgi.FieldStorage()

print 'Content-Type:text/html' # HTML is following
print                          # Leave a blank line
print '<h1>Addition Results</h1>'
try:
  num1 = int(input_data["num1"].value)
  num2 = int(input_data["num2"].value)
except:
  print '<p>Sorry, we cannot turn your inputs into numbers (integers).</p>'
print '<p>{0} + {1} = {2}</p>'.format(num1, num2, num1 + num2)
```

### CGI原理

```
Calling a command generally means the invocation of a newly created process on the server. Starting the process can consume much more time and memory than the actual work of generating the output, especially when the program still needs to be interpreted or compiled. If the command is called often, the resulting workload can quickly overwhelm the server.
```

我们可以使用不同的语言编写CGI代码，不过大同小异，都是一种原始的方式--每个请求新开启一个进程！

比如，我们让每个请求sleep一段时间，再看下进程个数：

```python
#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import time
for i in range(10):
    time.sleep(1)
print "Content-type:text/html"
print
print '<html>'
print '<head>'
print '<title>Hello</title>'
print '</head>'
print '<body>'
print '<h2>Hello Word! This is my first CGI program</h2>'
print '</body>'
print '</html>'
```

```shell
# ps aux| grep python
apache    2329  0.0  0.0  22384  3840 ?        S    14:06   0:00 python /var/www/cgi-bin/hello.py
apache    2330  0.0  0.0  22388  3844 ?        S    14:06   0:00 python /var/www/cgi-bin/hello.py
apache    2331  0.0  0.0  22388  3844 ?        S    14:06   0:00 python /var/www/cgi-bin/hello.py
```

参考：

http://www.tutorialspoint.com/python/python_cgi_programming.htm

https://en.wikipedia.org/wiki/Common_Gateway_Interface

https://docs.python.org/2/library/cgi.html

