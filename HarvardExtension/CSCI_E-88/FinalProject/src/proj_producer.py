import argparse
import time
import datetime

import pandas as pd
from kafka import KafkaConsumer, KafkaProducer



def send_events(topic_name, batch_count, start_at, stop_at, is_debug):

    print('loading csv ...')
    data = pd.read_csv('/mnt/share/e88/creditcard.csv', sep=',')
    producer = KafkaProducer(bootstrap_servers='localhost:9092')

    for i in range(start_at, stop_at, batch_count):
        batch = data[i:i + batch_count]
        json_events = batch.to_json(orient='records')
        if is_debug:
            print(json_events)
        producer.send(topic_name, str.encode(json_events))
        print(i, i+batch_count, len(batch))
        print('-' * 44)

        #time.sleep(1)

    producer.flush()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Send json events to Kafka')
    parser.add_argument('-t', '--topic', type=str)
    parser.add_argument('-b', '--batch-count', type=int, default=5)
    parser.add_argument('-s', '--start-at', type=int, default=0)
    parser.add_argument('-e', '--end-at', type=int, default=30)
    parser.add_argument('-d', '--debug', type=bool, default=False)
    args = parser.parse_args()
    
    print('BEGIN TEST, topic: {},  batch-count: {}, start-at: {},  end-at: {}, debug: {}'.format(
        args.topic, args.batch_count,args.start_at,  args.end_at, args.debug))
    print('sending first batch at {}'.format(datetime.datetime.now()))
    send_events(args.topic, args.batch_count, args.start_at, args.end_at, args.debug)