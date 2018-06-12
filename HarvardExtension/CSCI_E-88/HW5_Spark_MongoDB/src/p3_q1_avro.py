from pyspark import SparkContext
from pyspark.sql import SQLContext

sc = SparkContext("local", "P3 Query 1")
sqlContext = SQLContext(sc)
# Query 1: get count of unique URLs by hour

#Modify your Problem 2 Spark jobs to read input data in the Avro format, de-dupe the events and give answers to the same 3 queries

avro_url = 's3://owengnet-data/e88/A5/DatasetAvro'
# read the avro data using databricks library, turn into rdd and use .distinct() to de-dupe
rddAvro =  sqlContext.read.format("com.databricks.spark.avro").load(avro_url).rdd.distinct()

# take list of Row objects, like below, and simplify to strings so p1 code runs as-is
# rddAvro: Row(uuid=u'00049432-ef9f-4d57-8499-d0e399fe9718', timestamp=u'2017-07-08 19:25:29', url=u'google.com', uid=u'u15')
rddSimple = rddAvro.map(lambda row: [str(c) for c in row])

rdd1 = (
        # pull out only the two characters representing the hour, along with the 2nd field, i.e. the url
        # use negative indexing on the initial column selection so that same code will work when there are
        # additional columns pre-pended, i.e. when UUID is first column in problem 2
        rddSimple.map(lambda row: (row[-3][11:13], row[-2]))
        # group by the key, i.e. the hour value, making the value an iterable of urls
        .groupByKey()
        # pull out the hour value, apply set on the iterable to remove dups, and return length of that set as value
        .map(lambda row: (row[0], len(set(row[1]))))
    )
# pull out all the results, sorting by the hour value
final = rdd1.sortByKey().collect()

print('P3 Query 1: get count of unique URLs by hour')
for (hour, count) in final:
    print('- hour: {}\tcount unique urls: {}'.format(hour, count))

# pause while so I have a chance to checkout Spark UI web page
input("Press ctrl+z to exit")
