
# Table of Contents
    0. Introduction
    1. Technology used
    2. Resources consulted
    3. API usage details

# 0. Introduction

## What is this?

This is the repository for an API that provides a management system for **nodes** and **projects**, allowing the user to create, retrieve, and update them. Nodes can also be assigned to projects or unassigned from projects.

Features include batch creation of nodes and projects, validation of user-provided keys and values, and informative error responses. Complexity is hidden from the user when possible, e.g. by serializing/deserializing objects for DynamoDB's low-level interface.

## Team

This project was created by Ephraim Glick (github.com/ephraimg).

# 1. Technology used

The API code is written in Python and deployed using the AWS Chalice microframework, which uses API Gateway and Lambda to create a serverless system. Data is stored in two DynamoDB tables, with a global secondary index on the nodes table to support the assignment and unassignment endpoints.

# 2. Resources consulted

In development, the following resources were consulted:

- Chalice docs: http://chalice.readthedocs.io/en/latest/api.html
- DynamoDB boto3 docs: http://boto3.readthedocs.io/en/latest/reference/services/dynamodb.html
- AWS DynamoDB API reference: https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/Welcome.html
- AWS API Gateway docs: https://aws.amazon.com/documentation/apigateway/
- Post on DynamoDB's low-level API objects: https://stackoverflow.com/questions/43755888/how-to-convert-a-boto3-dynamo-db-item-to-a-regular-dictionary-in-python
- Python docs: https://docs.python.org/2.7/
- Basic info on regular expressions in Python: https://www.tutorialspoint.com/python/python_reg_expressions.htm

# 3. API usage details

## Overview

The API is deployed on AWS with the following base URL: 

- https://vm443vx2w9.execute-api.us-west-1.amazonaws.com/api

The API allows the user to perform three types of task (see the sections below for the endpoints and detailed instructions).

- Create, update, and retrieve nodes
- Create, update, and retrieve projects
- Assign or unassign nodes to/from projects

The node attributes that may be directly set by the user are:

- nodeID (format must be a string of one letter followed by seven digits, e.g. 'W0004551')
- locationXY (format must be a string of a simplified latitude/longitude in parens, e.g. '(24.90, 23.09)')
- shippingStatus (must be one of 'Pending', 'Shipping', 'Shipped')
- configurationStatus (must be one of 'Unconfigured', 'Configured', 'Working')

The project attributes that may be directly set by the user are:

- projectName (format must be a string containing only letters, numbers, and '_')
- customerName (format must be a string containing only letters, numbers, spaces, and '_')
- startDate (format must be a string as in '2018-05-01')
- endDate (format must be a string as in '2018-05-01')

Each project may have nodes assigned and unassigned to it via separate dedicated endpoints. When a node is assigned to a project, it acquires a projectName attribute.

## Security

The API is protected with a key. All requests must include an X-API-Key header. 

## Retrieving details for all nodes

To retrieve all stored nodes, send a **GET request to /nodes**.

## Adding a new node

To create a node, send a **POST request to /nodes**. Your request body should contain a json representation of a list of one or more nodes, each of which has at least a nodeID attribute. Other attributes may optionally be included. Example bodies:

- {"nodes": [{"nodeID": "W0455101"}]}
- {"nodes": [{"nodeID": "X0455101", "shippingStatus": "Pending"}, {"nodeID": "Z0000001", "locationXY": "(44.00, 71.23)"}]}

A maximum of 25 nodes may be created in a single request. However, creating one node per request is safer, as batch creation in DynamoDB does not include safegaurds against accidental overwriting of pre-existing items. (The use of a *ConditionExpression* is not supported.)

## Retrieving details for a node

To retrieve a stored node, send a **GET request to /nodes/{node}**, where {node} is the ID of node to retrieve.

## Updating a node

To update a node, send a **PATCH request to /nodes/{node}**, where {node} is the ID of node to update. Your request body should contain a json object with one or more pairs of node attributes and values. Updating a node's ID is not supported, so a nodeID attribute should not be included in the body. Example bodies:

- {"locationXY": "(23.54, 88.23)"}
- {"shippingStatus": "Shipped", "configurationStatus": "Configured"}

## Retrieving details for all projects

To retrieve all stored projects, send a **GET request to /projects**.

## Adding a new project

To create a project, send a **POST request to /projects**. Your request body should contain a json representation of a list of one or more projects, each of which has at least a projectName attribute. Other attributes may optionally be included. Example bodies:

- {"projects": [{"projectName": "BerkeleyFreshAirProject"}]}
- {"projects": [{"projectName": "ABC", "customerName": "City of Oakland"}, {"projectName": "DEF", "startDate": "2019-01-01"}]}

The only characters permitted in a projectName are letters, digits, and '_'. A maximum of 25 projects may be created in a single request.  However, creating one project per request is safer, as batch creation in DynamoDB does not include safegaurds against accidental overwriting of pre-existing items. (The use of a *ConditionExpression* is not supported.)

## Retrieving details for a project

To retrieve a stored project, send a **GET request to /projects/{project}**, where {project} is the projectName of the project to retrieve.

## Updating a project

To update a project, send a **PATCH request to /projects/{project}**, where {project} is the projectName of the project to update. Your request body should contain a json object with one or more pairs of project attributes and values. Updating a project's name is not supported, so a projectName attribute should not be included in the body. Example bodies:

- {"customerName": "Liz Kong"}
- {"customerName": "Liz Kong", "endDate": "2011-08-11"}

## Get details of all nodes assigned to a project

To retrieve all of a project's nodes, send a **GET request to /projects/{project}/nodes**, where {project} is the project whose nodes will be retrieved.

## Assigning nodes to a project

To assign a node to a project, send a **POST request to /projects/{project}/nodes**, where {project} is the project to which the node will be assigned. The request body should be a json object containing a nodeID. Example body:

- {"nodeID": "Z0022222"}

A node already assigned to a project cannot be assigned to another project unless it is first unassigned from its current one. After assigning a node to a project, that assignment will be included in the details returned from GET /nodes/{node}, stored in a projectName attribute. Assignments of multiple nodes in a single request are not supported.

## Unassigning nodes from a project

To unassign a node from a project, send a **DELETE request to /projects/{project}/nodes**, where {project} is the project from which the nodes will be removed. The request body should be a json object containing a nodeID. Example:

- {"nodeIDs": "A0000007"}

Multiple unassignments in a single request are not supported.


