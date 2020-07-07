from kafka import KafkaConsumer, KafkaProducer
from datetime import datetime, timedelta
from json import loads, dumps, decoder, encoder

def json_deserializer(m):
    try:
        return loads(m.decode('utf-8'))
    except decoder.JSONDecodeError:
        print(f'Unable to decode: {m}')
        return None
    except:
        print('Error in json_deserializer')
        return None

def json_serializer(m):
    try:
        return dumps(m).encode('utf-8')
    except:
        print('Error in json_serializer')
        return None

def time_converter(m):
    return datetime.utcfromtimestamp(int(m['ts'])).strftime('%Y-%m-%d %H:%M')

consumer = KafkaConsumer(
    'doodle_challenge_sample',
     bootstrap_servers=['localhost:9092'],
     auto_offset_reset='earliest',
     enable_auto_commit=True,
     group_id='user-counter',
     value_deserializer=json_deserializer,
     consumer_timeout_ms=5000 #maximum latency of 5 seconds
     )

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=json_serializer)

counter = 0
sublist_per_min = []
unique_uids = set()

start = datetime.now()

for message in consumer:
    counter += 1
    message = message.value
    if counter == 1:
        timestamp = time_converter(message)
    subdict_per_min = {'uid':message['uid'], 'ts':timestamp}
    if timestamp == time_converter(message):
        sublist_per_min += [subdict_per_min]
    else:
        for dict_id_ts in sublist_per_min:
            for key,val in dict_id_ts.items():
                if key == 'ts':
                    unique_uids.add(dict_id_ts['uid'])
        print(f'For minute {val} there were {len(unique_uids)} unique users')
        producer.send('doodle_challenge_sample_results',value={"minute":val, "unique_uid": len(unique_uids)})
        timestamp = time_converter(message)
        unique_uids = set()
        sublist_per_min = []
        sublist_per_min += [subdict_per_min]

end = datetime.now()
timedelta_seconds = round((end-start).total_seconds())
messages_per_second = counter/(timedelta_seconds-5) #subtract timeout of 5s

print(f'There were {counter} messages in the set')
print(f'The program took {timedelta_seconds-5} seconds to run')
print(f'{round(messages_per_second)} messages were processed per second')
