#!/usr/bin/env python

import sys
import collections
import argparse


def reduce(reduced_map, input_line):
    input_line = input_line.strip()
    hour, url, uid, count = input_line.split("\t")

    # if we don't do this the numbers will be appended like strings '1'+'2' = '12', as I found out
    count = int(count)
    updated = False
    if hour in reduced_map:
        if url in reduced_map[hour]:
            if uid in reduced_map[hour][url]:
                #get the exisitng count and increase by the value of incoming count
                reduced_map[hour][url][uid] = reduced_map[hour][url][uid] + count
                updated = True
    # brand new entry, add with the incoming count
    if not updated:
        reduced_map[hour][url][uid] = count


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Return results of Hadoop streaming map reduce queries')
    parser.add_argument('-q', '--query-number', type=int, default=3,
                        help='Number (1, 2, or 3) of Query for which results should be returned')
    parser.add_argument("-d", "--debug", type=bool, default=False)
    args = parser.parse_args()

    reduced_map = collections.defaultdict(lambda: collections.defaultdict(dict))
    for input_line in sys.stdin:
        reduce(reduced_map, input_line)

    # print out everything, each dictionary soreted on its keys
    if args.debug:
        print('-'*20, 'BEGIN DEBUG', '-'*20)
        for hour, url_map in sorted(reduced_map.items(), key=lambda item: item[0]):
            for url, uid_map in sorted(url_map.items(), key=lambda item: item[0]):
                for uid, count in sorted(uid_map.items(), key=lambda item: item[0]):
                    print('{}\t{}\t{}\t{}'.format(hour, url, uid, count))
        print('-'*20, 'END DEBUG', '-'*20)


    # if debug is set, run/print every query
    #	uery 1: get count of unique URLs by hour
    if args.query_number == 1 or args.debug:
        query_1 = ['{}: {}'.format(hour, len(url)) for hour, url in reduced_map.items()]
        print('Query 1: get count of unique URLs by hour: {}'.format(query_1))
        print()
    # Query 2: get count of unique visitors per URL by hour
    if args.query_number == 2 or args.debug:
        #query_2 = ['{}: {}'.format(url, len(user)) for url, user in reduced_map.items()]
        print('Query 2: get count of unique visitors per URL by hour:')
        for hour, url in sorted(reduced_map.items(), key=lambda item: item[0]):
            print('hour: {}'.format(hour))
            for url, uid_map in url.items():
                print('\turl {}: count of unique visitors: {}'.format(url, len(uid_map)))
        print()
    # Query 3: get count of unique (by userId) clicks per URL by hour
    if args.query_number == 3 or args.debug:
        print( 'Query 3: get count of unique (by userId) clicks per URL by hour: ')
        for hour, url_map in sorted(reduced_map.items(), key=lambda item: item[0]):
            print('hour: {}'.format(hour))
            for url, uid_map in sorted(url_map.items(), key=lambda item: item[0]):
                print('\turl: {}'.format(url))
                for uid, count in sorted(uid_map.items(), key=lambda item: item[0]):
                    print('\t\tuid {}: count of unique clicks by userId: {}'.format(uid, count))
