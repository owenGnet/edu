from kafka import KafkaConsumer
from datetime import datetime

consumer = KafkaConsumer('Lec08_P02_topic1',
                         group_id='p2_group',
                         #auto_offset_reset='earliest',
                         bootstrap_servers=['localhost:9092'])

for message in consumer:
    print '{0} - Random number received by CONSUMER: {1}'.format(datetime.now().strftime('%H:%M:%S:%f'), message.value)
    