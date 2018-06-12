
from pyspark import SparkConf, SparkContext, SQLContext

conf = SparkConf().setMaster('local').setAppName('py03a') 
sc = SparkContext(conf = conf) 
sqc = SQLContext(sc)

#and show that you could exit your pyspark shell and come back in it 
df = sqc.read.parquet('auction_parquet')
df.show(5)

sqc.registerDataFrameAsTable(df, 'auction_p')

print 'Bid history for bidder pagep123'
sqc.sql('''
        SELECT * FROM auction_p
        WHERE bidder = 'pagep123'
        ORDER BY auctionid, bid
          ''').show()


