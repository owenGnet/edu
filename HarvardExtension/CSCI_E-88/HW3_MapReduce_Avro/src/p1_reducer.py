#!/usr/bin/env python

import sys
import collections
import argparse

def reduce(reduced_map, input_line):
    input_line = input_line.strip()
    url, dict_string = input_line.split("\t")

    user_dict = eval(dict_string)

    if url in reduced_map:
        # in this toy example all the urls in additional maps will be in that reduced_map, this will be expected path
        for uid, count in user_dict.items():
            # iterate through the user_id: count map for the current url in "new" map
            if uid in reduced_map[url]:
                # this uid already appeared for this url, increment count
                reduced_map[url][uid] = reduced_map[url][uid] + count
            else:
                # new uid for current url, transfer the count from current map to reduced_map
                reduced_map[url][uid] = count
    else:
        # should a new url be encountered, add it to the base map
        reduced_map[url] = user_dict


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Return results of Hadoop streaming map reduce queries')
    parser.add_argument('-q', '--query-number', type=int, default=3,
                        help='Number (1, 2, or 3) of Query for which results should be returned')
    parser.add_argument("-d", "--debug", type=bool, default=False)
    args = parser.parse_args()

    reduced_map = collections.defaultdict(dict)
    for input_line in sys.stdin:
        reduce(reduced_map, input_line)

    if args.debug:
        print('-'*20, 'BEGIN DEBUG', '-'*20)
        for k, v in reduced_map.items():
            print('{}\t{}'.format(k, v))
        print('-'*20, 'END DEBUG', '-'*20)

    if args.query_number == 1:
        print('Query 1: get count of unique URLs: {}'.format(len(reduced_map)))
    elif args.query_number == 2:
        query_2 = ['{}: {}'.format(url, len(user)) for url, user in reduced_map.items()]
        print('Query 2: get count of unique visitors per URL: \n - {}'.format('\n - '.join(query_2)))
    else:
        print( 'Query 3: get count of unique (by userId) clicks per URL: ')
        for url,uids in reduced_map.items():
            print(' - {}'.format(url))
            for uid, count in uids.items():
                print('   - {}: {}'.format(uid, count))
