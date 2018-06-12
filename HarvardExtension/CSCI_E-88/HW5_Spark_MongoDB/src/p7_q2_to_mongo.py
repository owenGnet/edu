from pyspark import SparkContext
from pyspark.sql import SQLContext

from pyspark.sql.types import StructType
from pyspark.sql.types import StructField
from pyspark.sql.types import StringType
from pyspark.sql.types import IntegerType
from pyspark.sql.functions import lit

#Query 2: get count of unique visitors per URL by hour
sc = SparkContext("local", "P7 Query 2 to mongodb")
sqlContext = SQLContext(sc)

#rdd = sc.textFile('file:///home/cloudera/projects/e88/A5/p1_input/')
# makes more sense to use the 20 userid events vs. those from problem 1
rdd = sc.textFile('file:///home/cloudera/projects/e88/A5/p2_input/')

rdd1 = (rdd.map(lambda x: x.split('\t'))
    # pull out hour and url as key, playing w/slightly different slicing vs. query1, reutrn userid as value
    .map(lambda row: ((row[-3].split()[1][:2], row[-2]), row[-1]))
    # groupBy the key = hour+url combo, value becomes iterable of userids
    .groupByKey()
    # like query 1, but now getting the number of unique userids for each hour+url combo
    .map(lambda row: (row[0], len(set(row[1]))))
    )

# pull out all the results, sorting by the hour/url value, format the tuple key as a single string column
rdd2 = rdd1.sortByKey().map(lambda row: ('{}/{}'.format(row[0][0], row[0][1]),    row[1] ))

# specify a schema, in order to convert into a Dataframe, couldn't find a straightforward way of writing rdd to mongo using mongo-spark connector
schema = StructType([StructField('hour_url', StringType(), True), StructField('count', IntegerType(), True)])

df = sqlContext.createDataFrame(rdd2, schema)
# add marker for query 2
df = df.withColumn("query", lit(2))
df.write.format("com.mongodb.spark.sql").mode("append").save()

# for p7, do the collect() as a separate step, will only be used for display in hte console
final = rdd2.collect()


print('Query 2: get count of unique visitors per URL by hour')
for (hour_url, count) in final:
    print('hour/url combination: {}\tcount of unique visitors per URL unique urls: {}'.format(
        hour_url, count))
        #hour_url[0], hour_url[1], count))


