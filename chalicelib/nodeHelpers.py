import re

nodeKeys = ['nodeID', 'locationXY', 'shippingStatus', 'configurationStatus']

# ensure the submitted node's properties are formatted validly
def validateNode(node, checkID):
    # prevent setting projectName in order to use dedicated assignment logic and routes      
    if 'projectName' in node:
        return {'Error': 'Use /projects/{project}/nodes to assign a node to a project'}
    # check that nodeID is present and has the right format
    if checkID:
        if 'nodeID' in node:
            if not re.match('^[A-Z]\d{7}$', node['nodeID']):
                return {'Error': 'Invalid nodeID'}
        else:
            return {'Error': 'Missing nodeID'}           
    # check that locationXY has the right format (simplified lat/long)         
    if 'locationXY' in node:
        if not re.match('\(\d+.\d+, ?\d+.\d+\)', node['locationXY']):
            return {'Error': 'Invalid locationXY'}
    # check that shippingStatus is not outside allowed set of options       
    if 'shippingStatus' in node:
        if node['shippingStatus'] not in set(['Pending', 'Shipping', 'Shipped']): 
            return {'Error': 'Invalid shippingStatus'}
    # check that shippingStatus is not outside allowed set of options     
    if 'configurationStatus' in node:
        if node['configurationStatus'] not in set(['Unconfigured', 'Configured', 'Working']): 
            return {'Error': 'Invalid configurationStatus'}
    # get rid of unwanted properties
    return {k : v for k,v in filter(lambda t: t[0] in nodeKeys, node.iteritems())}

# sublement the submitted node with any missing properties (default value 'Unknown')
def completeNode(node):
    for key in nodeKeys:
        if key != 'nodeID':
            node[key] = node.get(key, None)
    return node
