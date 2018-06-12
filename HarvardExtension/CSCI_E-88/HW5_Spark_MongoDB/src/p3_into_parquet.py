
# Write a Spark job that reads DatasetAvro, de-dupes this data and # writes it back to S3  but in a Parquet format.
#  Call it DatasetParquet
from pyspark import SparkContext
from pyspark.sql import SQLContext


sc = SparkContext("local", "to parquet")
sqlContext = SQLContext(sc)

folder_url = 's3://owengnet-data/e88/A5/'
avro_url = folder_url + 'DatasetAvro'
# read in the avro file, as RDD, use distinct() to de-dupe
rddAvro =  sqlContext.read.format("com.databricks.spark.avro").load(avro_url).rdd.distinct()

print('COUNT IN rddAvro post de-dupe:', rddAvro.count())
parquet_url = folder_url + 'DatasetParquet'
# write dataframe to S3, as parquet, need to turn into dataframe first
df = rddAvro.toDF().write.parquet(parquet_url)


