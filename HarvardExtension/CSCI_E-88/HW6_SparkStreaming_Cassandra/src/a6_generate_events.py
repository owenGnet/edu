import argparse
from random import randint
import collections
import time


# make a deque with all the (random over a static day) timestamps that will be needed for given set of inputs
def get_all_timestamps(count):
    #'YYYY-MM-DD HH:MM:SS'
    # assigment 5, problem 1 modification = timestamps that span 3 to 4 months in time
    Timepoint = collections.namedtuple('Timepoint', 'year month day hour minute second')
    time_points = (Timepoint(year=2017, month=randint(6,8), day=randint(1,30),
        hour=randint(0,23), minute=randint(0,59), second=randint(0,59)) for i in range(count))

    return collections.deque('{year}-{month:02}-{day:02} {hour:02}:{minute:02}:{second:02}'.format(
        year=t.year, month=t.month,  day=t.day if t.month==6 else randint(1,31), hour=t.hour,
        minute=t.minute, second=t.second) for t in time_points)

# generate a list of user-ids in format of u##, zero-filled from the left as appropriate to total count
def get_userids(count):
    return ['u' + str.zfill('{}'.format(i), len(str(count))) for i in range(1, count+1)]

def generate_log(log_path, data, is_debug=False):
    with open(log_path, 'a') as f:
        lines = '\n'.join(data).strip()
        f.write(lines)
        f.write('\n')
        if is_debug:
            print('-- wrote: {}'.format(log_path), flush=True)

def output_log(num_userids, urls, event_count, total_num_events, is_debug):

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

    log_file_path = 'p1_events/events.log'
    while True:
        generate_log(log_file_path, visits, is_debug)
        print('batch written, number of events: {}'.format(total_num_events))
        time.sleep(1.5)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Write/append events to log')
    parser.add_argument('-n', '--num-userids', type=int, default=5)
    parser.add_argument('-u', '--urls', type=str, default='', help='comma separated string of urls')
    parser.add_argument('-e', '--event-count', type=int, default=5)
    parser.add_argument('-d', '--debug', type=bool, default=False)
    args = parser.parse_args()
    urls = [u for u in args.urls.split(',') if u]
    url_count = len(urls)
    print('BEGIN, userid count: {}, number of urls: {}, number of events: {}, debug: {}'.format(
        args.num_userids, url_count, args.event_count,  args.debug))
    total_event_count = args.num_userids * url_count * args.event_count

    output_log(args.num_userids, urls, args.event_count, total_event_count, args.debug)


    print('DONE')
