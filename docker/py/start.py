import io
import os
import common.common as common
from translation import translate
import api.dialog as dialog
import api.jira as jira
from dialog_bot_sdk.bot import DialogBot
from dialog_bot_sdk import interactive_media
import grpc
import time
import json
import threading
import fnmatch
import calendar
import sqlite3

lang = os.environ['LANGUAGE']
mode = os.environ['ISSUE_TYPE_MODE']

dbLocation = ('/queue.db')

requestMessageList = []
banList = []
autoSend = []

def on_msg(*params):
    if params[0].sender_uid != None and params[0].peer.type != 2:

        #request array creating
        request = [None]*4
        request[0] = params[0].date // 1000
        request[1] = params[0].sender_uid
        request[2] = str(params[0].message.textMessage.text)

        #getting peer for further actions
        peer = bot.users.get_user_peer_by_id(request[1])

        if str(params[0].message.textMessage.text)[0] != '/':
            if checkDelay(request[1]):
                banList.append(request)
                if mode == '1' or mode == '2':

                    common.conMsg('bot','Message accepted from uid ' + str(params[0].peer.id))
                    queueId = addToQueue(request)

                    request[3] = queueId
                    autoSend.append(request)

                    optional = [None]*2
                    optional[0] = link
                    optional[1] = projectId
                    postRequest = translate(lang,'ticketConfirmation') + request[2] + '\n***\n' + translate(lang,'creatingTicket',optional)

                    buttons = generateButtons(queueId)
                    
                    messageId = bot.messaging.send_message(bot.users.get_user_peer_by_id(request[1]),postRequest,
                        [interactive_media.InteractiveMediaGroup(
                            buttons
                    )]).message_id
                    
                    requestMessage = []
                    requestMessage.append(queueId)
                    requestMessage.append(messageId)
                    requestMessageList.append(requestMessage)
                if mode == '0':
                    common.conMsg('bot','Message accepted from uid ' + str(params[0].peer.id))
                    queueId = addToQueue(request)
                    requestTypeId = os.environ['ISSUE_TYPE_CONFIG'].split(',')[0]
                    sendTicketManually(queueId,requestTypeId)
                    
            else:
                common.conMsg('bot','Attempting to send request from id ' + str(params[0].peer.id) + ' with non-expired delay')
        else:
            if str(request[2]) == '/start':
                bot.messaging.send_message(peer,translate(lang,'greetings'))
                common.conMsg('bot','New user with id ' + str(params[0].peer.id) + ' started session')
            else:
                bot.messaging.send_message(peer,translate(lang,'invalidInput'))
    else:
        common.conMsg('bot','Ignoring message from group with id ' + str(params[0].peer.id))

def on_click(*params):
    buttonValue = str(params[0].value).split(',')
    message = returnFromQueueByQueueId(buttonValue[2])
    if message != None:
        common.conMsg('bot','Clicked button ' + str(buttonValue))
        if buttonValue[0] == 'delete':
            replyToReporter(queue_id=buttonValue[2],keep=False,ticketText=message[3])
            removeFromQueue(buttonValue[2])
            removeFromBanList(params[0].uid)
        else:
            sendTicketManually(buttonValue[2],buttonValue[1])
    else:
        message = bot.messaging.get_messages_by_id([params[0].mid])[0]
        bot.messaging.update_message(message, translate(lang,'requestError'))

def returnFromQueueByQueueId(queue_id):
    dbConnection = sqlite3.connect(dbLocation)
    dbCursor = dbConnection.cursor()

    dbCursor.execute("SELECT * FROM queue WHERE queue_id="+queue_id)
    dbResult = dbCursor.fetchall()
    if len(dbResult) > 0:
        message = tuple(dbResult[0])
    else:
        message = None
    dbConnection.close()
    return message

def generateButtons(queue_id):
    requestTypes = os.environ['ISSUE_TYPE_CONFIG'].split(',')
    buttons = []
    i = 0
    while i < len(requestTypes):
        requestTypeName = jira.getIssueTypeNameByIssueTypeId(credentials,requestTypes[i])
        buttons = buttons + [interactive_media.InteractiveMedia(1,interactive_media.InteractiveMediaButton("type," + requestTypes[i] + ","+queue_id, requestTypeName))]
        i += 1
    buttons = buttons + [interactive_media.InteractiveMedia(1,interactive_media.InteractiveMediaButton("delete,request,"+queue_id, translate(lang,'cancelTicketButton')))]
    common.conMsg('bot','Generated buttons ' + str(buttons))
    return buttons

