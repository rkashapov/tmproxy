TM Proxy <img src="https://travis-ci.org/rkashapov/tmproxy.svg?branch=master" />
<img src="https://codecov.io/gh/rkashapov/tmproxy/branch/master/graph/badge.svg" />
========

TM Proxy is a simple web server that proxies all queries to specified server and sends back to a client a processed text.
The response processing is simple: the ™ character is added after all 6-character length words.

Live example is [here](https://still-ridge-34585.herokuapp.com).

Requirements
============
Python 3.6

How to run
==========
```bash
pip3 install -r requirements.txt
cd src
python3 -m proxy --host https://habrahabr.ru
```
This commands start http server on localhost on 7777 port.
The port number could be configured by PORT environment variable.
For example:
```bash
PORT=8888 python3 -m proxy --host https://habrahabr.ru
```

If you visit http://localhost:8888 in your browser you will see trademarked content.

Docker
======
You can run an image by executing command:
```bash
docker run -it --rm -p 8000:80 -e ORIGIN=https://habrahabr.ru rkashapov/tmproxy  
```
or build your own image using Dockerfile.