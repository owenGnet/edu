from kafka import KafkaProducer
from random import randint
from datetime import datetime
import time

producer = KafkaProducer(bootstrap_servers='localhost:9092')

print 'Initiating random numbers '

while True:
    msg = str(randint(0,10))
    print '{0} - Random number created by PRODUCER: {1}'.format(datetime.now().strftime('%H:%M:%S:%f'), msg)
    producer.send('Lec08_P02_topic1', msg )
    
    time.sleep(1)

