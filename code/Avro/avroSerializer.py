
# import our avro libraries
import avro.schema
from avro.datafile import DataFileReader, DataFileWriter
from avro.io import DatumReader, DatumWriter

# set the schema of interest
schema = avro.schema.parse(open("slackSchema.avsc", "rb").read())


# a method to parse the data from Slack's RTM api and serialize it given a single message
def avroSerialize(message):
    """takes as input a message loops through each part of the message, 
    and attempts to serialize it and return the new AVRO serialized message"""
    
    # set up a writer to serialize data
    writer = DatumWriter(schema)
    
    # we set up a try loop because the RTM may return messages
    # that are not actual messages that fit our Avro schema
    try: 
            
        # set up a new converted message
        new_message = {}
        new_message['user_id'] = message['user']
        new_message['record_type'] = message['type']
        new_message['text'] = message['text']
        new_message['channel'] = message['channel']
        new_message['time_stamp'] = message['ts']

        # serialize the message and return it
        return writer.write(new_message)
    
    # if we fail to write successfully, it's probably that we were
    # attempting to write a message that we don't care about, like
    # a status change. if this happens, we'll pass
    except:
        pass