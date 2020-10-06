from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.http import JsonResponse
from .models import *
from django.db.models import Count
from django.shortcuts import redirect
import json
from datetime import date
from datetime import datetime, timedelta
from time import gmtime, strftime
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView
from django.http import HttpResponse, Http404
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.template import Context, Template
from django.db.models import Sum
from django.db.models import Avg
from django.db.models import Q
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
#from django.core import serializers
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import render_to_response
from django.template import RequestContext
import base64
import binascii
import os
from random import SystemRandom
import pusher
from django.core.context_processors import csrf

#pusher_client = pusher.Pusher(app_id='426470',key='09f86b38457695d2e661',secret='995b3b42f6123c553063',cluster='ap1',ssl=True)


sessionLogin = {}
# Create your views here.
    
def indexPage(request):
    template = loader.get_template('index.html')
    return HttpResponse(template.render())
    
def loginPage(request):
    template = loader.get_template('login.html')
    return HttpResponse(template.render(request))
    
##########################################################################################################################
#
#
####################################################USER_SYSTEM###########################################################

@csrf_exempt
def validate_user(request):
    username_input = request.POST.get('username', None)
    password_input = request.POST.get('password', None)
    result = UserTutoria.objects.filter(username=username_input, password=password_input)
    jsonr = json.dumps({ 'isValid': False })
    
    """subject = "Tutoria Endeavor email"
    message = "SMTP test (view.py line 49)"
    from_email = settings.EMAIL_HOST_USER
    to_list = [ "tonymok97@gmail.com", "u3524435@connect.hku.hk", "kflau@cs.hku.hk", "tsangsyf@connect.hku.hk" ]#will change it later
    send_emailNotification(subject, message, from_email, to_list)"""
        
    if result.count() > 0:
        #change db
        sessionLogin[str(result[0].username)] = True
        print sessionLogin
        jsonr = json.dumps({ 'isValid': True, 'id': result[0].id, 'is_student': result[0].is_student, 'is_tutor': result[0].is_tutor})
    return HttpResponse(jsonr,content_type='application/json')

def logoutUser(request):
    if request.method == 'GET':
        userID = request.GET['userID']
    userObj = UserTutoria.objects.filter(id=userID)[0]
    username = str(userObj.username)
    sessionLogin.pop(username, None)
    return redirect('index')
    
def student_home(request,userID):
    template = loader.get_template('student_home.html')
    user = UserTutoria.objects.filter(pk=userID)[0]
    """tutorList = Tutor.objects.all();
    tutorResponse = []
    for tutor in tutorList:
        tutorName = tutor.userID.name
        tutorHourlyRate = tutor.hourlyRate
        tutorUserID = tutor.userID.id
        tutorUniversity = tutor.universityID
        tutorList = Tutor.objects.all();
        tutorReviews=Review.objects.filter(tutor=tutor)
        tutorAvgReview=Review.objects.filter(tutor=tutor).aggregate(Avg('rating')).get('rating__avg', 0.0)
        taggings=Tagging.objects.filter(tutor=tutor)
        if tutorAvgReview is not None:
            tutorAvgReviewPercentage=tutorAvgReview*20
        else:
            tutorAvgReviewPercentage=tutorAvgReview
        tutorInfoJson = {'tutorUserID': tutorUserID, 'tutorName': tutorName, 'tutorHourlyRate': tutorHourlyRate, 'tutorAvgReview': tutorAvgReview, 'tutorAvgReviewPercentage': tutorAvgReviewPercentage, 'tutorReviews': tutorReviews, 'tutorUniversity': tutorUniversity, 'taggings': taggings}
        tutorResponse.append(tutorInfoJson)
    context = Context({'tutorList': tutorResponse, 'userID': userID})
    return HttpResponse(template.render(context))"""
    context = {'userID': userID, 'user': user}
    return HttpResponse(template.render(context, request))
    
def getTutorsList(request,userID):
    page = int(request.POST.get('start', None))                                 #variable sent by datatable
    numOfDataToBeDisplay = int(request.POST.get('length', None))                #variable sent by datatable
    allTutor = Tutor.objects.all()
    tutorList = allTutor.order_by('id')[page:page+numOfDataToBeDisplay]
    #username_input = request.GET.get('start', None)
    jsonResponse = []
    for tutor in tutorList:
        tutorAvgReview=Review.objects.filter(tutor=tutor).aggregate(Avg('rating')).get('rating__avg', 0.0)
        tempTutor = [str(tutor.userID.getFullName()), tutor.userID.gender, str(tutor.universityID.name), tutor.hourlyRate]
        subtag = '<ul>'
        taggings = Tagging.objects.filter(tutor=tutor)
        for tag in taggings:
            subtag += '<li>'+tag.tag.name+'</li>'
        subtag += '</ul>'
        tempTutor.append(subtag)
        if tutorAvgReview is None:
            tempTutor.append('No Ratings')
        else:
            tempTutor.append('<div class="star-ratings-sprite"><span style="width:20%" class="star-ratings-sprite-rating"></span></div>')
        bookingLink = str(str(userID)+"/student_booking/"+str(tutor.userID.id))
        tempTutor.append('<a class="btn btn-primary btn-xl js-scroll-trigger" href="'+bookingLink+'" style="word-wrap:break-word;white-space:pre-wrap;">Book</a>')
        jsonResponse.append(tempTutor)
    
    jsonr = json.dumps({'draw': 0, 'recordsTotal': allTutor.count(), 'recordsFiltered': allTutor.count(), "data": jsonResponse})
   
    return HttpResponse(jsonr,content_type='application/json')
    
def tutor_home(request,userID):
    t = userID
    result = UserTutoria.objects.filter(id=userID)
    template = loader.get_template('tutor_home.html')
    """if result.count() == 0:
        return redirect('login')
    elif request.session.get(result[0].username, default=None) == None:
       return redirect('login')"""
    context = Context({"tutor": userID, "user": result[0]})
    return HttpResponse(template.render(context, request))

