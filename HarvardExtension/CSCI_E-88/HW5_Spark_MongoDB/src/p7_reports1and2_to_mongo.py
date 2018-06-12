from pyspark import SparkContext
from pyspark.sql import SQLContext

from pyspark.sql.types import StructType
from pyspark.sql.types import StructField
from pyspark.sql.types import StringType
from pyspark.sql.types import IntegerType

#Report 1: Daily count of unique URLs
sc = SparkContext("local", "P7 Report 1/2 data to mongodb")
sqlContext = SQLContext(sc)

#rdd = sc.textFile('file:///home/cloudera/projects/e88/A5/p1_input/')
# makes more sense to use the 20 userid events vs. those from problem 1
rdd = sc.textFile('file:///home/cloudera/projects/e88/A5/p2_input/')

# split on tab character
rdd1 = (rdd.map(lambda x: x.split('\t'))
    # pull out day, url, userID, use negative indexing so it works on source files from either P1 or P2
    .map(lambda row: (row[-3][:10], row[-2], row[-1]))
    )

# specify a schema, in order to convert into a Dataframe, couldn't find a straightforward way of writing rdd to mongo using mongo-spark connector
schema = StructType([StructField('day', StringType(), True),
                     StructField('url', StringType(), True),
                     StructField('userID', StringType(), True)])

df = sqlContext.createDataFrame(rdd1, schema)
# replace anything present in the collection with new data
df.write.format("com.mongodb.spark.sql").mode("overwrite").save()

print('REPORT 1/2 INGESTION COMPLETE')
