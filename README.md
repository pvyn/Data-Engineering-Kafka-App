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
- bootstrap_servers = ['localhost:9092']: the location of the kafka broker
- auto_offset_reset = 'earliest': consumer starts reading at the latest committed offset
- enable_auto_commit = True: offset is committed every interval
- auto_commit_interval_ms = 1000ms: interval between two commits
- group_id = 'user-counter': the consumer group to which the consumer belongs
- consumer_timeout_ms = 5000: after 5 seconds the message iterator is ended
- value_deserializer = json_deserializer: the json_deserializer is a function created to turn the messages arriving from kafka from byte to string with the .decode('utf-8') method.

Subsequently, the KafkaProducer is set up. The arguments it takes are:
- bootstrap_servers = ['localhost:9092']: the location of the kafka broker
- value_serializer = json_serializer: the json_serializer is a function created to turn the messages sent to kafka from string to byte with the .encode('utf-8') method.

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
The solution and loop proposed would only work as long as messages are received in order, i.e. the timestamp is ordered. Due to time constraints I left the solution at that but I will explain my thoughts on how the solution could be improved below in the Additional Questions section.

### Results and Performance
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

#### When the data was output
Since the messages are ordered in time, the fastest way to output the results was to read all messages from the same minute and as soon as a message from the next minute arrives, compute the number of unique users and print the number to stdout / send it to Kafka via the producer.

#### Error in counting
Again, assuming messages are ordered in time, there should not be an error in counting with the process above.

## Additional Questions

### How scaling would work
In the solution above, there is 1 kafka broker and 1 consumer running, while the topic has 1 partition. The data load could be be balanced across multiple consumers if we had multiple partitions to read from. If we had created 3 partitions for our doodle_challenge_sample topic, there could be 3 consumers that read the data in parallel from those topic partitions. 

If not specified otherwise, the producer will send the data round robin to the three partitions, so messages from the same `ts` minute would not end up in the same partition. Then the solution above would not count correctly. There should be a way to specify a key so that messages with the same `ts` minute would end up in the same partition. 

In general it would make sense to also have multiple brokers running, so that when the broker breaks down, the application would not have to stop. It's a good idea to have at least 3 broker running, so that when one broker breaks down and the other is down for maintenance, there is still one broker working. I.e. the topic should have a replication factor of at least 3.

### How to cope with the app crashing mid day/mid year
Since the results are sent out after the end of every minute, the only issue with the script described above is within the minute that was being processed while the app crashed. It would be best to to have a mechanism that automatically resetts to offset to the first message of the new "minute", so that all of those messages are reprocessed for counting the number of unique users in that minute.

### If events were not strictly ordered
There should be a way to create objects for every `ts` minute that continually gets added unique user ids to it. The result should then not be sent to kafka with the first occurance of the next `ts` minute but the app would wait for a specified time until one can be confident that most of the late messages have arrived and the number of unique users has been counted correctly. The most important factor here, also to insure that results are output the fastest way possible, is to decide when the late messages must have finished arriving for a specific `ts` minute.

### Explanation why json is an ideal format
Json is an industry-standard for api-communication and a light-weight alternative (compared to e.g. xml).