####################################################USER_SYSTEM########################################################### 
#
#
##########################################################################################################################




#################################################################################################################################
#
#
####################################################CANCEL_BOOKING###############################################################
    
def student_cancel_booking(request, userID):
    template = loader.get_template('student_cancel_booking.html')
    #result = UserTutoria.objects.filter(id=userID)
    '''bookedSessionList = Session.objects.filter(studentID=userID, status='booked')
    responseResult = []
    for session in bookedSessionList:
        date = session.date
        startTime = session.startTime
        endTime = session.endTime
        tutorID = session.tutorID
        universityID = session.universityID
        sessionID = session.id
        sessionJson={'id': sessionID,'date': date, 'startTime': startTime, 'endTime': endTime, 'tutorID': tutorID,'universityID':universityID}
        responseResult.append(sessionJson)
    context=Context({'sessions': responseResult,'userID':userID})
    return HttpResponse(template.render(context))'''
    context = {'userID': userID}
    return HttpResponse(template.render(context, request))
    
def getBookedSession(request, userID):
    page = int(request.POST.get('start', None))                                 #variable sent by datatable
    numOfDataToBeDisplay = int(request.POST.get('length', None))                #variable sent by datatable
    allBookedSession = Session.objects.filter(studentID=userID, status='booked')
    bookedSessionList = allBookedSession.order_by('-id')[page:page+numOfDataToBeDisplay]
    jsonResponse = []
    for bookedSession in bookedSessionList:
        sessionID = bookedSession.id
        date = str(bookedSession.date)
        startTime = str(bookedSession.startTime)
        endTime = str(bookedSession.endTime)
        tutorName = bookedSession.tutorID.userID.getFullName()
        university = bookedSession.universityID.name
        cancelBtn = '<a class="btn btn-primary btn-xl js-scroll-trigger cancelSession" id="'+str(sessionID)+'" href="javascript:void(0);" style="word-wrap:break-word;white-space:pre-wrap;">Cancel</a>'
        tempSession = [sessionID, date, startTime, endTime, tutorName, university, cancelBtn]
        jsonResponse.append(tempSession)
    jsonr = json.dumps({'draw': 0, 'recordsTotal': allBookedSession.count(), 'recordsFiltered': allBookedSession.count(), "data": jsonResponse})
    return HttpResponse(jsonr,content_type='application/json')

def cancelSession(request):
    sessionID = request.POST.get('sessionID',None)
    sessionObj = Session.objects.filter(id=sessionID)
    userObj = sessionObj[0].studentID.userID
    sessionDate = sessionObj[0].date
    sessionTime = sessionObj[0].startTime
    currentDate = date.today()
    currentTime = datetime.now().time()
    
    diff = datetime.combine(sessionDate, sessionObj[0].startTime) - datetime.combine(currentDate, currentTime)
    if diff.total_seconds()-24*60*60 < 0:
        jsonr = json.dumps({'result': 2})
        return HttpResponse(jsonr,content_type='application/json')
    else:
        buffer = Transaction.objects.create(userID=userObj, totalPayment=sessionObj[0].tutorID.hourlyRate*1.05, description='4', sessionID=sessionObj[0])
        buffer.save()
        
        # student notification
        str1 = "You have cancelled the tutorial session " + str(sessionObj[0].id)
        generate_systemNotification(str1, userObj)
        
        # tutor notification
        str2 = userObj.getFullName() + " has cancelled the tutorial session " + str(sessionObj[0].id)
        tutorUserObj = sessionObj[0].tutorID.userID
        generate_systemNotification(str2, tutorUserObj)
        
        
        sessionObj.update(studentID="")
        jsonr = json.dumps({'result': 1})
        return HttpResponse(jsonr,content_type='application/json')
    
'''
def cancelSession(request):
    tutorID_req = request.POST.get('tutorID', None)
    start_date = request.POST.get('sd', None)
    start_time = request.POST.get('st', None)
    end_time = request.POST.get('et', None)
    result = UserTutoria.objects.filter(id=tutorID_req)[0]
    jsonr = json.dumps({'result': 'Cancel successful'})
    return HttpResponse(jsonr,content_type='application/json')
'''


        
def findOutAvailableSession(tutorType,userID):
    if tutorType == 0:
        userObj = UserTutoria.objects.filter(id=userID)[0]
        blackOutTimeSlots = BlackOutTimeSlot.objects.filter(userID=userObj)
        
    return 1

####################################################CANCEL_BOOKING###############################################################
#
#
#################################################################################################################################



##########################################################################################################################
#
#
####################################################BLACH_OUT#############################################################
def blackTimeSlot(request):
    currentDate = datetime.now()
    #Try to implement add and edit in this part, then delete.
    op = request.POST.get('op',None)
    #Basic information
    b_date = request.POST.get('b_date',None)
    start_t = request.POST.get('start_time',None)
    end_t = request.POST.get('end_time',None)
    
    if(op == 'add'):
        tutor = request.POST.get('user',None)
        tempTutorObj = UserTutoria.objects.filter(id = tutor)[0]
        buffer = BlackOutTimeSlot.objects.create(userID=tempTutorObj,bdate=b_date,startTime=start_t,endTime=end_t,)
        buffer.save()
        jsonr = json.dumps({'pKey':buffer.id})
        finish = datetime.now()
        print("blackTimeSlot--- %s seconds ---" %(finish - currentDate))
        return HttpResponse(jsonr,content_type='application/json')
        
    else:
        pk = request.POST.get('pKey',None)
        buffer = BlackOutTimeSlot.objects.get(id = pk)
        buffer.bdate=b_date
        buffer.startTime=start_t
        buffer.endTime=end_t
        buffer.save()
        jsonr = json.dumps({'pKey':buffer.id})
        finish = datetime.now()
        print("blackTimeSlot--- %s seconds ---" %(finish - currentDate))
        return HttpResponse(jsonr,content_type='application/json')
        
