import argparse

from pyspark import SparkContext
from pyspark.streaming import StreamingContext
import datetime

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Unique ')
    parser.add_argument('-w', '--window-duration', type=int, default=10)
    parser.add_argument('-a', '--aggregation_type', type=str, default='spark', help='"spark" or "hll "')
    parser.add_argument('-r', '--relative-sd', type=float, default=0.05)
    parser.add_argument('-d', '--debug', type=bool, default=False)
    args = parser.parse_args()

    if args.aggregation_type.lower() not in ('spark', 'hll'):
        agg = 'spark'
    else:
        agg = args.aggregation_type.lower()

    # create local spark context with two threads
    sc = SparkContext('local[2]', 'A6 Problem 3 {}'.format(agg if agg == 'spark' else 'hll @ {}'.format(args.relative_sd)))
    # StreamingContext with batch inverval of 1 second
    ssc = StreamingContext(sc, 1)
    # add checkpoining directory, necessary for stateful transformations
    ssc.checkpoint("/tmp/checkpoint")

    # Create a DStream
    events = ssc.socketTextStream("localhost", 7777)

    # events in format of tab separated: 2017-08-02 07:31:32	google.com	u05
    # split on tab and then map each userID as key
    userids = events.map(lambda x: x.split('\t')).map(lambda row: row[2])

    if args.debug:
        userids.pprint()

    # Calculate the number of unique users per N sec tumbling windows, spark aggregation
    userid_counts = userids.countByValueAndWindow(args.window_duration, args.window_duration)
    if args.debug:
        # with 20 userids the length of this rdd should never be > 20, print in full
        userid_counts.pprint(30)

    if agg == 'spark':
        # the count of distinct userids in current window
        count_distinct = userid_counts.count().map(lambda c: 'unique userid count, spark aggregation: {}'.format(c))
        count_distinct.pprint()
    else:
        #userid_counts.count().map(lambda x: '').pprint()
        # create the function that takes an RDD and performs countApproxDistinct on it
        def hll(rdd):
            stamp = datetime.datetime.now()
            # default relativeSD = 0.05, must be > 0.000017
            if args.debug:
                # do a spread of relative standard deviation values, + whatever was passed in
                relative_sds = sorted(set([0.001, 0.05, 0.25] + [args.relative_sd]))
            else:
                relative_sds = [args.relative_sd]
            for sd in relative_sds:
                # add timestamp value to output becausse "streaming window timestamp" does not print for HLL calcs
                # my gues is it directly relates to use of foreeachRDD()
                print('{} countApproxDistinct w/relative SD of {}: '.format(stamp, sd), rdd.countApproxDistinct(sd), flush=True)
        # window duration and slide duration of equal values results in tumbling window
        userids.window(args.window_duration, args.window_duration).foreachRDD(hll)

    ssc.start()
    ssc.awaitTermination()
