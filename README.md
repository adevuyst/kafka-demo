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

## Avro and Why
[Avro](https://avro.apache.org/) is a data serialization system that provide a compact, fast, binary data format that can be sent over the wire. It enables schema evolution without many of the draw backs of other formats (csv, json, xml).  While many example for kafka have been done sending messages composed of strings, json and csv data, to make this closer to a real world application we are going to use avro as it's much more robust for non-trivial use cases.

## Schema Registry
In an effort to coordinate evolving schema versions, to protect against malformed messages, and manage change, enter the schema registry.  This mechanism helps avoid several problems that would arise in the past:
* Required changes to serializers and deserializers otherwise no new data could be processed
* Required changes to producers and consumers otherwise no new data could be processed
* Old messages could no longer be processed by anyone that was upgraded to the new schema
* New messages could not be processed by producers or consumers that were not updated
The schema registry is provided as part of the confluent platform and more information on it can be found [here](https://docs.confluent.io/current/schema-registry/docs/index.html)
For our purposes we are going to generate an avro schema, upload that schema to the registry and then begin producing and consuming data. Evolving the schema to a new version will be handled potentially in a future entry.

## Creating an Avro Schema File
Avro schemas are defined in json files and for schema definition purposes they tend to end in .avsc, but otherwise I am not aware of any naming conventions for files.  Kafka used to reason about the world in terms of messages and offsets.  This has evolved to be in terms of keys and values you may want to define a schema for both.

We are going to create a schema file: ```click_v1.avsc```

To keep things simple we will only be defining a schema for the value:
```json
{
     "type": "record",
     "namespace": "com.example",
     "name": "click",
     "version": 1,
     "fields": [
       { "name": "id", "type": "string" },
       { "name": "impression_id", "type": "string" },
       { "name": "creative_id", "type": "string" },
       { "name": "placement_id", "type": "string" },
       { "name": "timestamp", "type": 
          { "type": "long", "logicalType": "timestamp-millis" } 
       },
       { "name": "user_agent", "type": ["string", "null"] },
       { "name": "ip", "type": ["string", "null"] },
       { "name": "referrer", "type": ["string", "null"] },
       { "name": "cost", "type": "float" },
     ]
}
```

## Adding a Schema to the Schema Registry
### Schema Naming Conventions
Topics names in Kafka should follow this convention ```{subject}-{format}```, where subject would be something like ```clicks``` and the format would indicate what data format the data is in, so avro, protobuf, json, etc.  For our purposes we are going to be using avro, so our topic would be ```clicks-avro```.  Correspondingly, schemas also have a naming convention.  The convetion for schemas is ```{topic}-{key|value}```.  Based on our ```clicks-avro``` and the fact we are only providing a schema for values our schema name will be ```clicks-avro-value```.
### The RESTful Schema Registry API
The schema registry operates a RESTful api that is defined [here](https://docs.confluent.io/current/schema-registry/docs/api.html).

