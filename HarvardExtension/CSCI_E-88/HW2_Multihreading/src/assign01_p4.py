import argparse
import collections
import pprint
import os
from threading import Thread
from queue import Queue
from random import randint


def prep_input_files(master_log_file, input_folder, is_debug):
    num_new_files = 4

    inputs = collections.defaultdict(list)
    with open(master_log_file, 'r') as f:
        for line in f.readlines():
            # each line will be randomly assigned to one of the files that will be written
            # each file will wind up with similar number of lines but rarely the same number (unless source file has many lines)
            file_num = randint(1, num_new_files )
            inputs[file_num].append(line)
    if is_debug:
        pprint.pprint(inputs)

    # for each group of clicks, write them to a new file
    for k,v in inputs.items():
        with open('{}/{}_input.log'.format(input_folder, k), 'w') as f:
            f.writelines(v)

    return os.listdir(input_folder)

def parse_log(q, file_path, is_debug):
    with open(file_path, 'r') as f:
        single_map = collections.defaultdict(dict)
        for i,line in enumerate(f.readlines()):
            # source log files are tab separated
            timestamp, url, user_id = line.strip().split('\t')
            if url in single_map and user_id in single_map[url]:
                # this url already registered a hit for this uid, increment the count
                single_map[url][user_id] = single_map[url][user_id] + 1
            else:
                # either a brand new url or a brand new user to the existing url, register as a new hit
                single_map[url].update({user_id: 1})

    if is_debug:
       print('----', file_path)
       pprint.pprint(single_map)
    q.put(single_map)


#TODO: handle scenario where number of available threads <> number of files
def process_files(input_folder, is_debug):
    log_threads=[]
    q = Queue()
    for i, input_file in enumerate(os.listdir(input_folder)):
        new_thread = Thread(target=parse_log, args=(q, os.path.join(input_folder, input_file), is_debug))
        print('thread {} starting'.format(i+1), flush=True)
        log_threads.append(new_thread)
        new_thread.start()

    # .join() on all the threads so the queue won't be returned until it is fully populated
    [t.join() for t in log_threads]

    return q

def reduce_maps(q, is_debug):
    # there will be at least one map in the queue, get the first one and update it in place if there are more
    base_map = q.get()
    if is_debug:
        print('*** first dict')
        pprint.pprint(base_map)

    while not q.empty():
        new_map = q.get()
        if is_debug:
            print('*** next dict')
            pprint.pprint(new_map)
        # url is the key for top level dict, iterate through the urls at top level
        for url, user_dict in new_map.items():
            if url in base_map:
                # in this toy example all the urls in additional maps will be in that base_map, this will be expected path
                for uid, count in user_dict.items():
                    # iterate through the user_id: count map for the current url in "new" map
                    if uid in base_map[url]:
                        # this uid already appeared for this url, increment count
                        base_map[url][uid] = base_map[url][uid] + count
                    else:
                        # new uid for current url, transfer the count from current map to base_map
                        base_map[url][uid] = count
            else:
                # should a new url be encountered, add it to the base map
                base_map[url] = user_dict

    if is_debug:
        print('\n*** REDUCED dict')
        pprint.pprint(base_map)

    return base_map


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Use map of maps strategy to map/reduce source log data')
    parser.add_argument('-s', '--source-file', type=str, help='leave empty to skip creation of new input files')
    parser.add_argument('-l', '--log-directory', type=str, default='input',
                        help='folder in which results of processing source file will be saved')
    parser.add_argument("-d", "--debug", type=bool, default=False)
    args = parser.parse_args()

    if args.source_file:
        written = prep_input_files(args.source_file, args.log_directory, args.debug)
        print('DONE, log directory contents: \n - {}'.format('\n - '.join(written)))

    q = process_files(args.log_directory, args.debug)
    reduced = reduce_maps(q, args.debug)
    print('Query 1: get count of unique URLs: {}'.format(len(reduced)))
    query_2 = ['{}: {}'.format(url, len(user)) for url, user in reduced.items()]
    print('Query 2: get count of unique visitors per URL: \n - {}'.format('\n - '.join(query_2)))
    print( 'Query 3: get count of unique (by userId) clicks per URL: ')
    for url,uids in reduced.items():
        print(' - {}'.format(url))
        for uid, count in uids.items():
            print('   - {}: {}'.format(uid, count))
