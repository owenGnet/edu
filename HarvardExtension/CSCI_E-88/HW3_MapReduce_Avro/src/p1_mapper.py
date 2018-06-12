#!/usr/bin/env python

import sys
import collections

single_map = collections.defaultdict(dict)

for line in sys.stdin:

    timestamp, url, user_id = line.strip().split('\t')
    if url in single_map and user_id in single_map[url]:
        # this url already registered a hit for this uid, increment the count
        single_map[url][user_id] = single_map[url][user_id] + 1
    else:
        # either a brand new url or a brand new user to the existing url, register as a new hit
        single_map[url].update({user_id: 1})

for k, v in single_map.items():
    print('{}\t{}'.format(k, v))