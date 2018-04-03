
import boto3
from chalicelib.dictHelpers import makeNormalDict

from chalice import Response

client = boto3.client('dynamodb')


#######################
# get a project's nodes

def handleGetProjectNodes(project):
    response = client.query(
        TableName='nodes',
        IndexName='projectName-index',
        KeyConditionExpression='projectName = :projectName',
        ExpressionAttributeValues={':projectName': {'S': project}}
    )
    # deserialize the dynamoDB results to simplify for the user 
    response['Items'] = [makeNormalDict(item) for item in response['Items']]
    return {'data': response}

############################
# assign a node to a project

def handleAddProjectNode(project, body):
    if 'nodeID' not in body:
        return Response(body={'Error': 'Request must include a nodeID'}, status_code=400)
    # send data to dynamoDB, but ensure node isn't already part of another project
    try:
        response = client.update_item(
            TableName='nodes',
            Key={'nodeID': {'S': body['nodeID']}},
            ReturnValues='UPDATED_NEW',
            UpdateExpression='SET projectName=:projectName',
            ConditionExpression='attribute_not_exists(projectName)',
            ExpressionAttributeValues={':projectName': {'S': project}}
        )
    except:
        return Response(body={'Error': 'Node is already assigned to a project'}, status_code=403)        
    # deserialize the dynamoDB results to simplify for the user 
    if 'Attributes' in response: response['Attributes'] = makeNormalDict(response['Attributes'])
    return Response(body={'data': response}, status_code=201)

################################
# unassign a node from a project

def handleRemoveProjectNode(project, body):
    if 'nodeID' not in body:
        return Response(body={'Error': 'Request must include a nodeID'}, status_code=400)
    # send request to dynamoDB
    response = client.update_item(
        TableName='nodes',
        Key={'nodeID': {'S': body['nodeID']}},
        ReturnValues='UPDATED_NEW',
        UpdateExpression='REMOVE projectName'
    )       
    # deserialize the dynamoDB results to simplify for the user 
    if 'Attributes' in response: response['Attributes'] = makeNormalDict(response['Attributes'])
    return Response(body={'data': response}, status_code=201)