def removeFromBanList(uid):
    i = 0
    while i < len(banList):
        if uid == banList[i][1]:
            banList.pop(i)
    return True

def checkDelay(uid):
    nowTime = int(calendar.timegm(time.gmtime()))
    result = None
    i = 0
    while i < len(banList):
        if uid == banList[i][1]:
            if nowTime < int(banList[i][0]) + int(os.environ['SEND_DELAY']):
                result = True
            else:
                banList.pop(i)
        i += 1
    if result == True:
        bot.messaging.send_message(bot.users.get_user_peer_by_id(int(uid)),translate(lang,'tooManyRequests'))
        return None
    else:
        return True 
                
    '''
    dbConnection = sqlite3.connect(dbLocation)
    dbCursor = dbConnection.cursor()
    dbCursor.execute("SELECT * FROM queue WHERE uid="+str(uid))
    dbResult = dbCursor.fetchall()

    if len(dbResult) > 0:
        queueMember = tuple(dbResult[0])
    else:
        return True

    messageTime = queueMember[1]

    if nowTime > int(messageTime) + int(os.environ['SEND_DELAY']):
        return True
    else:
        bot.messaging.send_message(bot.users.get_user_peer_by_id(int(uid)),translate(lang,'tooManyRequests'))
        return None
    '''

def replyToReporter(response='',queue_id='',uid='',keep=True,ticketText=''):
    if keep == True:
        if mode == '1' or mode == '2':
            mids = findMidsWithQueueId(str(queue_id))
            message = bot.messaging.get_messages_by_id(mids)[0]
            bot.messaging.update_message(message, translate(lang,'ticketConfirmation') + ticketText + '\n***\n' + translate(lang,'ticketSent') + ' [' + response[1] + '](' + response[0] + ')')
            common.conMsg('bot','Replied to reporter with editing queue_id=' + str(queue_id) + ' response=' + str(response))
        elif mode == '0':
            bot.messaging.send_message(bot.users.get_user_peer_by_id(int(uid)),translate(lang,'ticketConfirmation') + ticketText + '\n***\n' + translate(lang,'ticketSent') + ' [' + response[1] + '](' + response[0] + ')')
            common.conMsg('bot','Replied to reporter with messaging uid=' + str(uid) + ' response=' + str(response))
    else:
        mids = findMidsWithQueueId(str(queue_id))
        message = bot.messaging.get_messages_by_id(mids)[0]
        bot.messaging.update_message(message, translate(lang,'ticketConfirmation') + ticketText + '\n***\n' + translate(lang,'cancelRequest'))
        common.conMsg('bot','Cancelling Replied to reporter with editing queue_id=' + str(queue_id))

def findMidsWithQueueId(queue_id):
    mids = []
    i = 0
    while i < len(requestMessageList):
        if queue_id == requestMessageList[i][0]:
            mids.append(requestMessageList[i][1])
        i += 1
    return mids

def addToQueue(request):
    sqlInsert = [(request[0],request[1],request[2])]
    dbConnection = sqlite3.connect(dbLocation)
    dbCursor = dbConnection.cursor()
    dbCursor.executemany("INSERT INTO queue (time,uid,message) VALUES (?,?,?)", sqlInsert)
    dbConnection.commit()

    dbCursor.execute("SELECT * FROM queue ORDER BY queue_id DESC LIMIT 1")
    queue_id = tuple(dbCursor.fetchall()[0])[0]
    
    dbConnection.close()
    common.conMsg('bot','Added to queue with queue_id=' + str(queue_id) + ' uid=' + str(request[1]))
    return str(queue_id)

def removeFromQueue(queue_id):
    dbConnection = sqlite3.connect(dbLocation)
    dbCursor = dbConnection.cursor()
    dbCursor.execute("DELETE FROM queue WHERE queue_id=" + queue_id)
    dbConnection.commit()
    dbConnection.close()
    common.conMsg('bot','Removed from queue with queue_id=' + str(queue_id))

def removeFromAutoSend(queue_id):
    i = 0
    while i < len(queue_id):
        if autoSend[i][3] == queue_id:
            autoSend.pop(i)
        i += 1
    return None

