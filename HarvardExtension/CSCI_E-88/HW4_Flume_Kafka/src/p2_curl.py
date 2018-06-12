import requests
import datetime, time
import argparse


def do_gets(gets_per_second_limit, is_debug=False):
    # this first bit is just about starting off at the beginning of the next whole second
    begin = datetime.datetime.now().second
    new_now = begin
    while new_now <= begin:
        time.sleep(.01)
        new_now = datetime.datetime.now().second

    total_count_limit = 500
    # use total_count as a failsafe in debug mode
    total_count = 0
    # essentially run "forever" (unless is_debug = True, in which case exit after GET count hits total_count_limit
    while True and (not is_debug or total_count < total_count_limit):
        gets_made = 0
        # normally want to wait after x GET request made in "this" second, but not if gets_per_second > number that can be performed
        # w/o skip_wait the script would wait a full second in between loops
        skip_wait = False
        new_now = datetime.datetime.now().second
        # keep making GETs while in current second and still under requested limit
        while gets_made < gets_per_second_limit:
            gets_made += 1
            total_count += 1
            #print(datetime.datetime.now().second, gets_made, total_count)
            r = requests.get('http://localhost/index.html')
            # below is for problem 5, where I need to adjust port to 8081, on EMR cluster
            # r = requests.get('http://localhost:8081/index.html')
            # spent more than a second making requests, gets_per_second_limit was too high
            if datetime.datetime.now().second > new_now:
                skip_wait = True
                print('gets_per_second_limit ({}) higher than can be performed ({}), going to continue doing best we can'.format(
                    gets_per_second_limit, gets_made))
                break

        # we've made number of requested GETs for this second, hold off until we hit a whole new "second" unit of time
        new_now = datetime.datetime.now().second
        #print('new now a', new_now)
        while datetime.datetime.now().second == new_now and not skip_wait:
            time.sleep(.01)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Perform requested number of GETs per second on http://localhost/index.html')
    parser.add_argument('-c', '--count-per-second', type=int, required=True, help='number of GETs per second to attempt')
    parser.add_argument("-d", "--debug", type=bool, default=False)
    args = parser.parse_args()

    do_gets(args.count_per_second, args.debug)
