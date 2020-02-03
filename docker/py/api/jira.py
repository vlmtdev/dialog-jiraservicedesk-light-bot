import io
import json
import pycurl
import os
import sys
import time
import common.common as common

def createTicket(credentials,projectId,requestTypeId,reporter,requestMessage):
    requestMessageFormatted = common.formatRequest(requestMessage,int(os.environ['REQUEST_NAME_CHARS_COUNT']))
    requestMessageFormatted[0] = requestMessageFormatted[0].replace('\n',' ')
    requestMessageFormatted[1] = requestMessageFormatted[1].replace('\n','\\n')

    postfields = '{"serviceDeskId":"' + projectId + '","requestTypeId":"' + requestTypeId + '","requestFieldValues":{"summary":"' + requestMessageFormatted[0] + '","description":"' + requestMessageFormatted[1] + '"},"raiseOnBehalfOf":"' + reporter + '"}'
    rawjson = postRawData(credentials,'/rest/servicedeskapi/request',postfields)

    return rawjson

def deleteUserFromWatchers(credentials,issueKey):
    response = deleteRawData(credentials,'/rest/api/2/issue/' + issueKey + '/watchers?username=' + credentials[0])
    return response

def parseResponseCreatingTicket(rawjson):
    response = ['']*2
    response[0] = rawjson['_links']['web']
    response[1] = rawjson['issueKey']
    return response

def getProjectIdByProjectKey(credentials,projectKey):
    rawjson = getRawData(credentials,'/rest/servicedeskapi/servicedesk?limit=100')
    i = 0
    while i < len(rawjson['values']):
        if projectKey == rawjson['values'][i]['projectKey']:
            return rawjson['values'][i]['id']
        i += 1
    return None

def getIssueTypeNameByIssueTypeId(credentials,issueId):
    rawjson = getRawData(credentials,'/rest/servicedeskapi/servicedesk/2/requesttype?limit=100')
    i = 0
    while i < len(rawjson['values']):
        if issueId == rawjson['values'][i]['id']:
            return rawjson['values'][i]['name']
        i += 1
    return None

def deleteRawData(credentials,url):
    if checkAuth(credentials,'TECHSUP') == True:
        response = io.BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, credentials[2] + url)
        c.setopt(c.WRITEFUNCTION, response.write)
        c.setopt(c.HTTPHEADER, ["Content-Type: application/json"])
        c.setopt(pycurl.COOKIEFILE, 'jira.cookie')
        c.setopt(pycurl.TIMEOUT, 10)
        c.setopt(pycurl.CUSTOMREQUEST, "DELETE")
    
        c.perform()
        c.close()
        rawResponse = response.getvalue()
        response.close()
        return rawResponse
    else:
        common.conMsg('jira',"Authorization failed!")

def postRawData(credentials,url,postfld=""):
    if checkAuth(credentials,'TECHSUP') == True:
        response = io.BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, credentials[2] + url)
        c.setopt(c.WRITEFUNCTION, response.write)
        c.setopt(c.HTTPHEADER, ["Content-Type: application/json"])
        c.setopt(pycurl.COOKIEFILE, 'jira.cookie')
        c.setopt(pycurl.TIMEOUT, 10)
        c.setopt(pycurl.POST, 1)
        c.setopt(pycurl.POSTFIELDS, postfld.encode('utf-8'))
    
        c.perform()
        c.close()
        #print (response.getvalue())
        rawjson = json.loads(response.getvalue())
        response.close()
        return rawjson
    else:
        common.conMsg('jira',"Authorization failed!")

def getRawData(credentials,url):
    if checkAuth(credentials,'TECHSUP') == True:
        response = io.BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, credentials[2] + url)
        c.setopt(c.WRITEFUNCTION, response.write)
        c.setopt(c.HTTPHEADER, ["Content-Type: application/json"])
        c.setopt(pycurl.COOKIEFILE, 'jira.cookie')
        c.setopt(pycurl.TIMEOUT, 10)
    
        c.perform()
        c.close()
        rawjson = json.loads(response.getvalue())
        response.close()
        return rawjson
    else:
        common.conMsg('jira',"Authorization failed!")



def checkAuth(credentials,projectName):
    jiraurl = credentials[2]
    url = jiraurl+"/rest/api/2/mypermissions?projectKey="+projectName
    #print (url)
    response = io.BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.WRITEFUNCTION, response.write)
    c.setopt(c.HTTPHEADER, ["Content-Type: application/json"])
    c.setopt(pycurl.COOKIEFILE, 'jira.cookie')
    c.setopt(pycurl.TIMEOUT, 10)
    
    try:
        c.perform()
    except pycurl.error:
        return False
    c.close()
    #print ('ALALA'+str(response.getvalue()))
    try:
        rawjson = json.loads(response.getvalue())
    except json.decoder.JSONDecodeError:
        common.conMsg('jira','Lost auth cookie, trying to auth again (failed to parse JSON)')
        response.close()
        return basicAuth(credentials,projectName)
    response.close()
    if 'permissions' in rawjson:
        if rawjson['permissions']['BROWSE_PROJECTS']['havePermission'] == True:
            return True
        else:
            common.conMsg('jira','Lost auth cookie, trying to auth again (Cant obtain permissions)')
            return basicAuth(credentials,projectName)
    else:
        return False
    
    
def basicAuth(credentials,projectName):
    jiralogin = credentials[0]
    jirapwd = credentials[1]
    jiraurl = credentials[2]
    jiraapi = "/rest/api/2/mypermissions?projectKey="+projectName
    url = jiraurl+jiraapi
    response = io.BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.WRITEFUNCTION, response.write)
    c.setopt(c.HTTPHEADER, ["Content-Type: application/json"])
    c.setopt(pycurl.USERPWD, jiralogin+":"+jirapwd)
    c.setopt(pycurl.COOKIEJAR, 'jira.cookie')
    c.setopt(pycurl.TIMEOUT, 10)
    
    try:
        c.perform()
    except pycurl.error:
        return False
    c.close()
    #print ('OLOLO'+str(response.getvalue()))
    try:
        rawjson = json.loads(response.getvalue())
    except json.decoder.JSONDecodeError:
        response.close()
        return False
    if 'permissions' in rawjson:
        response.close()
        return rawjson['permissions']['BROWSE_PROJECTS']['havePermission']
    else:
        response.close()
        return False