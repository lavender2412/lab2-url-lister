#!/usr/bin/env python3
"""URLReducer.py: sum counts per URL, output only URLs seen more than 5 times"""

import sys

THRESHOLD = 5

current_url = None
current_count = 0

# Hadoop sorts map output by key, so identical URLs arrive consecutively
for line in sys.stdin:
    url, count = line.rstrip('\n').split('\t', 1)
    try:
        count = int(count)
    except ValueError:
        continue

    if url == current_url:
        current_count += count
    else:
        if current_url is not None and current_count > THRESHOLD:
            print('%s\t%s' % (current_url, current_count))
        current_url = url
        current_count = count

# flush the last URL
if current_url is not None and current_count > THRESHOLD:
    print('%s\t%s' % (current_url, current_count))