def sendTicketManually(queue_id,requestTypeId):
    dbConnection = sqlite3.connect(dbLocation)
    dbCursor = dbConnection.cursor()
    dbCursor.execute("SELECT * FROM queue WHERE queue_id=" + queue_id)
    dbResult = dbCursor.fetchall()
    dbConnection.close()
    if len(dbResult) > 0:
        queueMember = tuple(dbResult[0])

        reporter = bot.users.get_user_by_id(int(queueMember[2])).data.nick.value
        requestMessage = queueMember[3]

        response = jira.parseResponseCreatingTicket(jira.createTicket(credentials,projectId,requestTypeId,reporter,requestMessage))

        jira.deleteUserFromWatchers(credentials,response[1])

        replyToReporter(response=response,queue_id=queueMember[0],uid=queueMember[2],ticketText=requestMessage)

        common.conMsg('bot','Ticket sent request manually TypeId=' + str(requestTypeId) + ' reporter=' + str(reporter))

        removeFromQueue(str(queueMember[0]))
        removeFromAutoSend(str(queueMember[0]))
        return response
    else:
        return None

def sendTicketAuto():
    nowTime = int(calendar.timegm(time.gmtime()))
    i = 0
    while i < len(autoSend):
        if int(autoSend[i][0]) < int(nowTime-int(os.environ['ISSUE_TYPE_TIME'])):
            sendTicketManually(autoSend[i][3],os.environ['ISSUE_TYPE_CONFIG'].split(',')[0])
            return None
        i += 1
    else:
        return None

def checkRequestByTimeout():
    nowTime = int(calendar.timegm(time.gmtime()))

    i = 0
   #print (autoSend)
    while i < len(autoSend):
        if int(autoSend[i][0]) < int(nowTime-int(os.environ['REQUEST_TIMEOUT'])):
            #print(autoSend)
            mids = findMidsWithQueueId(str(autoSend[i][3]))
            message = bot.messaging.get_messages_by_id(mids)[0]
            bot.messaging.update_message(message, translate(lang,'cancelledByTimeout'))
            common.conMsg('bot','Ticket cancelled by timeout queue_id=' + str(autoSend[i][3]))
            removeFromQueue(str(autoSend[i][3]))
            removeFromBanList(autoSend[i][1])
            removeFromAutoSend(str(autoSend[i][3]))
            return None
        i += 1
    else:
        return None

def heartbeat():
    threadsList = []
    for thread in threading._enumerate():
        threadsList.append(thread.name)
    
    workingThreads = fnmatch.filter(threadsList, 'Thread-*')

    if len(workingThreads) >= 1:
        return True
    else:
        common.conMsg('bot', 'Bot dropped, trying to reinit')
        return False

def task_manager():
    if heartbeat() == False:
        time.sleep(2)
        initializeBot()
    if mode == '1' and len(autoSend) > 0:
        sendTicketAuto()
    if mode == '2' and len(autoSend) > 0:
        checkRequestByTimeout()
    time.sleep(1)

def checkEnvs():
    if (os.environ['BOT_API_KEY'] and os.environ['PROJECT_KEY'] 
    and os.environ['ISSUE_TYPE_MODE'] and os.environ['ISSUE_TYPE_TIME'] 
    and os.environ['ISSUE_TYPE_CONFIG'] and os.environ['ENDPOINT']
    and os.environ['JIRA_CREDS']):
        return True
    else:
        return None

def dbInit():
    dbConnection = sqlite3.connect(dbLocation)
    dbCursor = dbConnection.cursor()
#    dbCursor.execute("DROP TABLE IF EXISTS queue")
    dbCursor.execute("""CREATE TABLE IF NOT EXISTS queue
                  (queue_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, time text, uid text, message text)""")
    dbConnection.close()

def initializeBot():
    common.conMsg('bot','Bot initialized ')
    bot.messaging.on_message_async(on_msg,on_click)

if __name__ == '__main__':
    common.conMsg('bot','Starting bot')

    bot = DialogBot.get_secure_bot(os.environ['ENDPOINT'],grpc.ssl_channel_credentials(),os.environ['BOT_API_KEY'], verbose=False)

    if checkEnvs():
        credentials = common.parseCreds(os.environ['JIRA_CREDS'])
        link = credentials[2]
        projectId = jira.getProjectIdByProjectKey(credentials,os.environ['PROJECT_KEY'])
        if projectId:
            initializeBot()
            time.sleep(1)
            dbInit()
            common.conMsg('bot','Started bot. Mode: ' + mode)
            while True:  
                task_manager()
        else:
            common.conMsg('bot','Invalid JIRA Creds or JIRA Service Desk Project. Unable to start bot')
    else:
        common.conMsg('bot','Env variables error')

    common.conMsg('bot','Cleaning PyCache')
    common.cleanPyCache()