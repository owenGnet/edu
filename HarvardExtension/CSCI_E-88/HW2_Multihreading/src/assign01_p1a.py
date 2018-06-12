# write a simple program in your choice of language that does:
# 		§ creates specified number of threads - based on the input parameter
# 		§ starts each of those threads
# 		§ each thread does:
# 			□ sleep for 10-15 ms
# 			□ do some CPU-intensive work - like parsing a RegExp [your choice]
# 			□ do above 2 things forever
# 	○ start your app and let it run
# 	○ using Unix tools like ‘top’, ‘ps’ , 'htop' and Java specific ones like ‘jps’ - try to figure out how your threads are mapped to available CPUs - include the results into your solution document (screenshots and explanation)
# 	○ change the input parameter (number of threads to start) - see how it affects the CPU usage. Include your results into your solution document  (screenshots and explanation)
# 	○ create a graph of # of threads vs. CPU utilization [bonus: +5 points]

import argparse
from threading import Thread
from time import sleep
import itertools

def do_stuff(thread_num, sleep_for_ms=10, combo_iter=300, is_debug=False):
    i = 1
    while i <= 100 or not is_debug:
        sleep(sleep_for_ms/1000)
        sum(sum(i) for i in itertools.combinations(range(combo_iter), 3))
        if is_debug:
            print('thread: {}    iter: {}     combo iter range: {}'.format(thread_num, i, combo_iter))
        i += 1

def do_threads(thread_count, sleep_milliseconds, combo_iterations, is_debug):
    for i in range(1, thread_count + 1):
        new_thread = Thread(target=do_stuff, args=(i, sleep_milliseconds, combo_iterations, is_debug))
        new_thread.start()
        print('thread {} started'.format(i))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run selected number of threads')
    parser.add_argument('-t', '--thread-count', type=int, default=1)
    parser.add_argument('-m', '--sleep-milliseconds', type=int, default=10)
    parser.add_argument('-c', '--combo-iterations', type=int, default=300)
    parser.add_argument('-d', '--debug', type=bool, default=False)
    args = parser.parse_args()
    print('BEGIN TEST, thread count: {}, milliseconds to sleep for: {}, combo iterations: {}, debug: {}'.format(
        args.thread_count, args.sleep_milliseconds, args.combo_iterations, args.debug))

    do_threads(args.thread_count, args.sleep_milliseconds, args.combo_iterations, args.debug)