def getBlockedTime(request):
    #need to return the pkey slot.id!=0 for further delete and edit
    currentDate = datetime.now()
    
    tutorID_req = request.POST.get('tutorID', None)
    result = UserTutoria.objects.filter(id=tutorID_req)[0]
    result2 = BlackOutTimeSlot.objects.filter(userID = result, bdate__gte = currentDate, bdate__lte = currentDate + timedelta(days=14))
    
    responseResult = []
    i=1;
    for slot in result2:
        if slot.endTime.hour == 0:
            s = 1
        else:
            s = 0
        tempJson = {'pKey':slot.id, 'status':'resident', 'id':i,'start_date': str(slot.bdate)+" "+str(slot.startTime), 'end_date': str(slot.bdate+timedelta(days=s))+" "+str(slot.endTime),'user':tutorID_req}
        responseResult.append(tempJson)
        i+=1
    jsonr = json.dumps({'result': responseResult})
    finish = datetime.now()
    print("getBlockedTime--- %s seconds ---" %(finish - currentDate))
    return HttpResponse(jsonr,content_type='application/json')

def getFullSession(request):
    tutorUserID_req = request.POST.get('tutorID', None)
    currentDate = datetime.now()
    
    tutorUserObj = UserTutoria.objects.filter(id=tutorUserID_req)[0]
    tutorObj = Tutor.objects.filter(userID=tutorUserObj)[0]
    result = Session.objects.filter(tutorID = tutorObj.id, date__gte = currentDate, date__lte = currentDate + timedelta(days=7))
    responseResult = []
    #print(result.count())
    for session in result:
        if session.studentID is not None:#further implement for finding student name might be needed
            id = session.id
            universityName = University.objects.filter(pk=int(session.universityID.id))[0].name
            tutorObj = session.tutorID
            tutorName = tutorObj.userID.getFullName()
            date = str(session.date)
            startTime = str(session.startTime)
            endTime = str(session.endTime)
            tutorHourlyRate = tutorObj.hourlyRate
            #start_date': str(slot.bdate)+" "+str(slot.startTime), 'end_date': str(slot.bdate)+" "+str(slot.endTime)
            tempJson = {'id': id, 'start_date': date+" "+startTime, 'end_date': date+" "+endTime, 'university': universityName, 'pKey':id}
            responseResult.append(tempJson);
    jsonr = json.dumps({'result': responseResult })
    finish = datetime.now()
    print("getFullSession--- %s seconds ---" %(finish - currentDate))
    return HttpResponse(jsonr,content_type='application/json')

def cancelBlock(request):
    tutorID_req = request.POST.get('tutorID', None)
    start_date = request.POST.get('sd', None)
    start_time = request.POST.get('st', None)
    end_time = request.POST.get('et', None)
    result = UserTutoria.objects.filter(id=tutorID_req)[0]
    BlackOutTimeSlot.objects.filter(userID = result,bdate = start_date,startTime = start_time,endTime=end_time).delete()
    jsonr = json.dumps({'result': 'Cancel successful'})
    return HttpResponse(jsonr,content_type='application/json')


####################################################BLACH_OUT#############################################################
#
#
##########################################################################################################################


#########################################################################################################################
#
#
#
#######################################################WALLET#############################################################
def wallet(request, userID):
    result = UserTutoria.objects.filter(id=userID)
    template = loader.get_template('wallet.html')
    balance=Transaction.objects.filter(userID=userID).aggregate(Sum('totalPayment')).get('totalPayment__sum', 0.0)
    if balance is None:
        balance = 0
    context = {'balance': balance, 'userID': userID}
    return HttpResponse(template.render(context, request))
    #amount=result[0].coins
    #responseResult=[]
    #responseResult.append({'amount':amount})
    """transactionList = Transaction.objects.filter(userID=userID)
    balance=Transaction.objects.filter(userID=userID).aggregate(Sum('totalPayment')).get('totalPayment__sum', 0.0)
    if balance is None:
        balance = 0
    responseResult=[] 
    for transaction in transactionList:
        payment = transaction.totalPayment
        dateTime = transaction.dateTime
        session = transaction.sessionID
        description = transaction.description
        transactionLineJson={'payment': payment, 'dateTime': dateTime, 'session': session, 'description': description}
        responseResult.append(transactionLineJson)
    context=Context({'transactions': responseResult,'balance':balance, 'userID':userID})
    return HttpResponse(template.render(context))"""
    '''
    if result.count() == 0:
        return redirect('login')
    elif sessionLogin.get(str(result[0].username), None) == None:
        return redirect('login')
        
    tutorList = Tutor.objects.all();
    responseResult = []
    for tutor in tutorList:
        tutorName = tutor.userID.name
        tutorHourlyRate = tutor.hourlyRate
        tutorUserID = tutor.userID.id
        tutorInfoJson = {'tutorUserID': tutorUserID, 'tutorName': tutorName, 'tutorHourlyRate': tutorHourlyRate}
        responseResult.append(tutorInfoJson)
    context = Context({'tutorList': responseResult, 'userID': userID})
    return HttpResponse(template.render(context))
        '''

def coins(request,userID):
    userObj = UserTutoria.objects.filter(id=userID)[0]
    template = loader.get_template('addCoin.html')
    balance = Transaction.objects.filter(userID__id=userID).aggregate(Sum('totalPayment')).get('totalPayment__sum', 0.0)
    context = Context({
                      'userID': userObj.id,
                      'name': userObj.getFullName(),
                      'balance':balance,
                      })
    return HttpResponse(template.render(context, request))


