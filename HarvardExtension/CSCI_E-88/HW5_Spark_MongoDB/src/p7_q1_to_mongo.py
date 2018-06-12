from pyspark import SparkContext
from pyspark.sql import SQLContext

from pyspark.sql.types import StructType
from pyspark.sql.types import StructField
from pyspark.sql.types import StringType
from pyspark.sql.types import IntegerType
from pyspark.sql.functions import lit

# Query 1: get count of unique URLs by hour
sc = SparkContext("local", "P7 Query 1 to mongodb")
sqlContext = SQLContext(sc)

#rdd = sc.textFile('file:///home/cloudera/projects/e88/A5/p1_input/')
# makes more sense to use the 20 userid events vs. those from problem 1
rdd = sc.textFile('file:///home/cloudera/projects/e88/A5/p2_input/')

# split on tab character
rdd1 = (rdd.map(lambda x: x.split('\t'))
        # pull out only the two characters representing the hour, along with the 2nd field, i.e. the url
        # use negative indexing on the initial column selection so that same code will work when there are
        # additional columns pre-pended, i.e. when UUID is first column in problem 2
        .map(lambda row: (row[-3][11:13], row[-2]))
        # group by the key, i.e. the hour value, making the value an iterable of urls
        .groupByKey()
        # pull out the hour value, apply set on the iterable to remove dups, and return length of that set as value
        .map(lambda row: (row[0], len(set(row[1]))))
    )

# pull out all the results, sorting by the hour value
rdd2 = rdd1.sortByKey()

# specify a schema, in order to convert into a Dataframe, couldn't find a straightforward way of writing rdd to mongo using mongo-spark connector
schema = StructType([StructField('hour_of_day', StringType(), True),
                     StructField('count', IntegerType(), True)])

df = sqlContext.createDataFrame(rdd2, schema)
# add marker for query 1
df = df.withColumn("query", lit(1))
df.write.format("com.mongodb.spark.sql").mode("overwrite").save()

# for p7, do the collect() as a separate step, will only be used for display in hte console
final = rdd2.collect()

print('Query 1: get count of unique URLs by hour')
for (hour, count) in final:
    print('- hour: {}\tcount unique urls: {}'.format(hour, count))
