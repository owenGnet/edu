
import argparse
from threading import Thread
from queue import Queue
import time
import collections

from kafka import KafkaConsumer


def consumer(q, thread_id, group_id, main_topic, check_topic, is_debug=False):
    # auto_offset_reset = 'earliest',
    c = KafkaConsumer(
        bootstrap_servers='localhost:9092',
        group_id=group_id,
        enable_auto_commit=False # for Problem 13, turn off auto-commit
    )
    # will create topic if it doesn't already exist
    c.subscribe([main_topic, check_topic])

    for msg in c:
        if msg.topic == main_topic:
            key_value = None if msg.key is None else msg.key.decode()
            info = '''
    thread {} message received
        - partition number: {}
        - event key: {}
        - event body: {}'''.format(thread_id, msg.partition, key_value, msg.value.decode())
            print(info)
            #q.put(thread_id)
            q.put((thread_id, msg.partition))

        else:
            # report on per-thread_id/partition combinations, in a sorted manner
            for k, v in sorted(collections.Counter(q.queue).items(), key=lambda val: (val[0], val[1])):
                print('thread_id: {}, count: {}, pct total: {:.0f}%'.format(k, v, v / len(q.queue) * 100))

        # python version of commitAsync()
        c.commit_async()

        # if is_debug:
        #     time.sleep(1)


def do_threads(thread_count, is_debug=False):

    group_id = 'p13consumer'
    main_topic = 'problem13'
    # topic to be used to display distribution informaiton
    check_topic = 'problem13a'

    q = Queue()

    log_threads = []
    for i in range(1, thread_count + 1):
        new_thread = Thread(target=consumer, args=(q, i, group_id, main_topic, check_topic, is_debug))
        print('thread {} starting'.format(i), flush=True)
        log_threads.append(new_thread)
        new_thread.start()

    #don't return until all the threads have completed
    [t.join() for t in log_threads]

    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run selected number of threads')
    parser.add_argument('-t', '--thread-count', type=int, default=1)
    parser.add_argument('-d', '--debug', type=bool, default=False)
    args = parser.parse_args()

    threads_complete = do_threads(args.thread_count, args.debug)

    print('DONE')