def getWalletTransactionHistory(request,userID):
    page = int(request.POST.get('start', None))                                 #variable sent by datatable
    numOfDataToBeDisplay = int(request.POST.get('length', None))                #variable sent by datatable
    allTransaction = Transaction.objects.filter(userID=userID)
    transactionList = allTransaction.order_by('-id')[page:page+numOfDataToBeDisplay]
    jsonResponse = []
    for transaction in transactionList:
        payment = '$' + str(transaction.totalPayment)
        dateTime = transaction.dateTime
        session = transaction.sessionID
        description = transaction.description
        tranDes = ''
        sessionDetail = ''
        if session is None:
            sessionDetail = 'N/A'
        else:
            sessionDetail = '<a href="javascript:void(0);">'+str(session.id)+'</a>'
        if description == '0':
            tranDes = 'Add coins'
        elif description == '1':
            tranDes = 'Remove coins'
        elif description == '2':
            tranDes = 'Tutorial session payment'
        elif description == '3':
            tranDes = 'Tutorial session salary'
        elif description == '4':
            tranDes = 'Tutorial session refund'
        tempTran = [dateTime.strftime('%Y-%m-%d %H:%M:%S'), tranDes, sessionDetail, payment]
        jsonResponse.append(tempTran)
    
    jsonr = json.dumps({'draw': 0, 'recordsTotal': allTransaction.count(), 'recordsFiltered': allTransaction.count(), "data": jsonResponse})
   
    return HttpResponse(jsonr,content_type='application/json')
    
def addCoin(request, userID):
    if (request.method=='POST' and request.is_ajax()):
        try:
            '''
            UID = request.POST.get('userID',None)
            userObj = UserTutoria.objects.get(id=UID)
            #total = obj.coins + request.POST['amount']
            #userObj.coins = total
            #userObj.save()
            
            t = Transaction.objects.create(userID=userObj, totalPayment=request.POST['amount'], description='0')
            t.save()
            '''
            make_transaction(request.POST.get('userID',None), request.POST['amount'], '0')
            return JsonResponse({'status':'Success', 'msg': 'save successfully'})
        except UserTutoria.DoesNotExist:
            return JsonResponse({'status':'Fail', 'msg': 'Object does not exist'})
    else:
        return JsonResponse({'status':'Fail', 'msg':'Not a valid request'})
    #return redirect('wallet')
    #template = loader.get_template('wallet.html')
    #return HttpResponse(template.render())
    
    
def removeCoin(request):
    if (request.method=='POST' and request.is_ajax()):
        try:
            UID = request.POST['userID']
            obj = UserTutoria.objects.get(id=UID)
            total = obj.coins - request.POST['amount']
            obj.coins = total
            obj.save()
            return JsonResponse({'status':'Success', 'msg': 'save successfully'})
        except UserTutoria.DoesNotExist:
            return JsonResponse({'status':'Fail', 'msg': 'Object does not exist'})
    else:
        return JsonResponse({'status':'Fail', 'msg':'Not a valid request'})

#######################################################WALLET#############################################################
#
#
##########################################################################################################################


##########################################################################################################################
#
#
#######################################################MESSAGE############################################################

def notificationCenter(request,userID):
    template = loader.get_template('notification_centre.html')
    """responseResult = Notification.objects.filter(userID=userID).order_by('-id')
    context = Context({
                      'notifications':responseResult,
                      })"""
    context = {'userID': userID}
    return HttpResponse(template.render(context, request))
    
def getNotification(request, userID):
    page = int(request.POST.get('start', None))                                 #variable sent by datatable
    numOfDataToBeDisplay = int(request.POST.get('length', None))                #variable sent by datatable
    allNotifications = Notification.objects.filter(userID=userID).order_by('-id')
    notificationList = allNotifications.order_by('-id')[page:page+numOfDataToBeDisplay]
    jsonResponse = []
    for notification in notificationList:
        dateTime = notification.dateTime
        notificationDetail = notification.notificationDetails
        tempNotification = [dateTime.strftime('%Y-%m-%d %H:%M:%S'), notificationDetail]
        jsonResponse.append(tempNotification)
    jsonr = json.dumps({'draw': 0, 'recordsTotal': allNotifications.count(), 'recordsFiltered': allNotifications.count(), "data": jsonResponse})
   
    return HttpResponse(jsonr,content_type='application/json')
    
def booking_notification(user,conten):
    user = request.POST.get('userID', None)#receiver
    sessionID = request.POST.get('sessionID', None)
    str = userID + "books the tutorial session" + sessionID
    n = Notification.objects.create(userID=user, notificaitonDetails=str)
    n.save()
    return JsonResponse({'status':'Success', 'msg': 'save successfully'})
        
def cancelling_notification(user,conten):
    user = request.POST.get('userID', None)#receiver
    sessionID = request.POST.get('sessionID', None)
    str = userID + "cancela the tutorial session" + sessionID
    n = Notification.objects.create(userID=user, notificaitonDetails=str)
    n.save()
    return JsonResponse({'status':'Success', 'msg': 'save successfully'})
        
def email_notification(userID, sessionID):
    userObj = UserTutoria.objects.filter(id=userID)[0]
    sessionObj = Session.objects.filter(id=sessionID)[0]
    sessionDate = sessionObj.date
    sessionStartTime = sessionObj.startTime
    sessionEndTime = sessionObj.endTime
    tutorObj = sessionObj.tutorID
    tutorName = tutorObj.userID.getFullName()
    tutorEmail = tutorObj.userID.email
    studentName = userObj.getFullName()
    studentEmail = userObj.email
    
    print("")
    print("")
    
    print("Student Email:")
    print("To: " + studentEmail)
    print("Dear " + studentName + ", ")
    print("You have booked the session on " + str(sessionDate) + " from " + str(sessionStartTime) + " to " + str(sessionEndTime))
    print("Regards,")
    print("Tutoria")
    
    print("")
    print("")

    
    print("Tutor Email:")
    print("To: " + tutorEmail)
    print("Dear " + tutorName + ", ")
    print("Your session on " + str(sessionDate) + " from " + str(sessionStartTime) + " to " + str(sessionEndTime) + " has been booked by " +studentName)
    print("Regards,")
    print("Tutoria")
    
