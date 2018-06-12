from pyspark import SparkContext
from pyspark.sql import SQLContext

from pyspark.sql.types import StructType
from pyspark.sql.types import StructField
from pyspark.sql.types import StringType
from pyspark.sql.types import IntegerType
from pyspark.sql.functions import lit

#Query 3: get count of unique (by userId) clicks per URL by hour
sc = SparkContext("local", "P7 Query 3 to mongodb")
sqlContext = SQLContext(sc)

#rdd = sc.textFile('file:///home/cloudera/projects/e88/A5/p1_input/')
# makes more sense to use the 20 userid events vs. those from problem 1
rdd = sc.textFile('file:///home/cloudera/projects/e88/A5/p2_input/')

# split on tab character
rdd1 = (rdd.map(lambda x: x.split('\t'))
    # pull out hour and url AND userid as key, the value will simply be the number 1
    .map(lambda row: ((row[-3].split()[1][:2], row[-2], row[-1]), 1) )
    )

# ORIG P1, turned it into a dictionary
# .countByKey(): Count the number of elements for each key, and return the result to the master as a dictionary.
# rdd2 = rdd1.countByKey() #.map(lambda row: ('{}/{}/{}'.format(row[0][0], row[0][1], row[0][2]),    row[1] ))

# rewrite above for problem 7, want to keep as an rdd, for writing to mongo as such
from operator import add
# format the tuple key (hour, url, userID) as a single string column
rdd2 = rdd1.reduceByKey(add).sortByKey().map(lambda row: ('{}/{}/{}'.format(row[0][0], row[0][1], row[0][2]), row[1] ))

# specify a schema, in order to convert into a Dataframe, couldn't find a straightforward way of writing rdd to mongo using mongo-spark connector
schema = StructType([StructField('hour_url_userid', StringType(), True), StructField('count', IntegerType(), True)])

df = sqlContext.createDataFrame(rdd2, schema)
# add marker for query 3
df = df.withColumn("query", lit(3))
df.write.format("com.mongodb.spark.sql").mode("append").save()

# for p7, do the collect() as a separate step, will only be used for display in hte console
final = rdd2.collect()

print('Query 3: get count of unique (by userId) clicks per URL by hour')
# reqrite for problem 7 to iterate through collect()'d list instead of dictionary
for hour_url_userid, count in final:
    # each key is a tuple of (hour, url, userid)
    print('hour/url/userid combination: {}\tcount of unique (by userId) clicks per URL by hour: {}'.format(
        hour_url_userid, count))
