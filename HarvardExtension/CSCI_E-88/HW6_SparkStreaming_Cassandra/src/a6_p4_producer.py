
import argparse
from threading import Thread
from random import randint
import collections
import os, shutil
import time
import datetime

from kafka import KafkaConsumer, KafkaProducer


# make a deque with all the (random over a static day) timestamps that will be needed for given set of inputs
def get_all_timestamps(count):
    #'YYYY-MM-DD HH:MM:SS'
    return collections.deque('2017-09-12 {hour:02}:{minute:02}:{second:02}'.format(
        hour=randint(0,23), minute=randint(0,59), second=randint(0,59)) for i in range(count))

# generate a list of user-ids in format of u##, zero-filled from the left as appropriate to total count
def get_userids(count):
    return ['u' + str.zfill('{}'.format(i), len(str(count))) for i in range(1, count+1)]

def produce_topic_events(thread_number, data, is_debug=False):
    # use same url as passed into the --broker-list arge for kafka-console-producer.sh
    producer = KafkaProducer(bootstrap_servers='localhost:9092')
    topic_name = 'hw6problem4'

    for line in data:
        # use 3 lines below for first part of problem 10
        producer.send(topic_name, str.encode(line))
        if is_debug:
            print('-- topic {}, message sent: : {}'.format(topic_name, line))

    producer.flush()

def do_threads(num_userids, urls, event_count, thread_count, total_num_events, is_debug):
    ts = get_all_timestamps(total_num_events)
    uids = get_userids(num_userids)
    visits = []
    for uid in uids:
        for url in urls:
            for i in range(event_count):
                visits.append('{}\t{}\t{}'.format(ts.pop(),url, uid,))

    #sort by the random timestamp, for better simulation
    visits = sorted(visits) #, key=lambda line: line.split()[-1])
    if is_debug:
        for visit in visits:
           #print(visit) # skip this for Assignment 4/Problem 10
            pass

    log_threads = []
    for i in range(1, thread_count + 1):
        #new_thread = Thread(target=generate_log, args=(i, output_dir_path, visits, is_debug))
        new_thread = Thread(target=produce_topic_events, args=(i, visits, is_debug))
        #print('thread {} starting'.format(i), flush=True)
        log_threads.append(new_thread)
        new_thread.start()

    #don't return until all the threads have completed
    [t.join() for t in log_threads]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run selected number of threads')
    parser.add_argument('-n', '--num-userids', type=int, default=5)
    parser.add_argument('-u', '--urls', type=str, default='', help='comma separated string of urls')
    parser.add_argument('-e', '--event-count', type=int, default=5)
    parser.add_argument('-t', '--thread-count', type=int, default=1)
    parser.add_argument('-d', '--debug', type=bool, default=False)
    args = parser.parse_args()
    urls = [u for u in args.urls.split(',') if u]
    url_count = len(urls)
    print('BEGIN TEST, userid count: {}, number of urls: {}, number of events: {}, number of threads: {}, debug: {}'.format(
        args.num_userids, url_count, args.event_count, args.thread_count, args.debug))
    total_event_count = args.num_userids * url_count * args.event_count
    print('TOTAL EVENT COUNT: {}'.format(total_event_count))

    while True:
        print('sending batch at {}'.format(datetime.datetime.now()))
        do_threads(args.num_userids, urls, args.event_count, args.thread_count, total_event_count, args.debug)
        time.sleep(1)
