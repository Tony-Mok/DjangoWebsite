from channels import Group
import json
from channels.sessions import channel_session

@channel_session
def ws_connect(message,userID):
    Group('allUsers').add(message.reply_channel)
    Group('users-%s' % userID).add(message.reply_channel)
    message.reply_channel.send({'accept': True})

@channel_session
def ws_disconnect(message,userID):
    Group('users-%s' % userID).discard(message.reply_channel)
    
def ws_echo(message,userID):
    a=1
    #print message.content['text']
    
def ws_sendNotificationAlert(userID, notificationDetails):
    result = { 'text':json.dumps({
            'type': 'notificationUpdate',
            'details': 'New Notification\n'+notificationDetails
        })
    }
    Group('users-%s' % userID).send(result)
    
def sendMessage(senderID, receiverID, content, dateTime, senderName, receiverName):
    result = { 'text':json.dumps({
            'type': 'message',
            'senderID': senderID,
            'receiverID': receiverID,
            'senderName': senderName,
            'receiverName': receiverName,
            'content': content,
            'dateTime': dateTime,
        })
    }
    Group('users-%s' % senderID).send(result)
    Group('users-%s' % receiverID).send(result)
    
def sendEndSessionNotification(userID, sessionID):
    result = { 'text':json.dumps({
            'type': 'endSessionNotification',
            'details': 'The session ' + str(sessionID) + ' ended'
        })
    }
    Group('users-%s' % userID).send(result)
    
def sendReviewReminderNotification(userID, sessionID):
    result = { 'text':json.dumps({
            'type': 'reviewReminderNotification',
            'details': 'Please remember to fill in the review of session ' + str(sessionID)
        })
    }
    Group('users-%s' % userID).send(result)