def make_transaction(userID, amount, type):
    userObj = UserTutoria.objects.get(id=userID)
    #make transaction
    t = Transaction.objects.create(userID=userObj, totalPayment=amount, description=str(type))
    t.save()
    #make notification
    if amount >=0:
        message = "$"+str(amount) + " has been added to your wallet"
    else:
        message = "$"+str(-amount) + " has been removed from your wallet" 
    n= Notification.objects.create(userID=userObj, notificationDetails=message)
    n.save()

#######################################################MESSAGE############################################################
#
#
##########################################################################################################################

##############################################################################################################################
#
#
###################################################STUDENT_BOOKING############################################################

def getSessions(request,userID):
    tutorUserID = request.POST.get('tutorUserID', None)
    tutorUserID_req = tutorUserID
    currentDate = datetime.now()
    currentTime = currentDate
    tutorUserObj = UserTutoria.objects.filter(id=tutorUserID_req)[0] #blackout
    tutorObj = Tutor.objects.filter(userID=tutorUserObj)[0]
    tutorName = tutorUserObj.getFullName()

    universityName = University.objects.filter(pk=int(tutorObj.universityID.id))[0].name
    tutorHourlyRate = tutorObj.hourlyRate

    results=[]
    results2=[]
    if(tutorObj.tutorType==1):
        for i in range(0,7):
            k = currentDate+timedelta(days=i)
            k2 = k.strftime('%Y-%m-%d')
            blocks = BlackOutTimeSlot.objects.filter(userID = tutorUserObj, bdate=k2)
            list = [False]*48
            for slot in blocks:
                st = slot.startTime.hour*2+slot.startTime.minute/30
                et = slot.endTime.hour*2+slot.endTime.minute/30
                if(et==0):
                    et = 48
                for i in range(st,et):
                    list[i]=True
            results.append((k2,list))

        for (k,lit) in results:
            checks = Session.objects.filter(tutorID = tutorObj, date = k)
            for slot in checks:
                st = slot.startTime.hour*2+slot.startTime.minute/30
                #et = slot.endTime.hour*2+slot.endTime.minute/60
                for i in range(st,st+1):
                    lit[i]=True
            results2.append((k,lit))
    else:
        for i in range(0,7):
            k = currentDate+timedelta(days=i)
            k2 = k.strftime('%Y-%m-%d')
            blocks = BlackOutTimeSlot.objects.filter(userID = tutorUserObj, bdate=k2)
            list = [False]*24
            for slot in blocks:
                #print k2
                st = slot.startTime.hour
                et = slot.endTime.hour
                if(et==0):
                    et = 24
                for i in range(st,et):
                    #print i
                    list[i]=True
            results.append((k2,list))

        for (k,lit) in results:
            checks = Session.objects.filter(tutorID = tutorObj, date = k)
            for slot in checks:
                st = slot.startTime.hour
                #et = slot.endTime.hour
                for i in range(st,st+1):
                    lit[i]=True
            results2.append((k,lit))
            
    responseResult = []

    if(tutorObj.tutorType==0):
        for (k,lt) in results2:       
            for i in range(0,24):
                #print lt[i]
                if not lt[i]:
                    #print i
                    sdate = k
                    if(i==23):
                        date = datetime.strptime(k, "%Y-%m-%d")
                        modified_date = date + timedelta(days=1)
                        edate = datetime.strftime(modified_date, "%Y-%m-%d")
                    else:
                        edate = k
                    sTime = str(i)+":00:00"
                    eTime = str((i+1)%24)+":00:00"
                    tempJson = {'start_date': str(sdate+' '+sTime), 'end_date': str(edate+' '+eTime),'university': universityName, 'tutorName': tutorName, 'tutorHourlyRate': tutorHourlyRate}
                    responseResult.append(tempJson);
    else:
        for (k,lt) in results2:       
            for i in range(0,48):
                if not lt[i]:
                    sdate = k
                    if(i==47):
                        date = datetime.strptime(k, "%Y-%m-%d") #add one day
                        modified_date = date + timedelta(days=1)
                        edate = datetime.strftime(modified_date, "%Y-%m-%d")
                    else:
                        edate = k
                    if(i%2==1):
                        sTime = str(i/2)+":30:00"
                        eTime = str(((i+1)/2)%24)+":00:00"
                    else:
                        sTime = str(i/2)+":00:00"
                        eTime = str(((i+1)/2)%24)+":30:00"
                    tempJson = {'start_date': str(sdate+" "+sTime), 'end_date': str(edate+" "+eTime), 'university': universityName, 'tutorName': tutorName, 'tutorHourlyRate': tutorHourlyRate}
                    responseResult.append(tempJson);

    jsonr = json.dumps({ 'result': responseResult })
    finish = datetime.now()
    print("getSessions--- %s seconds ---" %(finish - currentTime))
    return HttpResponse(jsonr,content_type='application/json')
    
def student_booking(request, studentUserID, tutorUserID):
    result = UserTutoria.objects.filter(id=studentUserID)
    """if result.count == 0:
        print('1')
        return redirect('login')
    elif sessionLogin.get(str(result[0].username), None) == None:
        print('2')
        return redirect('login')"""
    template = loader.get_template('booking.html')
    tutorObj = Tutor.objects.filter(userID__id=tutorUserID)[0]
    context = {'tutorID': tutorObj.id, 'tutorName': tutorObj.userID.getFullName(), 'tutorUserID': tutorUserID, 'studentUserID': studentUserID}
    return HttpResponse(template.render(context, request))
    
