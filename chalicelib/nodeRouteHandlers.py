
import boto3
from chalicelib.nodeHelpers import validateNode, completeNode
from chalicelib.dictHelpers import makeNormalDict, makeLowLevelDict

from chalice import Response

client = boto3.client('dynamodb')

########################
# get info for all nodes

def handleGetAllNodes():
    # get data from dynamoDB
    response = client.scan(TableName='nodes')
    # deserialize the dynamoDB results to simplify for the user 
    response['Items'] = [makeNormalDict(item) for item in response['Items']]
    return {'data': response}

########################################
# get info for a particular node (by id)

def handleGetNode(node):
    # get data from dynamoDB
    response = client.get_item(TableName='nodes', Key={'nodeID': {'S': node}})
    if 'Item' not in response: return Response(body={'Error': 'Unknown nodeID'}, status_code=404)
    # deserialize the dynamoDB results to simplify for the user 
    response['Item'] = makeNormalDict(response['Item'])
    return {'data': response}

##########################
# create new node or nodes

def handleCreateNode(body):
    response = {}
    # make sure the user included nodes to create
    if 'nodes' not in body or len(body['nodes']) < 1: 
        return Response(body={'Error': 'Request must include a list of nodes'}, status_code=400)
    # creating > 25 nodes isn't supported yet, as it requires more complex interaction with db
    if len(body['nodes']) > 25: 
        return Response(body={'Error': 'Request cannot include more than 25 nodes'}, status_code=400)
    # if the user included multiple nodes, use batch_write_item
    if len(body['nodes']) > 1:
        nodes = []
        for node in body['nodes']:
            valNode = validateNode(node, True)
            if 'Error' in valNode: return Response(body={'Error': valNode['Error']}, status_code=400)
            valNode = makeLowLevelDict(completeNode(valNode))
            nodes.append(valNode)
        requests = list(map(lambda x: {'PutRequest': {'Item': x}}, nodes))
        response = client.batch_write_item(RequestItems={'nodes': requests})
    else:
    #if the user only included one item, use put_item (it retries failed put, allows anti-overwrite)
        node = completeNode(validateNode(body['nodes'][0], True))
        if 'Error' in node: return Response(body={'Error': node['Error']}, status_code=400)
        # send data to dynamoDB
        try:
            response = client.put_item(
                TableName='nodes',
                Item=makeLowLevelDict(node),
                ConditionExpression='attribute_not_exists(nodeID)',
            )
        except:
            return Response(body={'Error': 'NodeID already exists'}, status_code=403)
    # use Response to change status code to 201 from default 200    
    return Response(
        # no need to deserialize, as only metadata is returned
        body={'data': response},
        status_code=201,
        headers={'Content-Type': 'application/json'}
    )

#########################
# update a node's details

def handleUpdateNode(node, body):
    # user should not include nodeID, especially a different one from node!
    if 'nodeID' in body:
        if body['nodeID'] != node:
            return Response(body={'Error': 'A nodeID cannot be changed'}, status_code=403)
        else:
            del body['nodeID']
    # check if the node has valid properties / values
    valNode = validateNode(body, False)
    if 'Error' in valNode: return Response(body=valNode, status_code=400)
    # if there are no keys left in node, reject request
    if len(body.keys()) == 0:
        return Response(body={'Error': 'Request must include a valid update'}, status_code=400)
    valNode = makeLowLevelDict(valNode)
    # set up some storage to help with the dynamoDB operation
    updates = []
    expAttValues = {':nodeID': {'S': node}}
    # form update expression for dynamoDB operation
    updateExpr = 'SET '
    for key in valNode:
        updates.append(key + ' = :' + key)
        expAttValues[':' + key] = valNode[key]
    updateExpr += (', ').join(updates)
    # get data from dynamoDB
    try:
        response = client.update_item(
            TableName='nodes',
            Key={'nodeID': {'S': node}},
            ReturnValues='UPDATED_NEW',
            ReturnConsumedCapacity='NONE',
            ReturnItemCollectionMetrics='SIZE',
            UpdateExpression=updateExpr,
            ConditionExpression='nodeID = :nodeID',
            ExpressionAttributeValues=expAttValues
        )
    except:
        return Response(body={'Error': 'Requested node does not exist'}, status_code=404)
    # deserialize the dynamoDB results to simplify for the user
    if 'Attributes' in response: response['Attributes'] = makeNormalDict(response['Attributes'])
    return response
