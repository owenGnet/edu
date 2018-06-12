# 	2. Write a Spark Job to read the input data (both Dataset1 and Dataset2 you generated for Problem 2)
# from S3 and convert it to Avro format (DatasetAvro) and write the results back into S3 in a different folder.

from pyspark import SparkContext
from pyspark.sql import SQLContext

from pyspark.sql.types import StructType
from pyspark.sql.types import StructField
from pyspark.sql.types import StringType

sc = SparkContext("local", "to avro")
sqlContext = SQLContext(sc)

# keep format necessary for local testing for now
# read_url_base = 's3n://{AWS_ID}:{AWS_KEY}@owengnet-data/e88/A4/'.format(AWS_ID=AWS_ID, AWS_KEY=AWS_KEY)
read_url_base = 's3://owengnet-data/e88/A4/'
rddA = sc.textFile('{}Dataset1'.format(read_url_base))
rddB = sc.textFile('{}Dataset2'.format(read_url_base))

# concatenate the two RDDs
rdd = sc.union([rddA, rddB]).map(lambda x: x.split('\t'))

# create a schema consisting of all strings
schema = StructType([StructField('uuid', StringType(), True), StructField('timestamp', StringType(), True),
    StructField('url', StringType(), True), StructField('uid', StringType(), True)])

# I was only able to find a way of converting to avro that involved dataframe
df = sqlContext.createDataFrame(rdd, schema)

save_url = 's3://owengnet-data/e88/A5/DatasetAvro'
# save outptut as avro using the databricks library, available since it was passed to spark-submit
# using the --packages argument, overwrite if it already exists on S3
df.write.format("com.databricks.spark.avro").mode('overwrite').save(save_url)
