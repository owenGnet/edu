
from pyspark import SparkContext
from pyspark.streaming import StreamingContext

# create local spark context with two threads
sc = SparkContext("local[2]", "A6 Problem 2")
# StreamingContext with batch inverval of 1 second
ssc = StreamingContext(sc, 1)

# add checkpoining directory, necessary for stateful transformations
ssc.checkpoint("/tmp/checkpoint")

# Create a DStream
events = ssc.socketTextStream("localhost", 7777)

# events in format of tab separated: 2017-08-02 07:31:32	google.com	u05
# split on tab and then map each url as key, value = int = 1
urls = events.map(lambda x: x.split('\t')).map(lambda row: (row[1], 1))
# use reduceByKey to sum up the per-key 1 values, to get a total per key/url
url_counts = urls.reduceByKey(lambda x, y: x + y)

# print number of clicks per url, current batch
url_counts.pprint()

#	1. Modify the job from Problem 1 to do a (tumbling) "windowed" count of events per URL - per 5 second windows, with the same 1 second batch duration
# drop update_state function, call reduceByKeyAndWindow directly on the urls RDD
#  first arg does the adding of counts in window and the 2nd arg is an inverse of that first one, subtracting counts that have left the window
#  the first 5 is the window duration, i.e. 5 seconds, the final "5" arg is for slide duration
#    by making these last args the same value, the type of window is a non-overlapping tumbling window
running_counts = urls.reduceByKeyAndWindow(lambda x, y: x + y, lambda x, y: x - y, 5, 5)

# # print running totals
running_counts.pprint()

ssc.start()
ssc.awaitTermination()