def bookSession(request, userID):
    currentTime = datetime.now()
    
    studentUserID = request.POST.get('studentUserID', None)
    userObj = UserTutoria.objects.filter(id=studentUserID)[0]
    studentObj = Student.objects.filter(userID=userObj)[0]
    tutorUserID = request.POST.get('tutorUserID', None)
    tutorUserObj = UserTutoria.objects.filter(id=tutorUserID)[0]
    tutorObj = Tutor.objects.filter(userID=tutorUserObj)[0]
    startTime = request.POST.get('startTime', None)
    endTime = request.POST.get('endTime', None)
    date = request.POST.get('date', None)
    pKey = request.POST.get('pKey', None)
    status = 'booked'
    
    #check if this session has been booked or not
    check = Session.objects.filter(date=date,startTime=startTime,endTime=endTime,status=status,tutorID=tutorObj).count()
    if check > 0:
        jsonr = json.dumps({'result': 0})
        return HttpResponse(jsonr,content_type='application/json')
    
    #check today has booked or not
    duplicate = Session.objects.filter(studentID=studentObj, date=date).count()
    if duplicate > 0:
        jsonr = json.dumps({'result': 3})
        return HttpResponse(jsonr,content_type='application/json')
    #if no

    universityID = University.objects.filter(pk=int(tutorObj.universityID.id))[0]
    
    balance = Transaction.objects.filter(userID=studentUserID).aggregate(Sum('totalPayment')).get('totalPayment__sum', 0.0)
    if balance is None or balance < tutorObj.hourlyRate*1.05:
        jsonr = json.dumps({'result': 2})
        return HttpResponse(jsonr,content_type='application/json')
    else:
        sessionObj = Session.objects.create(date=date,startTime=startTime,endTime=endTime,status=status,universityID = universityID,tutorID=tutorObj,studentID=studentObj)
        make_transaction(studentUserID, -sessionObj.tutorID.hourlyRate*1.05, '2')
        '''
        t = Transaction.objects.create(userID=userObj, totalPayment=-sessionObj[0].tutorID.hourlyRate*1.05, description='2', sessionID=sessionObj[0])
        t.save()
        '''
        #from here
        '''
        #sessionID = request.POST.get('sessionID', None)
        str1 = "You have booked the tutorial session" + sessionID.id
        n1 = Notification.objects.create(userID=studentUserID, notificaitonDetails=str1) #for student
        n1.save()
        str2 = studentUserID "has booked the tutorial session" + sessionID.id
        n2 = Notification.objects.create(userID=sessionObj.tutorObj.id, notificaitonDetails=str) #for tutor
        n2.save()
        '''
        
        # student notification
        str1 = "You have booked the tutorial session " + str(sessionObj.id)
        n1 = Notification.objects.create(userID=userObj, notificationDetails=str1)
        n1.save()
        
        # tutor notification
        str2 = userObj.getFullName() + " has booked the tutorial session " + str(sessionObj.id)
        tutorUserObj = sessionObj.tutorID.userID
        n2 = Notification.objects.create(userID=tutorUserObj, notificationDetails=str2)
        n2.save()
        
        pusher_client.trigger('my-channel-'+str(tutorUserObj.id), 'notification', {'message': 'added new notification'})
        pusher_client.trigger('my-channel-'+str(userObj.id), 'notification', {'message': 'added new notification'})
        
        #to here (deadline fighter, remove if error occurs)
        #sessionObj.update(studentID=studentObj.id)
        sessionObj.save()
        email_notification(studentUserID, sessionObj.id)
        jsonr = json.dumps({'result': 1})
        finish = datetime.now()
        print("BookSessions--- %s seconds ---" %(finish - currentTime))
        return HttpResponse(jsonr,content_type='application/json')
    
###################################################STUDENT_BOOKING##################################################################
#
#
####################################################################################################################################







    
##########################################################################################################################
#
#
##########################################################################################################################


##################################################################################################################################
#
#
#       1. Tutors cannot black out timeslots that have already been booked --> we need a getFullSession.view for black-out view -->Line 322
#       2. Blacked-out timeslots cannot be booked by students for tutorial sessions -->Line 496
#
#
#######################################################NOT_IMPLEMENTED############################################################

        
"""
    def loginCheck(request):
        userID = request.POST.get('userID', None)
        userObj = UserTutoria.objects.filter(id=userID)[0]
        
    if userObj[0].studentID is not None:
        if !userObj[0].is_login:
            return redirect(//)
    else:
        return None
"""

######################################################DEADLINE_FIGHTER#############################################################


        
######################################Submit Review################################

def student_submit_review(request, studentUserID, tutorUserID):
    template = loader.get_template('submit_review.html')
    #result = UserTutoria.objects.filter(id=userID)
    tutorObj = Tutor.objects.filter(userID__id=tutorUserID)[0]
    '''
    for session in bookedSessionList:
        date = session.date
        startTime = session.startTime
        endTime = session.endTime
        tutorID = session.tutorID
        universityID = session.universityID
        sessionID = session.id
        sessionJson={'id': sessionID,'date': date, 'startTime': startTime, 'endTime': endTime, 'tutorID': tutorID,'universityID':universityID}
        responseResult.append(sessionJson)
    '''
    context=Context({'tutorID': tutorObj.userID.id, 'tutorName': tutorObj.userID.getFullName(), 'tutorUserID': tutorUserID, 'studentUserID': studentUserID})
    return HttpResponse(template.render(context, request))
    
def handle_review_submission(request, studentUserID, tutorUserID):
    template = loader.get_template('submit_review.html')
    return HttpResponse(template.render(request))
    
