

"""
 Counts words in UTF8 encoded, '\n' delimited text directly received from Kafka in every 2 seconds.
 Usage: direct_kafka_wordcount.py <broker_list> <topic>

 To run this on your local machine, you need to setup Kafka and create a producer first, see
 http://kafka.apache.org/documentation.html#quickstart

 and then run the example
    `$ bin/spark-submit --jars \
      external/kafka-assembly/target/scala-*/spark-streaming-kafka-assembly-*.jar \
      examples/src/main/python/streaming/direct_kafka_wordcount.py \
      localhost:9092 test`
"""

from __future__ import print_function
import sys

from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print ("Usage: direct_kafka_wordcount.py <broker_list> <topic>", file=sys.stderr)
        exit(-1)

    sc = SparkContext(appName="PythonStreamingDirectKafkaWordCount")
    ssc = StreamingContext(sc, 1) #batch interval to 1 second
    ssc.checkpoint('lec08checkpoint')

    brokers, topic = sys.argv[1:]
    kvs = KafkaUtils.createDirectStream(ssc, [topic], {"metadata.broker.list": brokers})
       
    # Please use windowing operations. The window is 30 seconds long and it moves every 5 seconds. Batch interval could remain 1 second.
    # Frequency (the count) for each digit in 30 second interval. That number should fluctuate. In one 30 second interval you will have 5 1-s, 7 2-s, 4 3-s, etc.    
    vals = kvs.map(lambda x: x[1])      
    counts = (vals.map(lambda num: (num, 1)) 
        .reduceByKeyAndWindow(lambda a, b: a + b, lambda a, b: a - b, 30, 5)
        .filter(lambda tup: tup[1] > 0))
        
    counts.pprint()

    ssc.start()
    ssc.awaitTermination()
