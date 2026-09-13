#!/usr/bin/env python3

import sys

from pdfmypics.app import PDFMyPicsApp


def main():
    app = PDFMyPicsApp()
    return app.run(sys.argv)


if __name__ == "__main__":
    main()


