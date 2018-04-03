
import boto3
dynamodb = boto3.resource('dynamodb')


# convert from low-level dynamoDB dictionary back to normal python dictionary
deserializer = boto3.dynamodb.types.TypeDeserializer()
def makeNormalDict(lowLevelDict):
    normalDict = {k: deserializer.deserialize(v) for k,v in lowLevelDict.items()}
    if 'assignedNodes' in normalDict:
        # for some reason server errors when returning deserialized string set, so convert
        normalDict['assignedNodes'] = list(normalDict['assignedNodes'])
    return normalDict

# convert from normal python dictionary to low-level dynamoDB dictionary
serializer = boto3.dynamodb.types.TypeSerializer()
def makeLowLevelDict(normalDict):
    return {k: serializer.serialize(v) for k,v in normalDict.items()}
