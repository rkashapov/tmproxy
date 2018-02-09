import io
import re

from .server import IProcessor


class AbstractTextProcessor(IProcessor):
    """
    AbstractTextProcessor is a processor with `process_text` method.
    All text except html tags, scripts and styles encountered on the
    html page is passed to the method.
    """

    def process_text(self, text, output):
        """
        Handle all the text on being processed page.
        Processed text should be written to the `output` buffer.
        """
        raise NotImplementedError

    def process_content(self, html_page):
        output = io.StringIO()
        data = io.StringIO(html_page)

        # last opened tag name
        tag = ''

        # are we inside the script or style tag?
        in_script = False

        # buffer to collect text
        text = io.StringIO()

        for char in iter(lambda: data.read(1), ''):
            if char == '<':
                if in_script:
                    # There is a situation when in script body
                    # could be "<" character. Check if it is a closing tag.
                    pos = data.tell()
                    next_char = data.read(1)
                    if next_char != '/':
                        output.write(char)
                        output.write(next_char)
                        continue

                    data.seek(pos, 0)

                # We encountered a tag start.
                # Process collected text and reset text buffer
                self.process_text(text.getvalue(), output)
                text = io.StringIO()

                output.write(char)

                # current tag name
                tag = ''

                # skip tag contents
                while char and char != '>':
                    tag += char

                    # If current tag is script or style
                    # we should ignore it contents.
                    if tag in ("<script", "<style"):
                        in_script = True
                    elif in_script and tag in ("</script", "</style"):
                        in_script = False

                    char = data.read(1)
                    output.write(char)

                continue

            if in_script:
                # We are in script or style tag.
                output.write(char)
                continue

            # We are in text now
            text.write(char)

        # process remining text
        self.process_text(text.getvalue(), output)

        return output.getvalue()


class TMProcessor(AbstractTextProcessor):
    """
    `TMProcessor` adds ™ (trademark) character to the end of
    all words which length is exactly `word_len`.
    """
    def __init__(self, word_len=6):
        self.word_len = word_len

    def process_text(self, text, output):
        word_len = 0

        for char in text:
            if not char.isalpha():
                if word_len == self.word_len:
                    output.write('™')
                word_len = 0
            else:
                word_len += 1

            output.write(char)

        # check last word
        if word_len == self.word_len:
            output.write('™')


class LinkProcessor(IProcessor):
    """
    LinkProcessor modifies `href` urls leading to the
    `hostname` argument to be absolute links.

    Example
    >>> lp = LinkProcessor("https://habrahabr.ru")
    >>> link = '<a href="https://yandex.ru/all/"></a>'
    >>> assert lp.process_html(link) == '<a href="/all/"></a>'
    """
    def __init__(self, hostname):
        self._href_regex = re.compile(f"(?<=href=.){hostname}")

    def process_content(self, html_page):
        return self._href_regex.sub("", html_page)


class MultiProcessor(IProcessor):
    """
    MultiProcessor delegates processing to given processors
    and combines they output.
    """
    def __init__(self, *processors):
        self._processors = processors

    def process_content(self, html_page):
        for proc in self._processors:
            html_page = proc.process_content(html_page)
        return html_page
