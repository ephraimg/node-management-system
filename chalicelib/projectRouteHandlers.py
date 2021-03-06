
import boto3
from chalicelib.projectHelpers import validateProject, completeProject
from chalicelib.dictHelpers import makeNormalDict, makeLowLevelDict

from chalice import Response

client = boto3.client('dynamodb')

##############################
# get details for all projects

def handleGetAllProjects():
    # get data from dynamoDB
    response = client.scan(TableName='projects')
    # deserialize the dynamoDB results to simplify for the user 
    response['Items'] = [makeNormalDict(item) for item in response['Items']]
    return {'data': response}

############################################
# get details for a specific project by name

def handleGetProject(project):
    # get data from dynamoDB
    response = client.get_item(TableName='projects', Key={'projectName': {'S': project}})
    if 'Item' not in response:
        return Response(body={'Error': 'Unknown projectName'}, status_code=404)
    # deserialize the dynamoDB results to simplify for the user 
    response['Item'] = makeNormalDict(response['Item'])
    return {'data': response}

####################
# post a new project

def handleCreateProject(body):
    response = {}
    # make sure the user included nodes to create
    if 'projects' not in body or len(body['projects']) < 1:
        return Response(body={'Error': 'Request must include a list of projects'}, status_code=400)     
    # creating > 25 nodes isn't supported yet, as it requires more complex interaction with db
    if len(body['projects']) > 25: 
        return Response(body={'Error': 'Request cannot include more than 25 projects'}, status_code=400)        
    # if the user included multiple nodes, use batch_write_item
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
    #if the user only included one item, use put_item (it retries failed put, allows anti-overwrite)
        project = completeProject(validateProject(body['projects'][0], True))
        if 'Error' in project: return Response(body={'Error': project['Error']}, status_code=400)  
        # send data to dynamoDB
        try:
            response = client.put_item(
                TableName='projects',
                Item=makeLowLevelDict(project),
                ConditionExpression='attribute_not_exists(projectName)'
            )
        except:
            return Response(body={'Error': 'ProjectName already exists'}, status_code=403)
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
    # check if the project has valid properties / values
    valProject = validateProject(body, False)
    if 'Error' in valProject: return Response(body=valProject, status_code=400)        
    # if there are no keys left in project, reject request    
    if len(valProject) < 1:
        return Response(body={'Error': 'Request must include a valid update'}, status_code=400)
    valProject = makeLowLevelDict(valProject)         
    # set up some storage to help with the dynamoDB operation
    updates = []
    expAttValues = {':projectName': {'S': project}}
    # form update expression for dynamoDB operation
    updateExpr = 'SET '
    for key in valProject:
        updates.append(key + ' = :' + key)
        expAttValues[':' + key] = valProject[key]
    updateExpr += (', ').join(updates)
    # get data from dynamoDB
    try:
        response = client.update_item(
            TableName='projects',
            Key={'projectName': {'S': project}},
            ReturnValues='UPDATED_NEW',
            ReturnConsumedCapacity='NONE',
            ReturnItemCollectionMetrics='SIZE',
            UpdateExpression=updateExpr,
            ConditionExpression='projectName = :projectName',
            ExpressionAttributeValues=expAttValues
        )
    except:
        return Response(body={'Error': 'Requested node does not exist'}, status_code=404)
    # deserialize the dynamoDB results to simplify for the user 
    if 'Attributes' in response: response['Attributes'] = makeNormalDict(response['Attributes'])
    return response

