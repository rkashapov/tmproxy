from unittest import TestCase

from proxy import processor
from proxy.server import IProcessor, Proxy


class TestLinkProcessor(TestCase):
    def test(self):
        lp = processor.LinkProcessor("https://habrahabr.ru")

        self.assertEqual(lp.process_content('<a href="https://habrahabr.ru/foo/bar/baz"></a>'),
                         '<a href="/foo/bar/baz"></a>',
                         'LinkProcessor.process_content must cut a known hostname part.')
        self.assertEqual(lp.process_content('<a href="/foo/bar/baz"></a>'),
                         '<a href="/foo/bar/baz"></a>',
                         'LinkProcessor.process_content must not modify absolute urls.')
        self.assertEqual(lp.process_content('<a></a>'), '<a></a>',
                         'LinkProcessor.process_content must not modify a tag.')
        self.assertEqual(lp.process_content('https://habrahabr.ru/foo/bar/baz'),
                         'https://habrahabr.ru/foo/bar/baz',
                         'LinkProcessor.process_content must not modify a text')
        self.assertEqual(lp.process_content('<div>https://habrahabr.ru/foo/bar/baz</div>'),
                         '<div>https://habrahabr.ru/foo/bar/baz</div>',
                         'LinkProcessor.process_content must not modify a text')
        self.assertEqual(lp.process_content('https://unknown.com/foo/bar/baz'),
                         'https://unknown.com/foo/bar/baz',
                         'LinkProcessor.process_content must not modify an unknown host')
        self.assertEqual(lp.process_content(''), '',
                         'LinkProcessor.process_content must return empty string')
        self.assertEqual(lp.process_content('<img src="http://habrahabr.ru/image.png">'),
                         '<img src="http://habrahabr.ru/image.png">',
                         'LinkProcessor.process_content must not modify image sources')


class TestTMProcessor(TestCase):
    def test(self):
        tm = processor.TMProcessor()

        self.assertEqual(tm.process_content(''), '',
                         'TMProcessor.process_content must return empty string')
        self.assertEqual(tm.process_content('<script>sixchr < foobar <script>'),
                         '<script>sixchr < foobar <script>',
                         'TMProcessor.process_content must not modify script content')
        self.assertEqual(tm.process_content('<style>a {sixchr: "foobar"} <style>'),
                         '<style>a {sixchr: "foobar"} <style>',
                         'TMProcessor.process_content must not modify style content')
        self.assertEqual(tm.process_content('<div class="sixchr"></div>'),
                         '<div class="sixchr"></div>',
                         'TMProcessor.process_content must not modify tag contents')
        self.assertEqual(tm.process_content('<div>Foo bar baz</div>'),
                         '<div>Foo bar baz</div>',
                         'TMProcessor.process_content must not modify words with length < 6')
        self.assertEqual(tm.process_content('<div>Longlong str</div>'),
                         '<div>Longlong str</div>',
                         'TMProcessor.process_content must not modify words with length > 6')
        self.assertEqual(tm.process_content('<div>sixchr sixchr sixchr.</div>'),
                         '<div>sixchr™ sixchr™ sixchr™.</div>',
                         'TMProcessor.process_content must add ™ character after words with length = 6')
        self.assertEqual(tm.process_content('sixchr foo, sixchr, longlong.'),
                         'sixchr™ foo, sixchr™, longlong.',
                         'TMProcessor.process_content must add ™ character after words with length = 6')
        self.assertEqual(tm.process_content('sixchr'), 'sixchr™',
                         'TMProcessor.process_content must add ™ character after words with length = 6')


class ReplaceProcessor(IProcessor):
    def __init__(self, string, replace):
        self.string = string
        self.replace = replace

    def process_content(self, html_page):
        return html_page.replace(self.string, self.replace)


class MultiProcessorTest(TestCase):
    def test(self):
        mp = processor.MultiProcessor(
            ReplaceProcessor('foo', 'bar'),
            ReplaceProcessor('egg', 'spam'),
        )
        self.assertEqual(mp.process_content(''), '',
                         "MultiProcessor.process_content must not modify empty strign")
        self.assertEqual(mp.process_content('foo egg'), 'bar spam',
                         "MultiProcessor.process_content must apply both processors")


text = """
<html>
    <head><title>Python</title></head>
    <body bgcolor="sixchr">
        <center><h1>This is Python</h1></center>
    </body>
    <!-- Comment string -->
</html>
"""

expected_text = """
<html>
    <head><title>Python™</title></head>
    <body bgcolor="sixchr">
        <center><h1>This is Python™</h1></center>
    </body>
    <!-- Comment string -->
</html>
"""


class TestProxy(TestCase):
    def test_success(self):
        host = "http://localhost"
        proc = processor.MultiProcessor(
            processor.LinkProcessor(host),
            processor.TMProcessor(word_len=6),
        )
        proxy = Proxy(host, proc)
        self.assertEqual(proxy.process_body(text), expected_text)
