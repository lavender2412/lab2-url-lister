#!/usr/bin/env python3
"""URLMapper.py: emit <url, 1> for every href="..." on each input line"""

import re
import sys

# capture whatever sits between href=" and the next double quote
HREF = re.compile(r'href="([^"]*)"')

for line in sys.stdin:
    for url in HREF.findall(line):
        print('%s\t%s' % (url, 1))
