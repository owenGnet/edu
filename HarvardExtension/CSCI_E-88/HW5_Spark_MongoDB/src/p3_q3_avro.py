from pyspark import SparkContext
from pyspark.sql import SQLContext

sc = SparkContext("local", "P3 Query 3")
sqlContext = SQLContext(sc)
#Query 3: get count of unique (by userId) clicks per URL by hour

avro_url = 's3://owengnet-data/e88/A5/DatasetAvro'
# read in the avro file, as RDD, use distinct() to de-dupe
rddAvro =  sqlContext.read.format("com.databricks.spark.avro").load(avro_url).rdd.distinct()

# take list of Row objects, like below, and simplify to strings so remaining code runs as-is
# rddAvro: Row(uuid=u'00049432-ef9f-4d57-8499-d0e399fe9718', timestamp=u'2017-07-08 19:25:29', url=u'google.com', uid=u'u15')
rddSimple = rddAvro.map(lambda row: [str(c) for c in row])

# pull out hour and url AND userid as key, the value will simply be the number 1
rdd1 = rddSimple.map(lambda row: ((row[-3].split()[1][:2], row[-2], row[-1]), 1) )

# .countByKey(): Count the number of elements for each key, and return the result to the master as a dictionary.
final = rdd1.countByKey()

print('Query 3: get count of unique (by userId) clicks per URL by hour')
for k,v in sorted(final.items()):
    # each key is a tuple of (hour, url, userid)
    print('hour/url/userid combination: {}\tcount of unique (by userId) clicks per URL by hour: {}'.format(
        '/'.join(k), v))

# pause while so I have a chance to checkout Spark UI web page
input("Press ctrl+z to exit")
