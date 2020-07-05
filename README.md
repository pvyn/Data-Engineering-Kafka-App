# Data-Engineer-Challenge

## How to build and run the code on Linux or OS X
Run the following commands in a CLI (command line interface).

Requirements: Kafka and Python are already installed.

1. Run zookeeper via

    `zookeeper-server-start.bat config\zookeeper.properties`
    
2. Run kafka via

    `kafka-server-start.bat config\server.properties`
    
3. Open a terminal window and create a topic via following command

    `kafka-topics.bat --zookeeper localhost:2181 --topic doodle_challenge --create --partitions 1 --replication-factor 1`
    
4. Enter the provided sample data 

    `gzcat stream.gz | kafka-console-producer.bat --broker-list localhost:9092 --topic doodle_challenge`
    
5. Go to the location of the doodle_app.py script with the cd command and run the script. (This requires that the following packages have been installed via pip install: json, datetime, kafka-python)
    

## Report: what was done
Firstly, the packages that will be used in the script are imported. Then in a first step the data is read by creating a KafkaConsumer. The arguments it takes are:
- 'doodle_challenge': the name of the topic
- auto_offset_reset = 'earliest': consumer starts reading at the latest committed offset
- enable_auto_commit = True: offset is committed every interval
- auto_commit_interval_ms = 1000ms: interval between two commits
- group_id = ’consumer-group’: the consumer group to which the consumer belongs

Looping through the messages and the counting mechanism:
- We loop through every message that the consumer finds. This will be where the offset is currently at.
- The messages arriving from kafka are turned from byte to strings with the .decode('utf-8') function.


