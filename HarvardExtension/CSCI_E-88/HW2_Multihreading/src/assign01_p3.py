# write a multi-threaded program to generate "log" files as following:
# - specify application parameters: number of distinct userIds, list of URLs , number of "events" per URL per user; number of threads in the app
# - number of log lines should be: [number of distinct userIds] X [number of URLs] X [number of "events" per URL per user]
# - create specified number of threads - "writers"
# - each writer thread should generate one output file with logs in the format (one line == one event)
# 	- <timestamp> <url> <userId>
#  *** For this HW - the actual values of timestamps are not important and can be simulated, because we do not do any aggregations/analytics
#    based on time. They serve the purpose of uniquely identifying each log record only for now.
# - name of the file should be:
# 	- <threadID>_events.txt
# right now, each log file can have the exact same combination of input data. We will not be doing any partitioning of data yet.
# This will come in the next set of HWs.However, having the ability to parameterize generation of input data is going to
# help you to generate potentially different sets of data later on, when needed (with minor tweaks)


import argparse
from threading import Thread
from random import randint
import collections
import os, shutil

def prepare_output_dir(output_dir):
    if os.path.exists(output_dir):
        if os.path.isfile(output_dir):
            os.remove(output_dir)
        else:
            shutil.rmtree(output_dir)
    wait_seconds = 10
    waited = 0
    while os.path.exists(output_dir) and waited < wait_seconds:
        import time
        time.sleep(1)
        waited += 1
    os.mkdir(output_dir)

# make a deque with all the (random over a static day) timestamps that will be needed for given set of inputs
def get_all_timestamps(count):
    #'YYYY-MM-DD HH:MM:SS'
    return collections.deque('2017-09-12 {hour:02}:{minute:02}:{second:02}'.format(
        hour=randint(0,23), minute=randint(0,59), second=randint(0,59)) for i in range(count))

# generate a list of user-ids in format of u##, zero-filled from the left as appropriate to total count
def get_userids(count):
    return ['u' + str.zfill('{}'.format(i), len(str(count))) for i in range(1, count+1)]

def generate_log(thread_number, output_dir, data, is_debug=False):
    # import itertools
    # sum(sum(i) for i in itertools.combinations(range(300), 3))
    log_path = os.path.join(output_dir, '{}_events.txt'.format(thread_number))
    with open(log_path, 'w') as f:
        lines = '\n'.join(data).strip()
        f.write(lines)
        if is_debug:
            print('-- wrote: {}'.format(log_path), flush=True)

def do_threads(num_userids, urls, event_count, thread_count, total_num_events, is_debug):
    output_dir_path = 'output'
    prepare_output_dir(output_dir_path)

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
           print(visit)

    log_threads = []
    for i in range(1, thread_count + 1):
        new_thread = Thread(target=generate_log, args=(i, output_dir_path, visits, is_debug))
        print('thread {} starting'.format(i), flush=True)
        log_threads.append(new_thread)
        new_thread.start()

    #don't return until all the threads have completed
    [t.join() for t in log_threads]

    return output_dir_path


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

    output_path = do_threads(args.num_userids, urls, args.event_count, args.thread_count, total_event_count, args.debug)

    print('\nDONE, contents of {}\n - {}'.format(output_path, '\n - '.join(os.listdir(output_path))))
