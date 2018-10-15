# kafka-demo
This repository captures a kafka demo and scripts to:
1) Generate an avro schema and register it in the schema registry
2) Generate some data and write to a kafka topic as a producer
3) Consume the data from the kafka topic as a consumer
4) Consume the data as a batch from the kafka topic as a spark batch job
5) Stream the data from the kafka topic using spark streaming

## Libraries
This demo is going to depend on the confluent kafka python libraries.  They are the fastest and best supported of the available python libraries at this time and instructions for installation and dependencies can be found [here](
https://github.com/confluentinc/confluent-kafka-python)

### Installing the confluent kafka libs:
```bash
$ pip install confluent-kafka
$ pip install confluent-kafka[avro]
```


