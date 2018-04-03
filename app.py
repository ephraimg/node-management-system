
import boto3
import json
import re

from chalice import Chalice

# functions to do the heavy lifting for routes
from chalicelib.nodeRouteHandlers import handleGetAllNodes, handleGetNode, handleCreateNode, handleUpdateNode
from chalicelib.nodeRouteHandlers import handleCreateNode, handleUpdateNode
from chalicelib.projectRouteHandlers import handleGetAllProjects, handleGetProject
from chalicelib.projectRouteHandlers import handleCreateProject, handleUpdateProject
from chalicelib.assignmentRouteHandlers import handleGetProjectNodes, handleAddProjectNode, handleRemoveProjectNode

app = Chalice(app_name='clarity')
app.debug = True


#############################
# routes for individual nodes

# get info for all nodes
@app.route('/nodes', methods=['GET'], api_key_required=True)
def getAllNodes():
    return handleGetAllNodes()

# get info for a particular node (by id)
@app.route('/nodes/{node}', methods=['GET'], api_key_required=True)
def getNode(node):
    return handleGetNode(node)

# create new node or nodes
@app.route('/nodes', methods=['POST'], api_key_required=True)
def createNode():
    body = app.current_request.json_body
    return handleCreateNode(body)

# update a node's details
@app.route('/nodes/{node}', methods=['PATCH'], api_key_required=True)
def updateNode(node):
    body = app.current_request.json_body
    return handleUpdateNode(node, body)


#####################
# routes for projects

@app.route('/projects', methods=['GET'], api_key_required=True)
def getAllProjects():
    return handleGetAllProjects()

@app.route('/projects', methods=['POST'], api_key_required=True)
def createProject():
    body = app.current_request.json_body
    return handleCreateProject(body)

@app.route('/projects/{project}', methods=['GET'], api_key_required=True)
def getProject(project):
    return handleGetProject(project)

@app.route('/projects/{project}', methods=['PATCH'], api_key_required=True)
def updateProject(project):
    body = app.current_request.json_body
    return handleUpdateProject(project, body)


###########################################
# routes for assigning or unassigning nodes

@app.route('/projects/{project}/nodes', methods=['GET'], api_key_required=True)
def getProjectNodes(project):
    body = app.current_request.json_body
    return handleGetProjectNodes(project)

@app.route('/projects/{project}/nodes', methods=['POST'], api_key_required=True)
def addProjectNode(project):
    body = app.current_request.json_body
    return handleAddProjectNode(project, body)

@app.route('/projects/{project}/nodes', methods=['DELETE'], api_key_required=True)
def removeProjectNode(project):
    body = app.current_request.json_body
    return handleRemoveProjectNode(project, body)
