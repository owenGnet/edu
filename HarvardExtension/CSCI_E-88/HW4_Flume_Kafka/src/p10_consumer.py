#!/usr/bin/env python
import time
import collections

from kafka import KafkaConsumer

def main():

    #auto_offset_reset = 'earliest',
    c = KafkaConsumer(
        bootstrap_servers='localhost:9092',
        group_id='p10consumer')
    # will create topic if it doesn't already exist
    c.subscribe(['problem10', 'problem10a', 'problem10b'])

    topic_10_partitions = []

    while True:
        for msg in c:
            if msg.topic == 'problem10':
                key_value = None if msg.key is None else msg.key.decode()
                info = '''
        message received
            - partition number: {}
            - event key: {}
            - event body: {}'''.format(msg.partition, key_value, msg.value.decode())
                print(info)
                topic_10_partitions.append(msg.partition)
            else:
                # presumably topic = problem10a, give a summary on partition distrbution, since script started
                for k, v in collections.Counter(topic_10_partitions).items():
                    print('partition: {}, count: {}, pct total: {:.0f}%'.format(k, v, v/len(topic_10_partitions) * 100))

        # sleep for 1/10th of a second before looping again
        time.sleep(0.1)


if __name__ == "__main__":

    main()