
import boto3
from chalicelib.projectHelpers import validateProject, completeProject
from chalicelib.dictHelpers import makeNormalDict, makeLowLevelDict

from chalice import Response

client = boto3.client('dynamodb')

##############################
# get details for all projects
def handleGetAllProjects():
    # get data from dynamoDB
    response = client.scan(
        TableName='projects'
    )
    # deserialize the dynamoDB results to simplify for the user 
    response['Items'] = [makeNormalDict(item) for item in response['Items']]
    return {'data': response}

############################################
# get details for a specific project by name
def handleGetProject(project):
    # get data from dynamoDB
    response = client.get_item(
        TableName='projects',
        Key={'projectName': {'S': project}}
    )
    if 'Item' not in response:
        return Response(body={'Error': 'Unknown projectName'}, status_code=404)
    # deserialize the dynamoDB results to simplify for the user 
    response['Item'] = makeNormalDict(response['Item'])
    return {'data': response}

####################
# post a new project
def handleCreateProject(body):
    response = {}
    if 'projects' not in body or len(body['projects']) < 1:
        return Response(body={'Error': 'Request must include a list of projects'}, status_code=400)     
    if len(body['projects']) > 25: 
        return Response(body={'Error': 'Request cannot include more than 25 projects'}, status_code=400)        
    if len(body['projects']) > 1:
        projects = []
        for project in body['projects']:
            valProject = validateProject(project, True)
            if 'Error' in valProject: return Response(body={'Error': valProject['Error']}, status_code=400)   
            valProject = makeLowLevelDict(completeProject(valProject))
            projects.append(valProject)
        requests = list(map(lambda x: {'PutRequest': {'Item': x}}, projects))
        response = client.batch_write_item(RequestItems={'projects': requests})
    else:
        # treat this case specially b/c put_item will retry failed puts, allows anti-overwrite
        project = completeProject(validateProject(body['projects'][0], True))
        if 'Error' in project: return Response(body={'Error': project['Error']}, status_code=400)  
        response = client.put_item(
            TableName='projects',
            Item=makeLowLevelDict(project),
            ConditionExpression='attribute_not_exists(projectName)',
        )
    # use Response to change status code to 201 from default 200    
    return Response(
        # no need to deserialize, as only metadata is returned
        body={'data': response},
        status_code=201,
        headers={'Content-Type': 'application/json'}
    )

#############################################
# update a project's details (by projectName)
def handleUpdateProject(project, body):
    # user should not include a projectName, especially different one from project!
    if 'projectName' in body:
        if body['projectName'] != project:
            return Response(body={'Error': 'A projectName cannot be changed'}, status_code=403)              
        else:
            del body['projectName']
    # if there are no keys left in project, reject request
    if len(body.keys()) == 0:
        return Response(body={'Error': 'Request must include a valid update'}, status_code=400)          
    # check if the project has valid properties / values
    valProject = validateProject(body, False)
    if 'Error' in valProject: return Response(body=valProject, status_code=400)        
    valProject = makeLowLevelDict(valProject)
    # set up some storage to help with the dynamoDB operation
    updates = []
    expAttValues = {}
    # form update expression for dynamoDB operation
    updateExpr = 'SET '
    for key in valProject:
        updates.append(key + ' = :' + key)
        expAttValues[':' + key] = valProject[key]
    updateExpr += (', ').join(updates)
    # get data from dynamoDB
    response = client.update_item(
        TableName='projects',
        Key={'projectName': {'S': project}},
        ReturnValues='UPDATED_NEW',
        ReturnConsumedCapacity='NONE',
        ReturnItemCollectionMetrics='SIZE',
        UpdateExpression=updateExpr,
        ExpressionAttributeValues=expAttValues
    )
    # deserialize the dynamoDB results to simplify for the user 
    response['Attributes'] = makeNormalDict(response['Attributes'])
    return response

#######################################
# assign one or more nodes to a project
def handleAddProjectNode(project, body):
    if 'nodeIDs' not in body or len(body['nodeIDs']) < 1:
        return Response(body={'Error': 'POST request must include a list of nodeIDs.'}, status_code=400)        
    response = client.update_item(
        TableName='projects',
        Key={'projectName': {'S': project}},
        ReturnValues='UPDATED_NEW',
        UpdateExpression='ADD assignedNodes :nodeIDs',
        ExpressionAttributeValues={':nodeIDs': {'SS': body['nodeIDs']}}
    )
    # deserialize the dynamoDB results to simplify for the user 
    response['Attributes'] = makeNormalDict(response['Attributes'])
    return {'data': response}

###########################################
# unassign one or more nodes from a project
def handleRemoveProjectNode(project, body):
    if 'nodeIDs' not in body or len(body['nodeIDs']) < 1:
        return Response(body={'Error': 'DELETE request must include a list of nodeIDs.'}, status_code=400)  
    response = client.update_item(
        TableName='projects',
        Key={'projectName': {'S': project}},
        ReturnValues='UPDATED_NEW',
        UpdateExpression='DELETE assignedNodes :nodeIDs',
        ExpressionAttributeValues={':nodeIDs': {'SS': body['nodeIDs']}}
    )
    # deserialize the dynamoDB results to simplify for the user 
    response['Attributes'] = makeNormalDict(response['Attributes'])
    return {'data': response}
