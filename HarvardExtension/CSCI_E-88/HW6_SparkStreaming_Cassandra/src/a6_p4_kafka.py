import sys

from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
import datetime

if __name__ == '__main__':
    if len(sys.argv) != 3:
        exit('Usage: a6_p4_kafka.py <topic>')

    sc = SparkContext(appName='Problem 4')
    # 1 second duratoin
    ssc = StreamingContext(sc, 1)

    # add checkpoining directory, necessary for stateful transformations
    ssc.checkpoint("/tmp/checkpoint")

    topic = sys.argv[1]
    window_duration = int(sys.argv[2])
    group_id = 'p4_group'
    # KafkaUtils.createStream(streamingContext,  [ZK quorum], [consumer group id], [per-topic number of Kafka partitions to consume])
    kvs = KafkaUtils.createStream(ssc, 'localhost:2181', group_id, {topic: 1})

    # events in format of tab separated: 2017-08-02 07:31:32	google.com	u05
    # use map to pull out value and discard key (index=1), then split on tab and then map each userID as key
    userids = kvs.map(lambda x: x[1]).map(lambda x: x.split('\t')).map(lambda row: (row[2]))

    def hll(rdd):
        stamp = datetime.datetime.now()
        # add timestamp value to output becausse "streaming window timestamp" does not print for HLL calcs
        # my gues is it directly relates to use of foreeachRDD()
        sd = 0.05
        print('{} countApproxDistinct w/relative SD of {}: '.format(stamp, sd), rdd.countApproxDistinct(sd), flush=True)

    # window duration and slide duration of equal values results in tumbling window
    userids.window(window_duration, window_duration).foreachRDD(hll)

    ssc.start()
    ssc.awaitTermination()

