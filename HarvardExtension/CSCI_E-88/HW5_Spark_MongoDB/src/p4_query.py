#Write a new Spark job that loads both DatasetParquet and DatasetCommunity
#query: get counts of clicks per URL per communityID

from pyspark import SparkContext
from pyspark.sql import SQLContext

sc = SparkContext("local", "P5 Query")
sqlContext = SQLContext(sc)

# might as well load the DatasetCommunity from local path, where it was written
rddA = sc.textFile('file:///home/cloudera/projects/e88/A5/p4_input/DatasetCommunity').map(lambda x: x.split('\t'))

# now load DatasetParquet from s3
folder_url = 's3://owengnet-data/e88/A5/'
parquet_url = folder_url + 'DatasetParquet'
# read the DatasetParquet, cast as RDD, that data has been de-duped already
rddB = sqlContext.read.parquet(parquet_url).rdd

# pull out the last column (userid) as key and 2nd to last (urls) as value from the ParquetDataset
rdd_1 = (
        rddB.map(lambda row: (row[-1], row[-2]))
        # perform left outer join, matching the key from base rdd (userid) on the same in DatasetCommunity
        .leftOuterJoin(rddA)
        # row[1] below points to the tuple, from there pull out communityID (index 1) , url (index 0)
        .map(lambda row: (row[1][1], row[1][0]))
)

# use map and reduceByKey to add up the events/clicks per url per communityID
final = rdd_1.map(lambda x: (x, 1)).reduceByKey(lambda a,b: a+b).collect()

for k, v in sorted(final):
    print('communityID: {}, url: {:>12}  count: {}'.format(k[0], k[1], v))


# pause while so I have a chance to checkout Spark UI web page
input("Press ctrl+z to exit")

