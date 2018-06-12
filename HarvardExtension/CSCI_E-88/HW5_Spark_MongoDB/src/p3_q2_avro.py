from pyspark import SparkContext
from pyspark.sql import SQLContext

sc = SparkContext("local", "P3 Query 2")
sqlContext = SQLContext(sc)
#Query 2: get count of unique visitors per URL by hour

avro_url = 's3://owengnet-data/e88/A5/DatasetAvro'
# read in the avro file, as RDD, use distinct() to de-dupe
rddAvro =  sqlContext.read.format("com.databricks.spark.avro").load(avro_url).rdd.distinct()

# take list of Row objects, like below, and simplify to strings so remaining code runs as-is
# rddAvro: Row(uuid=u'00049432-ef9f-4d57-8499-d0e399fe9718', timestamp=u'2017-07-08 19:25:29', url=u'google.com', uid=u'u15')
rddSimple = rddAvro.map(lambda row: [str(c) for c in row])

rdd1 = (
    # pull out hour and url as key, playing w/slightly different slicing vs. query1, reutrn userid as value
    rddSimple.map(lambda row: ((row[-3].split()[1][:2], row[-2]), row[-1]))
    # groupBy the key = hour+url combo, value becomes iterable of userids
    .groupByKey()
    # like query 1, but now getting the number of unique userids for each hour+url combo
    .map(lambda row: (row[0], len(set(row[1]))))
    )

# pull out all the results, sorting by the hour value
final = rdd1.sortByKey().collect()

print('Problem 3, Query 2: get count of unique visitors per URL by hour')
for (hour_url, count) in final:
    print('hour/url combination: {}/{}\tcount of unique visitors per URL unique urls: {}'.format(
        hour_url[0], hour_url[1], count))

# pause while so I have a chance to checkout Spark UI web page
input("Press ctrl+z to exit")
