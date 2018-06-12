from pyspark import SparkContext
from pyspark.sql import SQLContext
from pyspark.sql.types import TimestampType

sc = SparkContext("local", "P8 data to mariadb")
sqlContext = SQLContext(sc)

rdd = sc.textFile('file:///home/cloudera/projects/e88/A5/p2_input/')
rdd = rdd.map(lambda x: x.split('\t'))
# this time convert straight to Dataframe, default will be all string types I think
df = rdd.toDF(['uuid','event_time','url','userid'])
# best case would bet to replace the string version of the timestamp with a true timestamp data type via cast
# BUT my timestamp strings with hour=24 will be NULL'd via the below cast, due to Spark's inability to handle
#     Martian timestamps - I'll need to do a PR on that after the class has finished.
# In meantime, will need to pass the full string in as-is and do hour manipulation via SQL
# df = df.withColumn("event_time", df['event_time'].cast(TimestampType()))
# no need for uuid in any of the calcs
df = df.drop('uuid')

# mariadb driver doesn't work with modern spark apparenlty, but still need to use mariadb port of course
url = 'jdbc:mysql://localhost:3306/test'
properties = {'user': 'root'}
df.write.jdbc(url=url, table='problem8_str', mode='overwrite', properties=properties)

print('PROBLEM 8 INGESTION COMPLETE')
