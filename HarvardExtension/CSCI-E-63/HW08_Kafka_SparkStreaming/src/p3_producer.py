from kafka import KafkaProducer
from random import randint
from datetime import datetime
import time

producer = KafkaProducer(bootstrap_servers='localhost:9092')

print 'Initiating random numbers '

while True:
    msg = str(randint(1,10))
    print b'{0} - Random number created by P3 PRODUCER: {1}'.format(datetime.now().strftime('%H:%M:%S:%f'), msg)
    producer.send('Lec08_P03_topic1', msg )
    
    time.sleep(1)



