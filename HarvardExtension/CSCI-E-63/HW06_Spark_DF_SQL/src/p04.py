
from pyspark import SparkConf, SparkContext, SQLContext, HiveContext

conf = SparkConf().setMaster('local').setAppName('py02') 
sc = SparkContext(conf = conf) 
hc = HiveContext(sc)

query = '''
SELECT o.order_id, COUNT(o.order_id) as NumItemsInOrder
FROM order_items i
INNER JOIN orders o ON o.order_id = i.order_item_order_id
GROUP BY o.order_id
ORDER BY COUNT(o.order_id) DESC
LIMIT 10
'''
dfs = hc.sql(query)
dfs.show()