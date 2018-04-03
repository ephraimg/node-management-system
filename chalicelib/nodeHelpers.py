import re

nodeKeys = ['nodeID', 'locationXY', 'shippingStatus', 'configurationStatus']

# ensure the submitted node's properties are formatted validly
def validateNode(node, checkID):
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
    validNode = {
        k : v for k,v in filter(lambda t: t[0] in nodeKeys, node.iteritems())
    }
    return validNode 

# sublement the submitted node with any missing properties (default value 'Unknown')
def completeNode(node):
    for key in nodeKeys:
        if key != 'nodeID':
            node[key] = node.get(key, None)
    return node