######################################Submit Review################################






##################################### Student's view of tutor's profile################################
def student_tutor_profile(request, studentUserID, tutorUserID):
    template = loader.get_template('student_tutor_profile.html')
    tutorObj = Tutor.objects.filter(userID__id=tutorUserID)[0]
    tutorReviews=Review.objects.filter(tutor=tutorObj)
    taggings=Tagging.objects.filter(tutor=tutorObj)
    context = {'tutorName': tutorObj.userID.getFullName(), 'tutorHourlyRate': tutorObj.hourlyRate, 'tutorUniversity': tutorObj.universityID.name ,'tutorBiography': tutorObj.biography ,'tutorUserID': tutorUserID, 'studentUserID': studentUserID, 'tutorReviews':tutorReviews, 'taggings': taggings}
    return HttpResponse(template.render(context, request))

def test(request):
    template = loader.get_template('test.html')
    return HttpResponse(template.render())
    
#############################View Course History#####################################
def course_history(request,userID):
    userObj = UserTutoria.objects.get(id=userID)
    if userObj.is_student == 1 and userObj.is_tutor == 0:
        template = loader.get_template('student_course_history.html');
        studentObj = Student.objects.get(userID=userObj)
        sessions = Session.objects.filter(Q(status='completed') | Q(status='reviewed'), Q(studentID=studentObj))
        context = {'sessionList': sessions}
        return HttpResponse(template.render(context, request))


#############################Registration#####################################
def registration(request):
    template = loader.get_template('registration.html');
    return HttpResponse(template.render(request))
    
def registration_student(request):
    """template = loader.get_template('registration_student.html');
    return HttpResponse(template.render(request))"""
    c = {}
    c.update(csrf(request))
    return render_to_response("registration_student.html", c)
    
def registration_tutor(request):
    template = loader.get_template('registration_tutor.html');
    universityList = University.objects.all()
    context = {'universityList': universityList}
    return HttpResponse(template.render(context, request))
    
def registration_student_tutor(request):
    template = loader.get_template('registration_student_tutor.html');
    return HttpResponse(template.render(request))
    
def registerNewTutor(request):
    if request.method == 'POST':
        #user
        firstName = request.POST.get('inputName_first', None)
        lastName = request.POST.get('inputName_last', None)
        username = request.POST.get('inputUsername', None)
        password = request.POST.get('inputPassword', None)
        email = request.POST.get('inputEmail', None)
        mobilePhone = request.POST.get('inputMobilePhone', None)
        gender = request.POST.get('selectGender', None)
        #avatar = request.POST.files('inputAvatar', None)
        type = request.POST.get('selectTutorType', None)
        tag = request.POST.get('inputTag', None)
        hourlyRate = request.POST.get('inputHourlyRate', None)
        biography = request.POST.get('inputBiography', None)
        courselist = request.POST.getlist('selectCourseCode')
        #save to db
        newUser = UserTutoria.objects.create(username=username, password=password, firstName=firstName, lastName=lastName, gender=gender, phoneNumber=mobilePhone, email = email, is_tutor = 1, is_student = 0, isActive=0)
        newUser.save()
        
        #new tutor
       
        '''university =  request.POST.get('selectUniversity', None)
        if university == 'Other':
            university = request.POST.get('inputOtherUniversity', None)
            University(name=university).save()
        
        universityID = University.object.filter(name=university)
        newTutor = Tutor.objects.create(userID=newUser, hourlyRate=hourlyRate, tutorAvatar=avatar, tutorType=type, biography=biography)
        newTutor.save()
        
        #CourseTaughtByTutor

        for courses in courselist:
            courseObj = CourseCode.object.filter(courseCode=courses)
            teach = CourseTaughtByTutor.object.create(newTutor, courseObj)
            teach.save()'''
    c = {}
    return render(request, "successRegistration.html", c)
    
def registerNewStudent(request):
    if request.method == 'POST':
        #user
        firstName = request.POST.get('inputName_first', None)
        lastName = request.POST.get('inputName_last', None)
        username = request.POST.get('inputUsername', None)
        password = request.POST.get('inputPassword', None)
        email = request.POST.get('inputEmail', None)
        mobilePhone = request.POST.get('inputMobilePhone', None)
        gender = request.POST.get('selectGender', None)
        #save to db
        newUser = UserTutoria.objects.create(username=username, password=password, firstName=firstName, lastName=lastName, gender=gender, phoneNumber=mobilePhone, email = email, is_tutor = 0, is_student = 1, isActive=0)
        newUser.save()
        #student to db
        newStudent = Student.objects.create(userID=newUser)
        newStudent.save()
    c = {}
    return render(request, "successRegistration.html", c)

    
def registerNewStudentTutor(request):
    if request.method == 'POST':
        #user
        firstName = request.POST.get('inputName_first', None)
        lastName = request.POST.get('inputName_last', None)
        username = request.POST.get('inputUsername', None)
        password = request.POST.get('inputPassword', None)
        email = request.POST.get('inputEmail', None)
        mobilePhone = request.POST.get('inputMobilePhone', None)
        gender = request.POST.get('selectGender', None)
        #user save to db
        newUser = UserTutoria.objects.create(username=username,password=password, firstName=firstName, lastName=lastName, gender=gender, phoneNumber=mobilePhone, email = email, is_tutor = 1, is_student = 1, isActive=0)
        newUser.save()
        
        #new tutor to db
        avator = request.POST.files('inputAvatar', None)
        type = request.POST.get('selectTutorType', None)
        tag = request.POST.get('inputTag', None)
        hourlyRate = request.POST.get('inputHourlyRate', None)
        biography = request.POST.get('inputBiography', None)
        university =  request.GET['selectUniversity']
        if university == 'Other':
            university = request.POST.get('inputOtherUniversity', None)
            University(name=university).save()
        
        universityID = University.object.filter(name=university)
        newTutor = Tutor.objects.create(userID=newUser, universityID=universityID, hourlyRate=hourlyRate, tutorAvatar=avator, tutorType=type, biography=biography)
        newTutor.save()
        
        #CourseTaughtByTutor to db
        courselist = request.POST.getlist('selectCourseCode')
        for courses in courselist:
            courseObj = CourseCode.object.filter(courseCode=courses)
            teach = CourseTaughtByTutor.object.create(newTutor, courseObj)
            teach.save()
        
        #student to db
        newStudent = Student.objects.create(userID=newUser)
        newStudent.save()
    c = {}
    return render(request, "successRegistration.html", c)
