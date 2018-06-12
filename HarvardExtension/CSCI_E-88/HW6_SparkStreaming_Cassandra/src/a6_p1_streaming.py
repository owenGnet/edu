# based off of https://hortonworks.com/hadoop-tutorial/introduction-spark-streaming/ example

from pyspark import SparkContext
from pyspark.streaming import StreamingContext

# create local spark context with two threads
sc = SparkContext("local[2]", "A6 Problem 1")
# StreamingContext with batch inverval of 1 second
ssc = StreamingContext(sc, )

# add checkpoining directory, necessary for stateful transformations
ssc.checkpoint("checkpoint")

# Create a DStream
events = ssc.socketTextStream("localhost", 7777)

# events in format of tab separated: 2017-08-02 07:31:32	google.com	u05
# split on tab and then map each url as key, value = int = 1
urls = events.map(lambda x: x.split('\t')).map(lambda row: (row[1], 1))
# use reduceByKey to sum up the per-key 1 values, to get a total per key/url
url_counts = urls.reduceByKey(lambda x, y: x + y)

# print number of clicks per url, current batch
url_counts.pprint()

# define function to be called by updateStateByKey in order to do stateful calculations
update_state = lambda batch_count, running_count: sum(batch_count) + (running_count or 0)

running_counts = urls.reduceByKey(lambda x, y: x + y).updateStateByKey(update_state)
# print running totals
running_counts.pprint()

ssc.start()
ssc.awaitTermination()
