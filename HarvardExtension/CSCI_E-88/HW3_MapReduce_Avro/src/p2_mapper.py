#!/usr/bin/env python


import sys
import collections
import datetime

# some googling and playing around to get a defaultdict of type = defaultdict, suffice to say it works
single_map = collections.defaultdict(lambda: collections.defaultdict(dict))

for line in sys.stdin:

    timestamp, url, user_id = line.strip().split('\t')
    # string in format of "2017-09-12 06:31:55", turn that into a datetime object and pull out the hour
    hour = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S').hour

    # same as with p1 mapper, only now there is a parent key=hour dict holding everything
    if hour in single_map and url in single_map[hour]:
        if user_id in single_map[hour][url]:
            # increase existing count by one
            single_map[hour][url][user_id] = single_map[hour][url][user_id] + 1
        else:
            # new user_id for this hour/url, add with count = 1
            single_map[hour][url].update({user_id: 1})
    else:   # by definition, this url ain't in here
        single_map[hour][url].update({user_id: 1})

# iterate through all levels of dictionaries, though I've only sorted the hour one, helps with troubleshooting
for hour, url_map in sorted(single_map.items(), key=lambda item: item[0] ):
    for url, uid_map in url_map.items():
        for uid, count in uid_map.items():
            # this time doing one single tab separate line for each item in the nested dicts
            print('{}\t{}\t{}\t{}'.format(hour, url, uid, count))
