
import re

projectKeys = ['projectName', 'customerName', 'startDate', 'endDate'] #, 'assignedNodes']

# ensure the submitted node's properties, if present, are valid
def validateProject(project, checkName):
    # check that projectName is present and has the right format
    if checkName:
        if 'projectName' in project:
            if not re.match('^\w+$', project['projectName']):
                return {'Error': 'The projectName must be alphanumeric with no spaces'}
        else:
            return {'Error': 'Missing projectName'}           
    # check that customerName is a string         
    if 'customerName' in project:
        if not re.match('^[ \w]+$', project['customerName']):
            return {'Error': 'Project\'s customerName must be alphanumeric'}
    # check that startDate is a date (using simplified dates here, just as strings)       
    if 'startDate' in project:
        if not re.match('^\d{4}\-\d{2}\-\d{2}$', project['startDate']):
            return {'Error': 'Invalid startDate format'}
    # check that endDate is a date (using simplified dates here, just as strings)       
    if 'endDate' in project:
        if not re.match('^\d{4}\-\d{2}\-\d{2}$', project['endDate']):
            return {'Error': 'Invalid endDate format'}
    return {k : v for k,v in filter(lambda t: t[0] in projectKeys, project.iteritems())}

# sublement the submitted project with any missing properties (default value 'Unknown' or [])
def completeProject(project):
    for key in projectKeys:
        if key != 'projectName': # and key != 'assignedNodes':
            project[key] = project.get(key, None)
    return project