import time
import io
import shutil
import os
from translation import translate

def now():
    return time.strftime("%Y/%m/%d %H:%M:%S", time.gmtime())

def conMsg(product,text):
    print (now() + ' : ' + product + ' : ' + text)

def formatRequest(request,charLimit):
    newRequest = ['']*2
    newRequest[0] = request
    newRequest[1] = request
    words = request.split(' ')
    while len(newRequest[0]) >= charLimit and len(words) > 1: 
        words = words[:-1]
        newRequest[0] = ''
        i = 0
        while i < len(words):
            newRequest[0] = newRequest[0] + words[i] + ' '
            i += 1
        
        newRequest[0] = newRequest[0][:-1]

    if len(newRequest[0]) >= charLimit:
        newRequest[0] = translate('ru','veryLongFirstWordInRequest')

    newRequest[1] = newRequest[1] + '\n***\n' + translate('ru','createdBy')

    return newRequest

def parseCreds(creds):
    credsArray = creds.split('@')
    hostname = credsArray[1]
    credsArray = credsArray[0].split(':')
    credsArray.append(hostname)
    return credsArray

def cleanPyCache():
    if os.path.exists("__pycache__"): shutil.rmtree('__pycache__')
    if os.path.exists("api/__pycache__"): shutil.rmtree('api/__pycache__')
    if os.path.exists("common/__pycache__"): shutil.rmtree('common/__pycache__')