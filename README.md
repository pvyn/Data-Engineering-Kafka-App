# Data-Engineer-Challenge

## How to build and run the code on Linux or OS X
Run the following commands in a CLI (command line interface).

Requirements: Kafka and Python are already installed.

1. Run zookeeper via

    `zookeeper-server-start.bat config\zookeeper.properties`
    
2. Run a kafka broker via

    `kafka-server-start.bat config\server.properties`
    
3. Open a terminal window and create a topic via following command

    `kafka-topics.bat --zookeeper localhost:2181 --topic doodle_challenge_sample --create --partitions 1 --replication-factor 1`
    
4. Enter the provided sample data 

    `gzcat stream.gz | kafka-console-producer.bat --broker-list localhost:9092 --topic doodle_challenge_sample`
    
5. Go to the location of the doodle_app.py script with the cd command and run the script. (This requires that the following packages have been installed via pip install: datetime, kafka-python)
    

## Report: what was done
Firstly, the packages that will be used in the script are imported. Then in a first step the KafkaConsumer is set up. The arguments it takes are:
- 'doodle_challenge_sample': the name of the topic
- bootstrap_servers = ['localhost:9092']: The location of the kafka broker
- auto_offset_reset = 'earliest': consumer starts reading at the latest committed offset
- enable_auto_commit = True: offset is committed every interval
- auto_commit_interval_ms = 1000ms: interval between two commits
- group_id = 'user-counter': the consumer group to which the consumer belongs
- consumer_timeout_ms = 5000: after 5 seconds the message iterator is ended
- value_deserializer = json_deserializer: The json_deserializer is a function created to turn the messages arriving from kafka from byte to string with the .decode('utf-8') method.

Subsequently, the KafkaProducer is set up. The arguments it takes are:
- bootstrap_servers = ['localhost:9092']: The location of the kafka broker
- value_serializer = json_serializer: The json_serializer is a function created to turn the messages sent to kafka from string to byte with the .encode('utf-8') method.

### Looping through the messages and the counting mechanism:
- We loop through every message that the consumer finds. This will be where the offset is currently at. After doing the initial load of the data the offset will be at 0.
- A `counter` variable counts through every iteration and shows in the end, how many messages from kafka have been processed.

First iteration (`counter` = 1):
- In the first iteration the `timestamp` variable is set. This is done by converting the unixtime out of the kafka message into '%Y-%m-%d %H:%M' format.
- A dictionary by the variable name `subdict_per_min` is created that saves the `uid` and `ts` out of the first message.
- A list by the variable name `sublist_per_min` is created that adds the `subdict_per_min` dictionary.

Second iteration (`counter` = 2): 
- (Assumption is that the `ts` of the second message is in the same minute as the first message.)
- The dictionary `subdict_per_min` is updated to the current `uid` and `ts` of the second message.
- The dictionary `subdict_per_min` is added to the list `sublist_per_min`.

Iteration number x, the message where the `ts` from the message jumps to the next minute:
- We enter the else case on line 53. We loop through the `sublist_per_min` list, that contains all the dictionaries with the `uid` and `ts` of all the previous messages. The `uid` of those are added to a set with the variable name `unique_uids`. By being a set, the duplicates are filtered out automatically.
- On line 58, the number of unique users from the set and the corresponding minute in time is printed to stdout.
- On line 59, the same information that is sent to stdout is sent to the KafkaProducer as a dictionary. Simultaneously a new topic is created that receives these results 'doodle_challenge_sample_results'.
- Since the jump to the next minute has occured, the `timestamp` variable is overwritten with the new minute, the `unique_uids` set is cleared and the `sublist_per_min` list is cleared. Then the `subdict_per_min` with the current `uid` and `ts` is added to the `sublist_per_min`.

Last iteration:
- All the messages are processed and a timeout occurs after 5 seconds. The loop has ended.

### Performance indicator
Before the iteration through all the messages starts, on line 43, we save the current time in a variable named `start`. After the loop the time is saved in a variable named `end`. By subtracting `start` from `end` the total amout of seconds the program has run is computed, this is saved in `timedelta_seconds`. Simply by dividing the number of processed messages, which was saved in the `counter` variable by the seconds saved in `timedelta_seconds`, we receive a simple performance indicator: the number of messages processed in a second.

### Notes on the solution
The solution and loop proposed would only work as long as messages are received in order, i.e. the timestamp is ordered. Due to time constraints I left the solution at that but I will explain my thoughts how the solution could be improved below in the Additional Questions section.

### Results
There were 1'000'000 messages in the sample data set. The program took 91 seconds to run. 10989 messages were processed per second

Number of unique users per minute:
- For minute 2016-07-11 13:39 there were 16193 unique users
- For minute 2016-07-11 13:40 there were 41130 unique users
- For minute 2016-07-11 13:41 there were 47369 unique users
- For minute 2016-07-11 13:42 there were 49488 unique users
- For minute 2016-07-11 13:43 there were 47863 unique users
- For minute 2016-07-11 13:44 there were 40439 unique users
- For minute 2016-07-11 13:45 there were 42859 unique users
- For minute 2016-07-11 13:46 there were 47312 unique users
- For minute 2016-07-11 13:47 there were 48180 unique users
- For minute 2016-07-11 13:48 there were 47981 unique users
- For minute 2016-07-11 13:49 there were 42194 unique users
- For minute 2016-07-11 13:50 there were 45070 unique users
- For minute 2016-07-11 13:51 there were 43659 unique users
- For minute 2016-07-11 13:52 there were 48611 unique users
- For minute 2016-07-11 13:53 there were 42742 unique users
- For minute 2016-07-11 13:54 there were 51930 unique users
- For minute 2016-07-11 13:55 there were 45471 unique users

## Additional Questions



