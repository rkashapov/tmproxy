import abc
import urllib.parse

import aiohttp
from aiohttp import web


class IProcessor:
    """
    ..class:IProcessor is an interface defining
    html-formatted page processor methods.

    ..class:RegexProcessort uses it to process the origin server
    response content befere it will be sent to the client.

    A class implementing the interface must define `process_content` method.
    It accepts html page body in unicode and returns processed content.
    """

    @abc.abstractmethod
    def process_content(self, html_page: str) -> str:
        """
        `process_content` accepts html page content
        and returns processed string.

        :param html_page: an html page content
        :returns: processed page content
        """
        raise NotImplementedError


class Proxy(web.Application):
    """
    ..class:Proxy represents a simple http proxy server
    Proxy sends all accepted requests to an origin server specified by
    `address` argument.
    The body of the response received from the origin server is passed to the
    `processor` instance and sent back to the client.

    :param address: origin server address in https://example.com form.
    :param processor: an object of class implementing IProcessor interface.
    """

    def __init__(self, address, processor):
        super().__init__()

        address = urllib.parse.urlsplit(address)

        self.host = f"{address.scheme}://{address.hostname}"
        self.netloc = address.netloc
        self.port = address.port

        self.processor = processor

        self.router.add_route("GET", "/{tail:.*}", self.handler)

    async def handler(self, request):
        """
        `handler` is a handler for client requests.
        """
        response = await self.send_to_origin(request)

        headers = response.headers.copy()
        body = response.body

        if response.status == 200:
            if "text/html" in headers['Content-Type']:
                charset = response.charset or 'utf-8'
                body = self.process_body(body.decode(charset))
                body = body.encode(charset)

        headers["Connection"] = "close"
        headers["Content-Length"] = str(len(body))
        headers.pop("Transfer-Encoding", None)
        headers.pop("Content-Encoding", None)

        return web.Response(body=body,
                            headers=headers,
                            status=response.status)

    async def send_to_origin(self, request):
        """
        `send_to_origin` sends the request accepted from the
        client to the origin server.
        """
        url = self.host + request.path

        # Pass all client headers to the origin server.
        headers = request.headers.copy()
        # Change host header to the right one.
        headers["Host"] = self.netloc
        # We don't use the persistent connection.
        # Tell to the origin server about it.
        headers["Connection"] = "close"

        with aiohttp.ClientSession() as sess:
            response = await sess.request(
                method=request.method,
                params=request.query_string,
                url=url,
                headers=headers,
            )
            response.body = await response.content.read()

        return response

    def process_body(self, body):
        return self.processor.process_content(body)

    def run(self, port):
        """
        Start server on the `port`.
        """
        web.run_app(self, port=port)
