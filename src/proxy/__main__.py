import argparse
import os

from .server import Proxy
from . import processor


class TMProxy(Proxy):
    def __init__(self, address):
        proc = processor.MultiProcessor(
            processor.LinkProcessor(address),
            processor.TMProcessor(word_len=6),
        )
        super().__init__(address, proc)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", help="A URI to proxied host")
    args = parser.parse_args()

    port = int(os.getenv("PORT", 7777))

    proxy = TMProxy(args.host)
    proxy.run(port=port)


if __name__ == '__main__':
    main()