#############################################################################
    
def send_emailNotification(subject, message, from_email, to_list):
    send_mail(subject, message, from_email, to_list, fail_silently = True)
    
def generate_systemNotification(messages, userID):
    n = Notification.objects.create(userID=userID, notificationDetails=messages)
    n.save()

def forgetPassword(request):
    template = loader.get_template('forgetpassword.html');
    return HttpResponse(template.render(request))

#https://docs.python.org/3/library/secrets.html
def validate_email(request):
    email_input = request.POST.get('email', None)
    result = UserTutoria.objects.filter(email=email_input)
    if result.count() > 0:#exist in the db
        userObj = UserTutoria.objects.filter(email=email_input)[0]
        result2 = passwordToken.objects.filter(userID=userObj)
        if result2.count() > 0:#has existing token
            passwordToken.objects.filter(userID=userObj).delete()
        #else
        subject = "change your password"
        token = str(token_hex(32))
        message = "Dear "+userObj.firstName+"\n\nPlease follow the link below to reset your password:\n https://comp3297-demo-laukinfungdavid.c9users.io/tutoria/forgetPassword/"+token+"\n\nRegards,\nTutoria Administrator"
        from_email = settings.EMAIL_HOST_USER
        tok = passwordToken.objects.create(userID=userObj, token=token)
        tok.save()
        to_list = [ email_input ]
        send_emailNotification(subject, message, from_email, to_list)
        return JsonResponse({'status':'Success', 'msg': 'validate successfully'})
    else:
        return JsonResponse({'status':'Error', 'msg': 'email not exist'})
        



#########LIBRARY SECRETS FOR GENERATING RANDOM TOKEN########
_sysrand = SystemRandom()

randbits = _sysrand.getrandbits
choice = _sysrand.choice

def randbelow(exclusive_upper_bound):
    """Return a random int in the range [0, n)."""
    if exclusive_upper_bound <= 0:
        raise ValueError("Upper bound must be positive.")
    return _sysrand._randbelow(exclusive_upper_bound)

DEFAULT_ENTROPY = 32  # number of bytes to return by default
"""
def token_bytes(nbytes=None):
    """Return a random byte string containing *nbytes* bytes.
    If *nbytes* is ``None`` or not supplied, a reasonable
    default is used.
    >>> token_bytes(16)  #doctest:+SKIP
    b'\\xebr\\x17D*t\\xae\\xd4\\xe3S\\xb6\\xe2\\xebP1\\x8b'
    """
    if nbytes is None:
        nbytes = DEFAULT_ENTROPY
    return os.urandom(nbytes)
"""
def token_hex(nbytes=None):
    """Return a random text string, in hexadecimal.
    The string has *nbytes* random bytes, each byte converted to two
    hex digits.  If *nbytes* is ``None`` or not supplied, a reasonable
    default is used.
    >>> token_hex(16)  #doctest:+SKIP
    'f9bf78b9a18ce6d46a0cd2b0b86df9da'
    """
    return binascii.hexlify(token_bytes(nbytes)).decode('ascii')
"""
def token_urlsafe(nbytes=None):
    Return a random URL-safe text string, in Base64 encoding.
    The string has *nbytes* random bytes.  If *nbytes* is ``None``
    or not supplied, a reasonable default is used.
    >>> token_urlsafe(16)  #doctest:+SKIP
    'Drmhze6EPcv0fN_81Bj-nA'
    tok = token_bytes(nbytes)
    return base64.urlsafe_b64encode(tok).rstrip(b'=').decode('ascii')"""

##########################################################################
def isValidToken(request, token):
    result = passwordToken.objects.filter(token=token)
    template = loader.get_template('resetPassword.html')
    if result.count() > 0:#exist in the db
        userID = result[0].userID
    #do date check later
        context = {'valid': True, 'userID':userID }
    else:
        context = {'valid': False}
    return HttpResponse(template.render(context, request))
    
def resetPassword(request, token):
    #get password from the form
    password_input = request.POST.get('password', None)
    #to get the userID back by the token
    result = passwordToken.objects.filter(token=token)
    userID = result[0].userID
    #update the password
    UserTutoria.objects.select_related().filter(pk=userID.id).update(password=password_input)
    #delete the token after changing password
    passwordToken.objects.filter(userID=userID).delete()
    return JsonResponse({'status':'Success', 'msg': 'change successfully, check your email for the token'})

"""def activation_email(userID, email):
    userObj = UserTutoria.objects.filter(pk=userID)[0]
    email_input = user.email
    subject = "Activate your account!"
    token = str(token_hex(32))
    message = "Dear "+userObj.firstName+"\n\nPlease follow the link below to activate your account:\n https://comp3297-demo-laukinfungdavid.c9users.io/tutoria/activate_account/"+token+"\n\nRegards,\nTutoria Administrator"
    from_email = settings.EMAIL_HOST_USER
    tok = ActivationToken.objects.create(userID=userObj, token=token)
    tok.save()
    to_list = [ email_input ]
    send_emailNotification(subject, message, from_email, to_list)
    return JsonResponse({'status':'Success', 'msg': 'sent'})
"""