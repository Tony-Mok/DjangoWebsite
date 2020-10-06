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
from django.db.models import Max
from django.db.models import F
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
from django.core.context_processors import csrf
import decimal
from collections import defaultdict
from dateutil.parser import parse
from django.core.files import File
from . import consumers
from . import emailNotification
from django.contrib.sessions.models import Session


def getRole(userID):
    user = TutoriaUser.objects.filter(id=userID)[0]
    notificationNotRead = Notification.objects.filter(isRead=False, user__id=userID).count()
    if notificationNotRead > 0:
        role={'isTutor':user.isTutor, 'isStudent':user.isStudent, 'userID':userID, 'haveNotificationNotRead': True}
    elif notificationNotRead == 0:
        role={'isTutor':user.isTutor, 'isStudent':user.isStudent, 'userID':userID, 'haveNotificationNotRead': False}
    
    return role

#finished
def indexPage(request):
    template = loader.get_template('index.html')
    return HttpResponse(template.render())

#finished
def loginPage(request):
    if request.session.has_key('userID'):
        session_userid = request.session['userID']
        if(getRole(session_userid)['isTutor']):
            return redirect("/tutoria/"+str(session_userid)+"/tutor_home/")
        elif(getRole(session_userid)['isStudent']):
            return redirect("/tutoria/"+str(session_userid)+"/student_home/")
        else:
            return redirect("/tutoria/"+str(session_userid)+"/wallet/")
    template = loader.get_template('login.html')
    return HttpResponse(template.render(request))

#finished
@csrf_exempt
def validate_user(request):
    username_input = request.POST.get('username', None)
    password_input = request.POST.get('password', None)
    jsonr = TutoriaUser.validate_user(username_input, password_input)
    resp = json.loads(jsonr)
    if resp['isValid']:
        request.session['userID'] = resp['id']
    return HttpResponse(jsonr,content_type='application/json')

#finished
def student_home(request,userID):
    template = loader.get_template('student_home.html')
    return_status = login_check(request, userID)
    if (return_status==1):
        true_id = request.session['userID']
        return redirect("/tutoria/"+str(true_id)+"/student_home/")
    elif (return_status==2):
        return redirect("/tutoria/login")
    user = TutoriaUser.objects.filter(pk=userID)[0]
    isTutor = False
    if int(user.isTutor) == 1:
        isTutor = True
    universities = University.objects.all()
    courses = Course.objects.all()
    context = {'userID': userID, 'user': user,'isTutor':isTutor, 'universities': universities, 'courses': courses, 'role':getRole(userID)}
    return HttpResponse(template.render(context, request))
    
#finished
@csrf_exempt
def getTutorsList(request,userID):
    page = int(request.POST.get('start', None))                                 #variable sent by datatable
    numOfDataToBeDisplay = int(request.POST.get('length', None))                #variable sent by datatable d
    
    filters = {}
    filters['firstName'] = request.POST.get('inputName_first',None)
    filters['lastName'] = request.POST.get('inputName_last',None)
    
    filters['university'] = request.POST.getlist('selectUniversity[]',None)       #Array
    filters['selectTutorType'] = request.POST.getlist('selectTutorType[]', None)
    filters['selectCourseCode'] = request.POST.getlist('selectCourseCode[]', None)
    
    filters['inputSubjectTag'] = request.POST.get('inputSubjectTag', None)
    
    filters['inputMinHourlyRate'] = request.POST.get('inputMinHourlyRate', None)
    filters['inputMaxHourlyRate'] = request.POST.get('inputMaxHourlyRate', None)
    filters['selectSorting'] = request.POST.getlist('selectSorting[]', None)
    
    jsonr = Tutor.getTutorList(userID, page, numOfDataToBeDisplay, filters)
    return HttpResponse(jsonr,content_type='application/json')

#finished
def tutor_home(request,userID):
    return_status = login_check(request, userID)
    if (return_status==1):
        true_id = request.session['userID']
        return redirect("/tutoria/"+str(true_id)+"/tutor_home/")
    elif (return_status==2):
        return redirect("/tutoria/login")
    t = userID
    result = TutoriaUser.objects.filter(id=userID)
    template = loader.get_template('tutor_home.html')
    section = 60
    result2= None
    isStudent = False
    if Tutor.objects.filter(user=result[0]).count() > 0 :
        result2 = Tutor.objects.filter(user=result[0])[0]
        if int(result2.tutorType) == 1:
            section = 30
        if int(result[0].isStudent) == 1:
            isStudent = True
    context = Context({"tutor": userID, "user": result[0],"section":section,"isStudent":isStudent, 'role':getRole(userID)})
    return HttpResponse(template.render(context, request))

#finished
def student_cancel_booking(request, userID):
    return_status = login_check(request, userID)
    if (return_status==1):
        true_id = request.session['userID']
        return redirect("/tutoria/"+str(true_id)+"/cancel_booking/")
    elif (return_status==2):
        return redirect("/tutoria/login")
    template = loader.get_template('student_cancel_booking.html')
    context = {'userID': userID, 'role':getRole(userID)}
    return HttpResponse(template.render(context, request))

#finished
@csrf_exempt
def getBookedSession(request, userID):
    page = int(request.POST.get('start', None))                                 #variable sent by datatable
    numOfDataToBeDisplay = int(request.POST.get('length', None))                #variable sent by datatable
    jsonr = Booking.getBooking(userID, page, numOfDataToBeDisplay)
    
    return HttpResponse(jsonr,content_type='application/json')

@csrf_exempt
def cancelSession(request):#must call when there is a booking session
    sessionID = request.POST.get('sessionID',None)
    print(sessionID)
    sessionObj = Booking.objects.filter(id=sessionID)[0]
    userObj = sessionObj.student.user
    sessionDate = sessionObj.date
    sessionTime = sessionObj.startTime
    currentDate = date.today()
    currentTime = datetime.now().time()
    
    diff = datetime.combine(sessionDate, sessionObj.startTime) - datetime.combine(currentDate, currentTime)
    if diff.total_seconds()-24*60*60 < 0:
        jsonr = json.dumps({'result': 2})
        return HttpResponse(jsonr,content_type='application/json')
    else:
        #email notification
        #to tutor
        template = loader.get_template('email_templete/cancel_tutor.txt')
        subject = "Session cancellation comfirmation"
        d = Context({ 'tutor_name': sessionObj.tutor.user.firstname, 'date':sessionObj.date, 'startTime': sessionObj.startTime, 'endTime': sessionObj.endTime, 'sID':sessionObj.id, 'student_name': sessionObj.student.user.getFullName()})
        text_content = template.render(d)
        from_email = settings.EMAIL_HOST_USER
        to_list = [ sessionObj.tutor.user.email ]
        emailNotification.send_emailNotification(subject, text_content, from_email, to_list)
        #email to student
        template = loader.get_template('email_templete/cancel_student.txt')
        d = Context({ 'student_name': sessionObj.student.user.firstname, 'date':sessionObj.date, 'startTime': sessionObj.startTime, 'endTime': sessionObj.endTime, 'sID':sessionObj.id})
        text_content = template.render(d)
        from_email = settings.EMAIL_HOST_USER
        to_list = [ sessionObj.student.user.email ]
        emailNotification.send_emailNotification(subject, text_content, from_email, to_list)
        
        if sessionObj.tutor.tutorType == 0:
            Transaction.objects.filter(booking=sessionID).update(description='4')
            buffer = Transaction.objects.filter(booking=sessionObj)[0]
            if buffer.cancelBooking():
                cancelNotification(sessionObj)
                sessionObj.delete()
                print("deleted1")
                
            else:
                jsonr = json.dumps({'result': 3})
                return HttpResponse(jsonr,content_type='application/json')
        else:
            cancelNotification(sessionObj)
            sessionObj.delete()
            print("deleted2")
            
        
        jsonr = json.dumps({'result': 1})
        return HttpResponse(jsonr,content_type='application/json')
        
def cancelNotification(sessionObj):
    # student notification
    str1 = "You have cancelled the tutorial session " + str(sessionObj.id)
    Notification.generate_systemNotification(sessionObj.student.user, str1)
    # tutor notification
    str2 = sessionObj.student.user.getFullName() + " has cancelled the tutorial session " + str(sessionObj.id)
    tutorUserObj = sessionObj.tutor.user
    Notification.generate_systemNotification(sessionObj.tutor.user, str2)

@csrf_exempt     
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
        tempTutorObj = TutoriaUser.objects.filter(id = tutor)[0]
        buffer = BlackOutTimeSlot.objects.create(user=tempTutorObj,bdate=b_date,startTime=start_t,endTime=end_t,)
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

@csrf_exempt      
def getBlockedTime(request):
    #need to return the pkey slot.id!=0 for further delete and edit
    currentDate = datetime.now()
    responseResult = []
    tutorID_req = request.POST.get('tutorID', None)
    result = TutoriaUser.objects.filter(id=tutorID_req)[0]
    if int(result.isActive) == 1:
        result2 = BlackOutTimeSlot.objects.filter(user = result, bdate__gte = currentDate, bdate__lte = currentDate + timedelta(days=14))
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

@csrf_exempt 
def getFullSession(request):
    tutorUserID_req = request.POST.get('tutorID', None)
    currentDate = datetime.now()
    responseResult = []
    tutorUserObj = TutoriaUser.objects.filter(id=tutorUserID_req)[0]
    tutorObj = Tutor.objects.filter(user=tutorUserObj)[0]
    result = Booking.objects.filter(tutor = tutorObj, date__gte = currentDate, date__lte = currentDate + timedelta(days=7))
    #if int(tutorUserObj.isActive) == 1:
    for session in result:
        if session.student is not None:#further implement for finding student name might be needed
            id = session.id
            student_name=session.student.user.getFullName()
            universityName = University.objects.filter(pk=int(tutorObj.university.id))[0].name
            tutorObj = session.tutor
            tutorName = tutorObj.user.getFullName()
            tutorUserID=tutorObj.user.id
            date = str(session.date)
            startTime = str(session.startTime)
            endTime = str(session.endTime)
            tutorHourlyRate = tutorObj.hourlyRate
            tempJson = {'id': id, 'start_date': date+" "+startTime, 'end_date': date+" "+endTime, 'university': universityName, 'pKey':id, 'student_name': student_name, 'tutorUserID':tutorUserID}
            responseResult.append(tempJson);
    jsonr = json.dumps({'result': responseResult })
    finish = datetime.now()
    print("getFullSession--- %s seconds ---" %(finish - currentDate))
    return HttpResponse(jsonr,content_type='application/json')

@csrf_exempt 
def cancelBlock(request):
    tutorID_req = request.POST.get('tutorID', None)
    start_date = request.POST.get('sd', None)
    start_time = request.POST.get('st', None)
    end_time = request.POST.get('et', None)
    result = TutoriaUser.objects.filter(id=tutorID_req)[0]
    BlackOutTimeSlot.objects.filter(user = result,bdate = start_date,startTime = start_time,endTime=end_time).delete()
    jsonr = json.dumps({'result': 'Cancel successful'})
    return HttpResponse(jsonr,content_type='application/json')
    
def wallet(request, userID):
    return_status = login_check(request, userID)
    if (return_status==1):
        true_id = request.session['userID']
        return redirect("/tutoria/"+str(true_id)+"/wallet/")
    elif (return_status==2):
        return redirect("/tutoria/login")
    result = TutoriaUser.objects.filter(id=userID)
    template = loader.get_template('wallet.html')
    redir = "student"
    if int(result[0].isTutor) == 1:
        redir = "tutor"
    context = {'balance': result[0].balance, 'userID': userID,'redir':redir, 'role':getRole(userID)}
    return HttpResponse(template.render(context, request))
    
def coins(request,userID):
    return_status = login_check(request, userID)
    if (return_status==1):
        true_id = request.session['userID']
        return redirect("/tutoria/"+str(true_id)+"/coins")
    elif (return_status==2):
        return redirect("/tutoria/login")
    userObj = TutoriaUser.objects.filter(id=userID)[0]
    template = loader.get_template('addCoin.html')
    #balance = Transaction.objects.filter(userID__id=userID).aggregate(Sum('totalPayment')).get('totalPayment__sum', 0.0)
    balance = userObj.balance
    context = Context({
                      'userID': userObj.id,
                      'name': userObj.getFullName(),
                      'balance':balance,
                      })
    return HttpResponse(template.render(context, request))

@csrf_exempt  
def getWalletTransactionHistory(request,userID):
    page = int(request.POST.get('start', None))                                 #variable sent by datatable
    numOfDataToBeDisplay = int(request.POST.get('length', None))                #variable sent by datatable
    allTransaction = Transaction.objects.filter(user=userID)
    transactionList = allTransaction.order_by('-id')[page:page+numOfDataToBeDisplay]
    jsonResponse = []
    for transaction in transactionList:
        payment = '$' + str(transaction.amount)
        dateTime = transaction.dateTime
        session = transaction.booking
        description = transaction.description
        otherParty=transaction.otherParty
        tranDes = ''
        sessionDetail = ''
        if session is None:
            sessionDetail = 'N/A'
        #elif(str(session.student.user.id)==userID):
            #sessionDetail = 'Tutor: '+str(session.tutor.user.getFullName())
        else:
            #sessionDetail = 'Student: '+str(session.student.user.getFullName())
            sessionDetail = otherParty
            print(userID)
            print(session.student.user.id)
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

@csrf_exempt  
def addCoin(request, userID):
    if (request.method=='POST' and request.is_ajax()):
        userObj = TutoriaUser.objects.get(pk=userID)
        try:
            '''make_transaction(request.POST.get('userID',None), request.POST['amount'], '0')'''
            amount = int(request.POST['amount'])
            if (amount>0):
                Transaction.create(userObj, None, 'addCoins', int(request.POST['amount']), None)
                return JsonResponse({'status':'Success', 'msg': 'save successfully', 'role':getRole(userID)})
            elif (amount<=0):
                Transaction.create(userObj, None, 'removeCoins', int(request.POST['amount']), None)
                return JsonResponse({'status':'Success', 'msg': 'save successfully', 'role':getRole(userID)})
            else:
                return JsonResponse({'status':'Fail', 'msg': 'Object does not exist', 'role':getRole(userID)})
        except TutoriaUser.DoesNotExist:
            return JsonResponse({'status':'Fail', 'msg': 'Object does not exist', 'role':getRole(userID)})
    else:
        return JsonResponse({'status':'Fail', 'msg':'Not a valid request', 'role':getRole(userID)})

@csrf_exempt
def removeCoin(request):
    if (request.method=='POST' and request.is_ajax()):
        try:
            UID = request.POST['userID']
            obj = TutoriaUser.objects.get(id=UID)
            total = obj.coins - request.POST['amount']
            obj.coins = total
            obj.save()
            return JsonResponse({'status':'Success', 'msg': 'save successfully', 'role':getRole(userID)})
        except UserTutoria.DoesNotExist:
            return JsonResponse({'status':'Fail', 'msg': 'Object does not exist', 'role':getRole(userID)})
    else:
        return JsonResponse({'status':'Fail', 'msg':'Not a valid request', 'role':getRole(userID)})
        
def notificationCenter(request,userID):
    return_status = login_check(request, userID)
    if (return_status==1):
        true_id = request.session['userID']
        return redirect("/tutoria/"+str(true_id)+"/notification_center/")
    elif (return_status==2):
        return redirect("/tutoria/login")
    template = loader.get_template('notification_centre.html')
    notificationNotRead = Notification.objects.filter(isRead=False, user__id=userID)
    for notification in notificationNotRead:
        notification.isRead = True
        notification.save()
    context = {'userID': userID, 'role':getRole(userID)}
    return HttpResponse(template.render(context, request))

@csrf_exempt 
def getNotification(request, userID):
    page = int(request.POST.get('start', None))                                 #variable sent by datatable
    numOfDataToBeDisplay = int(request.POST.get('length', None))                #variable sent by datatable
    jsonr = Notification.getNotification(userID, page, numOfDataToBeDisplay)
    return HttpResponse(jsonr,content_type='application/json')

@csrf_exempt
def booking_notification(user,conten):
    user = request.POST.get('userID', None)#receiver
    sessionID = request.POST.get('sessionID', None)
    str = userID + "books the tutorial session" + sessionID
    n = Notification.objects.create(userID=user, notificaitonDetails=str)
    n.save()
    return JsonResponse({'status':'Success', 'msg': 'save successfully'})
   
@csrf_exempt 
def cancelling_notification(user,conten):
    user = request.POST.get('userID', None)#receiver
    sessionID = request.POST.get('sessionID', None)
    str = userID + "cancela the tutorial session" + sessionID
    n = Notification.objects.create(userID=user, notificaitonDetails=str)
    n.save()
    return JsonResponse({'status':'Success', 'msg': 'save successfully'})

@csrf_exempt
def email_notification(userID, sessionID):
    userObj = TutoriaUser.objects.filter(id=userID)[0]
    sessionObj = Booking.objects.filter(id=sessionID)[0]
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
'''    
def make_transaction(userID, amount, type):
    userObj = TutoriaUser.objects.get(id=userID)
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
''' 
@csrf_exempt
def getSessions(request,userID):
    tutorUserID = request.POST.get('tutorUserID', None)
    tutorUserID_req = tutorUserID
    currentDate = datetime.now()
    currentTime = currentDate
    tutorUserObj = TutoriaUser.objects.filter(id=tutorUserID_req)[0] #blackout
    tutorObj = Tutor.objects.filter(user=tutorUserObj)[0]
    tutorName = tutorUserObj.getFullName()

    universityName = University.objects.filter(pk=int(tutorObj.university.id))[0].name
    tutorHourlyRate = tutorObj.hourlyRate

    results=[]
    results2=[]
    if(tutorObj.tutorType==1):
        for i in range(0,7):
            k = currentDate+timedelta(days=i)
            k2 = k.strftime('%Y-%m-%d')
            blocks = BlackOutTimeSlot.objects.filter(user = tutorUserObj, bdate=k2)
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
            checks = Booking.objects.filter(tutor = tutorObj, date = k)
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
            blocks = BlackOutTimeSlot.objects.filter(user = tutorUserObj, bdate=k2)
            list = [False]*24
            for slot in blocks:
                st = slot.startTime.hour
                et = slot.endTime.hour
                if(et==0):
                    et = 24
                for i in range(st,et):
                    list[i]=True
            results.append((k2,list))

        for (k,lit) in results:
            checks = Booking.objects.filter(tutor = tutorObj, date = k)
            for slot in checks:
                st = slot.startTime.hour
                for i in range(st,st+1):
                    lit[i]=True
            results2.append((k,lit))
            
    responseResult = []

    if(tutorObj.tutorType==0):
        for (k,lt) in results2:       
            for i in range(0,24):
                if not lt[i]:
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
    
def student_booking(request, userID, tutorUserID):
    return_status = login_check(request, userID)
    if (return_status==1):
        true_id = request.session['userID']
        return redirect("/tutoria/"+str(true_id)+"/student_booking/"+str(tutorUserID))
    elif (return_status==2):
        return redirect("/tutoria/login")
    result = TutoriaUser.objects.filter(id=userID)
    template = loader.get_template('booking.html')
    tutorObj = Tutor.objects.filter(user__id=tutorUserID)[0]
    context = {'tutorID': tutorObj.id, 'tutorName': tutorObj.user.getFullName(), 'tutorUserID': tutorUserID, 'userID': userID, 'role':getRole(userID)}
    return HttpResponse(template.render(context, request))

@csrf_exempt
def bookSession(request, userID):

    currentTime = datetime.now()
    userID = request.POST.get('userID', None)
    userObj = TutoriaUser.objects.filter(id=userID)[0]
    studentObj = Student.objects.filter(user=userObj)[0]
    tutorUserID = request.POST.get('tutorUserID', None)
    tutorUserObj = TutoriaUser.objects.filter(id=tutorUserID)[0]
    tutorObj = Tutor.objects.filter(user=tutorUserObj)[0]
    startTime = request.POST.get('startTime', None)
    endTime = request.POST.get('endTime', None)
    date = request.POST.get('date', None)
    pKey = request.POST.get('pKey', None)
    coupon = request.POST.get('coupon', None)
    status = 'booked'
    
    jsonr = Booking.bookASession(date, startTime, endTime, studentObj, tutorObj,coupon)
    return HttpResponse(jsonr,content_type='application/json')

@csrf_exempt    
def checkCoupon(request, userID):
    coupon = request.POST.get('coupon', None)
    count = Coupon.objects.filter(couponCode=coupon).count()
    if count > 0:
        c = Coupon.objects.filter(couponCode=coupon)[0]
        if c.startTime <= datetime.now() and c.endTime >= datetime.now():
            jsonr = json.dumps({'result':1})
        else:
            jsonr = json.dumps({'result':0})#expired
    else:
        jsonr = json.dumps({'result':0})
    return HttpResponse(jsonr,content_type='application/json')
        
def student_submit_review(request, userID, tutorUserID, bookingID):
    return_status = login_check(request, userID)
    if (return_status==1):
        true_id = request.session['userID']
        return redirect("/tutoria/"+str(true_id)+"/student_submit_review/"+str(tutorUserID)+"/"+str(bookingID)+"/")
    elif (return_status==2):
        return redirect("/tutoria/login")
    template = loader.get_template('finishedReview.html')
    bookingObj = Booking.objects.get(id=bookingID)
    tutorObj = Tutor.objects.filter(user=bookingObj.tutor.user)[0]
    reviewObj = Review.objects.filter(booking__id=bookingID)
    if bookingObj.status == 'completed':
        #context=Context({'tutorID': tutorObj.user.id, 'tutorName': tutorObj.user.getFullName(), 'tutorUserID': tutorUserID, 'userID': userID, 'bookingDate':bookingObj.date, 'bookingStart':bookingObj.startTime, 'bookingEnd':bookingObj.endTime})
        context={'tutorID': tutorObj.user.id, 'tutorName': tutorObj.user.getFullName(), 'tutorUserID': tutorUserID, 'userID': userID, 'bookingDate':bookingObj.date, 'bookingStart':bookingObj.startTime, 'bookingEnd':bookingObj.endTime, 'reviewObj': reviewObj, 'bookingObj': bookingObj, 'role':getRole(userID)}
        #return HttpResponse(template.render(context,request))
        return render(request,'submit_review.html',context)
    else:
        return HttpResponse(template.render(request))

@csrf_exempt 
def handle_review_submission(request, userID, tutorUserID, bookingID):
    return_status = login_check(request, userID)
    if (return_status==1):
        true_id = request.session['userID']
        return redirect("/tutoria/"+str(true_id)+"/student_submit_review/"+str(tutorUserID)+"/"+str(bookingID)+"/handle_review_submission/")
    elif (return_status==2):
        return redirect("/tutoria/login")
    template = loader.get_template('successReview.html')
    c =  {}
    print("here")
    if request.method == 'POST':
        bookingObj = Booking.objects.filter(id=bookingID)[0]
        if bookingObj.status != 'completed':
            template = loader.get_template('finishedReview.html')
            return HttpResponse(template.render(request))
        #tutorObj = Tutor.objects.filter(user__id=tutorUserID)[0]
        #studentObj = Student.objects.filter(user__id=userID)[0]
        rating = request.POST.get('inputRating', None)
        comment = request.POST.get('inputComment', None)
        review = Review.objects.create(tutor = bookingObj.tutor, student = bookingObj.student, booking = bookingObj, rating=rating, comment=comment )
        if "anonymous" in request.POST:
            review.anonymous = True
        review.save()
        Booking.objects.filter(id=bookingID).update(status='reviewed')
        
        if Review.objects.filter(tutor=bookingObj.tutor).count()<3:
            bookingObj.tutor.score = -1.0
        else:
            bookingObj.tutor.score = Review.objects.filter(tutor=bookingObj.tutor).aggregate(Avg('rating')).get('rating__avg', 0.0)
        bookingObj.tutor.save()
        
        #bookingObj.objects.update(status='reviewed')
    return HttpResponse(template.render(request))
    #return render(request, "successReview.html", c)
    
def session_detail(request, userID, bookingID):
    return_status = login_check(request, userID)
    if (return_status==1):
        true_id = request.session['userID']
        return redirect("/tutoria/"+str(true_id)+"/session_detail/"+str(bookingID)+"/")
    elif (return_status==2):
        return redirect("/tutoria/login")
    template = loader.get_template('session_detail.html')
    bookingObj = Booking.objects.get(id=bookingID)
    context={'bookingObj':bookingObj, 'role':getRole(userID)}
    return HttpResponse(template.render(context, request))
    
def student_tutor_profile(request, userID, tutorUserID):
    return_status = login_check(request, userID)
    if (return_status==1):
        true_id = request.session['userID']
        return redirect("/tutoria/"+str(true_id)+"/student_tutor_profile/"+str(tutorUserID)+"/")
    elif (return_status==2):
        return redirect("/tutoria/login")
    template = loader.get_template('student_tutor_profile.html')
    tutorObj = Tutor.objects.filter(user__id=tutorUserID)[0]
    tutorReviews=Review.objects.filter(tutor=tutorObj)
    tags=SubjectTag.objects.filter(tutor=tutorObj)
    courses=Course.objects.filter(tutor=tutorObj)
    context = {'tutorObj': tutorObj,'tutorName': tutorObj.user.getFullName(), 'tutorHourlyRate': tutorObj.hourlyRate, 'tutorUniversity': tutorObj.university.name ,'tutorBiography': tutorObj.biography ,'tutorUserID': tutorUserID, 'userID': userID, 'tutorReviews':tutorReviews, 'tags': tags, 'tutorAvatar': tutorObj.user.avatar, 'courses':courses, 'email':tutorObj.user.email, 'role':getRole(userID)}
    return HttpResponse(template.render(context, request))
    
def my_profile(request, userID):
    return_status = login_check(request, userID)
    if (return_status==1):
        true_id = request.session['userID']
        return redirect("/tutoria/"+str(true_id)+"/my_profile/")
    elif (return_status==2):
        return redirect("/tutoria/login")
    template = loader.get_template('my_profile.html')
    userObj=TutoriaUser.objects.filter(id=userID)[0]
    tutorInfo={}
    if userObj.isTutor :
        tutorObj = Tutor.objects.filter(user__id=userID)[0]
        tutorReviews=Review.objects.filter(tutor=tutorObj)
        tags=SubjectTag.objects.filter(tutor=tutorObj)
        courses=Course.objects.filter(tutor=tutorObj)
        tutorInfo = {'tutorReviews':tutorReviews, 'tags': tags, 'courses':courses, 'tutorObj': tutorObj}
    context={'userObj':userObj, 'tutorInfo': tutorInfo,'role':getRole(userID)}
    return HttpResponse(template.render(context, request))
    
def edit_profile(request, userID):
    return_status = login_check(request, userID)
    if (return_status==1):
        true_id = request.session['userID']
        return redirect("/tutoria/"+str(true_id)+"/edit_profile/")
    elif (return_status==2):
        return redirect("/tutoria/login")
    template = loader.get_template('edit_profile.html')
    userObj=TutoriaUser.objects.filter(id=userID)[0]
    universityList = University.objects.all()
    Allcourse = Course.objects.all()
    tutorInfo={}
    if userObj.isTutor :
        tutorObj = Tutor.objects.filter(user__id=userID)[0]
        tutorReviews=Review.objects.filter(tutor=tutorObj)
        tags=SubjectTag.objects.filter(tutor=tutorObj)
        courses=Course.objects.filter(tutor=tutorObj)
        tutorInfo = {'tutorReviews':tutorReviews, 'tags': tags, 'courses':courses, 'tutorObj': tutorObj}
    context={'userObj':userObj, 'tutorInfo': tutorInfo,'role':getRole(userID), 'universityList':universityList, 'Allcourse':Allcourse}
    return HttpResponse(template.render(context, request))


def course_history(request,userID):
    return_status = login_check(request, userID)
    if (return_status==1):
        true_id = request.session['userID']
        return redirect("/tutoria/"+str(true_id)+"/course_history/")
    elif (return_status==2):
        return redirect("/tutoria/login")
    userObj = TutoriaUser.objects.get(id=userID)
    if userObj.isStudent == 1:
        template = loader.get_template('student_course_history.html')
        #studentObj = Student.objects.get(user=userObj)
        #sessions = Booking.objects.filter(Q(status='completed') | Q(status='reviewed'), Q(student=studentObj))
        #context = {'sessionList': sessions}
        #return HttpResponse(template.render(context, request))
        context={'userID': userID, 'role': getRole(userID)}
        return HttpResponse(template.render(context,request))

@csrf_exempt     
def getCourseHistory(request,userID):
    return_status = login_check(request, userID)
    if (return_status==1):
        true_id = request.session['userID']
        return redirect("/tutoria/"+str(true_id)+"/course_history/")
    elif (return_status==2):
        return redirect("/tutoria/login")
    userObj = TutoriaUser.objects.filter(id=userID)[0]
    if userObj.isStudent == 1:
        studentObj = Student.objects.get(user=userObj)
        bookings = Booking.objects.filter(Q(status='completed') | Q(status='reviewed'), Q(student=studentObj))
        jsonResponse = []
        for booking in bookings:
            tempBooking = [str(booking.id), str(booking.date), str(booking.startTime), str(booking.endTime), str(booking.tutor.user.getFullName()), str(booking.tutor.university.name)]
            if booking.status == 'reviewed':
                tempBooking.append("")
            elif booking.status == 'completed':
                href = str('/tutoria/' + str(studentObj.user.id) + '/submit_review/' + str(booking.tutor.user.id) + '/' + str(booking.id))
                tempBooking.append('<a class="btn btn-primary btn-xl js-scroll-trigger review" id="'+str(booking.id)+'" href="'+href+'" style="word-wrap:break-word;white-space:pre-wrap;">Review</a>')
            jsonResponse.append(tempBooking)
        jsonr = json.dumps({'draw': 0, 'recordsTotal': bookings.count(), 'recordsFiltered': bookings.count(), "data": jsonResponse})
        return HttpResponse(jsonr,content_type='application/json')
        
#############################Registration#####################################

def registration(request):
    template = loader.get_template('registration.html');
    return HttpResponse(template.render(request))
    
def registration_student(request):
    #template = loader.get_template('registration_student.html');
    #return HttpResponse(template.render(request))
    c = {}
    c.update(csrf(request))
    return render_to_response("registration_student.html", c)
    
def registration_tutor(request):
    template = loader.get_template('registration_tutor.html');
    universityList = University.objects.all()
    courseList = Course.objects.all().order_by('courseCode')
    subjectTagList = SubjectTag.objects.all().order_by('tagName')
    context = {'universityList': universityList, 'courseList': courseList, 'subjectTagList': subjectTagList}
    return HttpResponse(template.render(context, request))
    
def registration_student_tutor(request):
    template = loader.get_template('registration_student_tutor.html');
    universityList = University.objects.all()
    courseList = Course.objects.all().order_by('courseCode')
    subjectTagList = SubjectTag.objects.all().order_by('tagName')
    context = {'universityList': universityList, 'courseList': courseList, 'subjectTagList': subjectTagList}
    return HttpResponse(template.render(context, request))

@csrf_exempt
def registerNewTutor(request):
    c = {}
    if request.method == 'POST':
        #user
        firstName = request.POST.get('inputName_first', None)
        lastName = request.POST.get('inputName_last', None)
        username = request.POST.get('inputUsername', None)
        password = request.POST.get('inputPassword', None)
        email = request.POST.get('inputEmail', None)
        mobilePhone = request.POST.get('inputMobilePhone', None)
        gender = request.POST.get('selectGender', None)
        try:#if no avatar
            avatar = request.FILES['inputAvatar']
        except KeyError:
            avatar = None
        tutorType = request.POST.get('selectTutorType', None)
        taglist = request.POST.getlist('inputTag', None)
        hourlyRate = request.POST.get('inputHourlyRate', None)
        if int(tutorType) == 1:
            if hourlyRate == None:
                hourlyRate = 0
        else:
            if hourlyRate == None:
                hourlyRate = 10
        biography = request.POST.get('inputBiography', None)
        courselist = request.POST.getlist('selectCourseCode')
        university = request.POST.get('selectUniversity', None)
        universityObj = University.objects.get(name = university)
        #validate check before updating db
        #check for repeat userID
        result = TutoriaUser.objects.filter(username=username)
        if result.count() > 0:
            return render(request, "failRegistration_1.html", c)
        result = TutoriaUser.objects.filter(email=email)
        if result.count() > 0:
            return render(request, "failRegistration_2.html", c)
        #save to db
        newUser = TutoriaUser.objects.create(username=username, password=password, firstname=firstName, lastname=lastName, gender=gender, phoneNumber=mobilePhone, email = email, isTutor = 1, isStudent = 0, isActive=1, balance = 0)
        newUser.save()
        if avatar is not None:
            newUser.avatar=avatar
            print("is not None")
            print(avatar)
        newUser.save()
        #tutor to db
        newTutor = Tutor.objects.create(user=newUser, university = universityObj, hourlyRate = hourlyRate, tutorType = int(tutorType), biography = biography)
        newTutor.save()
        

        for courses in courselist:
            courseObj=Course.objects.filter(courseCode=courses)[0]
            newTutor.courseCode.add(courseObj)
        newTutor.save()
        
        for tags in taglist:
            result=SubjectTag.objects.filter(tagName=tags)
            if result.count() > 0:
                newTutor.tags.add(result[0])
            else:
                tagObj = SubjectTag.objects.create(tagName = tags)
                tagObj.save()
                newTutor.tags.add(tagObj)
        newTutor.save()
    return render(request, "successRegistration.html", c)

@csrf_exempt
def registerNewStudent(request):
    c = {}
    if request.method == 'POST':
        #user
        firstName = request.POST.get('inputName_first', None)
        lastName = request.POST.get('inputName_last', None)
        username = request.POST.get('inputUsername', None)
        password = request.POST.get('inputPassword', None)
        email = request.POST.get('inputEmail', None)
        mobilePhone = request.POST.get('inputMobilePhone', None)
        gender = request.POST.get('selectGender', None)
        #validate check before updating db
        #check for repeat userID
        result = TutoriaUser.objects.filter(username=username)
        try:#if no avatar 
            avatar = request.FILES['inputAvatar']
        except KeyError:
            avatar = None
        if result.count() > 0:
            return render(request, "failRegistration_1.html", c)
        result = TutoriaUser.objects.filter(email=email)
        if result.count() > 0:
            return render(request, "failRegistration_2.html", c)
        #save to db
        newUser = TutoriaUser.objects.create(username=username, password=password, firstname=firstName, lastname=lastName, gender=gender, phoneNumber=mobilePhone, email = email, isTutor = 0, isStudent = 1, isActive=1, balance = 0)
        newUser.save()
        print("new user just created.. now create avatar...")
        if avatar is not None:
            newUser.avatar=avatar
            print("is not None")
            print(avatar)
        newUser.save()
        #student to db
        newStudent = Student.objects.create(user=newUser)
        newStudent.save()
    return render(request, "successRegistration.html", c)

@csrf_exempt
def registerNewStudentTutor(request):
    c = {}
    if request.method == 'POST':
        #user
        firstName = request.POST.get('inputName_first', None)
        lastName = request.POST.get('inputName_last', None)
        username = request.POST.get('inputUsername', None)
        password = request.POST.get('inputPassword', None)
        email = request.POST.get('inputEmail', None)
        mobilePhone = request.POST.get('inputMobilePhone', None)
        gender = request.POST.get('selectGender', None)
        #avatar = None
        try:
            avatar = request.FILES['inputAvatar']
        except KeyError:
            avatar = None
        #avatar = request.FILES('inputAvatar', False)
        tutorType = request.POST.get('selectTutorType', None)
        taglist = request.POST.getlist('inputTag', None)
        hourlyRate = request.POST.get('inputHourlyRate', None)
        if int(tutorType) == 1:
            if hourlyRate == None:
                hourlyRate = 0
        else:
            if hourlyRate == None:
                hourlyRate = 10
        biography = request.POST.get('inputBiography', None)
        courselist = request.POST.getlist('selectCourseCode')
        university = request.POST.get('selectUniversity', None)
        #validate check before updating db
        #check for repeat userID
        result = TutoriaUser.objects.filter(username=username)
        if result.count() > 0:
            return render(request, "failRegistration_1.html", c)
        result = TutoriaUser.objects.filter(email=email)
        if result.count() > 0:
            return render(request, "failRegistration_2.html", c)
        universityObj = University.objects.get(name = university)
        #save to db
        newUser = TutoriaUser.objects.create(username=username, password=password, firstname=firstName, lastname=lastName, gender=gender, phoneNumber=mobilePhone, email = email, isTutor = 1, isStudent = 1, isActive=1, balance = 0)
        newUser.save()
        if avatar is not None:
            newUser.avatar=avatar
        newUser.save()
        #student to db
        newStudent = Student.objects.create(user=newUser)
        newStudent.save()
        #tutor to db
        newTutor = Tutor.objects.create(user=newUser, university = universityObj, hourlyRate = hourlyRate, tutorType = int(tutorType), biography = biography )
        newTutor.save()
        

        for courses in courselist:
            courseObj=Course.objects.filter(courseCode=courses)[0]
            newTutor.courseCode.add(courseObj)
        newTutor.save()
        for tags in taglist:
            result=SubjectTag.objects.filter(tagName=tags)
            if result.count() > 0:#y exist
                newTutor.tags.add(result[0])
            else:
                tagObj = SubjectTag.objects.create(tagName = tags)
                tagObj.save()
                newTutor.tags.add(tagObj)
        newTutor.save()
    return render(request, "successRegistration.html", c)

@csrf_exempt
def usernameExist(request):
    username = request.POST.get('inputUsername')
    #check for repeat userID
    result = TutoriaUser.objects.filter(username=username)
    if result.count() > 0:
        return JsonResponse({'status':"Fail", 'msg':'username has been used by others'})
    return JsonResponse({'status':"success", 'msg':'ok'})

@csrf_exempt
def emailExist(request):
    email = request.POST.get('inputEmail')
    #check for repeat userID
    result = TutoriaUser.objects.filter(email=email)
    if result.count() > 0:
        return JsonResponse({'status':"Fail", 'msg':'email has been used by others'})
    return JsonResponse({'status':"success", 'msg':'ok'})
    
"""def checkRepeat(email,username):
   #check for repeat userID
    result = TutoriaUser.objects.filter(username=username)
    if result.count() > 0:
        return render(request, "failRegistration_1.html", c)
    result = TutoriaUser.objects.filter(email=email)
    if result.count() > 0:
        return render(request, "failRegistration_2.html", c)
    return None"""

"""@csrf_exempt
def send_emailNotification(subject, message, from_email, to_list):
    send_mail(subject, message, from_email, to_list, fail_silently = True)
    print ("to:"+to_list[0])
    print (subject)
    print (message)"""

@csrf_exempt
def generate_systemNotification(messages, userID):
    n = Notification.objects.create(userID=userID, notificationDetails=messages)
    n.save()

def forgetPassword(request):
    template = loader.get_template('forgetpassword.html');
    return HttpResponse(template.render(request))

#https://docs.python.org/3/library/secrets.html
@csrf_exempt
def validate_email(request):
    email_input = request.POST.get('email', None)
    if request.POST.get('type', None) == "adminResetPassword":
        id = request.POST.get('id', None)
        email_input = TutoriaUser.objects.get(pk=id).email
    href =  request.POST.get('href', None)#get the current href
    result = TutoriaUser.objects.filter(email=email_input)
    if result.count() > 0:#exist in the db
        userObj = TutoriaUser.objects.filter(email=email_input)[0]
        result2 = passwordToken.objects.filter(userID=userObj)
        if result2.count() > 0:#has existing token
            passwordToken.objects.filter(userID=userObj).delete()
        #else
        subject = "change your password"
        token = str(token_hex(32))
        #print (request.path)
        #message = "Dear "+userObj.firstname+"\n\nPlease follow the link below to reset your password:\n"+href+token+"\n\nRegards,\nTutoria Administrator"
        template = loader.get_template('email_templete/password_token.txt')
        d = Context({ 'firstname': userObj.firstname, 'href':href, 'token': token})
        text_content = template.render(d)
        from_email = settings.EMAIL_HOST_USER
        tok = passwordToken.objects.create(userID=userObj, token=token)
        tok.save()
        to_list = [ email_input ]
        emailNotification.send_emailNotification(subject, text_content, from_email, to_list)
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
@csrf_exempt
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

@csrf_exempt
def resetPassword(request, token):
    #get password from the form
    password_input = request.POST.get('password', None)
    #to get the userID back by the token
    result = passwordToken.objects.filter(token=token)
    userID = result[0].userID
    #update the password
    TutoriaUser.objects.select_related().filter(pk=userID.id).update(password=password_input)
    #delete the token after changing password
    passwordToken.objects.filter(userID=userID).delete()
    return JsonResponse({'status':'Success', 'msg': 'change successfully, check your email for the token'})
    
    
######################Admin####################
def adminIndex(request):
    if not request.session.has_key('AdminLogin'):
        return redirect('/tutoria/tutoria_admin/login')
    template = loader.get_template('tutoria_admin/index.html')
    return HttpResponse(template.render(), request)
    
def adminResetPasswordPage(request):
    if not request.session.has_key('AdminLogin'):
        return redirect('/tutoria/tutoria_admin/login')
    template = loader.get_template('tutoria_admin/reset_password.html')
    return HttpResponse(template.render(), request)

def controlUserRightPage(request):
    if not request.session.has_key('AdminLogin'):
        return redirect('/tutoria/tutoria_admin/login')
    template = loader.get_template('tutoria_admin/control_user_right.html')
    return HttpResponse(template.render(), request)

@csrf_exempt
def getUserList(request):
    page = int(request.POST.get('start', None))                                 #variable sent by datatable
    numOfDataToBeDisplay = int(request.POST.get('length', None))                #variable sent by datatable d
    allUser = TutoriaUser.objects.all()
    userList = allUser.order_by('id')[page:page+numOfDataToBeDisplay]
    type = request.POST.get('type', None)
    jsonResponse = []
    for user in userList:
        tempUser = [user.id, user.username, user.getFullName()]
        if type == 'userInfo':
            if user.isActive == 1:
                tempUser.append("Active")
            else:
                tempUser.append("Inactive")
            #tempUser.append('<a class="btn btn-primary btn-xl" href="javascript:void(0);" style="word-wrap:break-word;white-space:pre-wrap;">View Account Details</a>')
            tempUser.append('<a class="btn btn-primary btn-xl" href="javascript:void(0);" style="word-wrap:break-word;white-space:pre-wrap;">Control User Right</a>')
        elif type == 'resetPassword':
            tempUser.append('<a class="btn btn-primary btn-xl reset-password-btn" id="'+str(user.id)+'" href="javascript:reset('+str(user.id)+')" style="word-wrap:break-word;white-space:pre-wrap;">Reset Password</a>')
        elif type == 'changeUserRight':
            if user.isActive == 1:
                tempUser.append("Active")
                tempUser.append('<a class="btn btn-primary btn-xl reset-password-btn" id="'+str(user.id)+'" href="javascript:changeUserActiveStatus('+str(user.id)+')" style="word-wrap:break-word;white-space:pre-wrap;">Inactive</a>')
            else:
                tempUser.append("Inactive")
                tempUser.append('<a class="btn btn-primary btn-xl reset-password-btn" id="'+str(user.id)+'" href="javascript:changeUserActiveStatus('+str(user.id)+')" style="word-wrap:break-word;white-space:pre-wrap;">Active</a>')
        jsonResponse.append(tempUser)
    jsonr = json.dumps({'draw': 0, 'recordsTotal': allUser.count(), 'recordsFiltered': allUser.count(), "data": jsonResponse})
    return HttpResponse(jsonr,content_type='application/json')

@csrf_exempt
def changeUserActiveStatus(request):
    id = request.POST.get('id', None)
    user = TutoriaUser.objects.get(id=id)
    if user.isActive == 1:
        user.isActive = 0
    else:
        user.isActive = 1
    user.save()
    jsonr = json.dumps({'result': 'success'})
    return HttpResponse(jsonr,content_type='application/json')

def withdraw(request,userID):
    return_status = login_check(request, userID)
    if (return_status==1):
        true_id = request.session['userID']
        return redirect("/tutoria/"+str(true_id)+"/withdraw/")
    elif (return_status==2):
        return redirect("/tutoria/login")
    userObj = TutoriaUser.objects.filter(id=userID)[0]
    template = loader.get_template('withdrawMoney.html')
    balance = userObj.balance
    context = Context({
                      'userID': userObj.id,
                      'name': userObj.getFullName(),
                      'balance':balance,
                      'role':getRole(userID)
                      })
    return HttpResponse(template.render(context, request))
    
def adminCoupon(request):
    template = loader.get_template('tutoria_admin/coupon_code.html')
    return HttpResponse(template.render(request))

@csrf_exempt
def getCouponCode(request):
    page = int(request.POST.get('start', None))                                 #variable sent by datatable
    numOfDataToBeDisplay = int(request.POST.get('length', None))                #variable sent by datatable d
    allCouponCode = Coupon.objects.all()
    CouponCodeList = allCouponCode.order_by('id')[page:page+numOfDataToBeDisplay]
    jsonResponse = []
    for coupon in CouponCodeList:
        tempCouponCode = [coupon.couponCode, str(coupon.startTime), str(coupon.endTime)]
        jsonResponse.append(tempCouponCode)
    jsonr = json.dumps({'draw': 0, 'recordsTotal': allCouponCode.count(), 'recordsFiltered': allCouponCode.count(), "data": jsonResponse})
    return HttpResponse(jsonr,content_type='application/json')

@csrf_exempt
def addCouponPage(request):
    template = loader.get_template('tutoria_admin/addCoupon.html')
    return HttpResponse(template.render(request))
    
@csrf_exempt  
def gen_coupon(request):#need to change to ajax
    from_time =  request.POST.get('fromTime', None)
    to_time =  request.POST.get('toTime', None)
    if (from_time > to_time):  #validate date first!!
        print ("error")
        return JsonResponse({'status':'error','msg':'Not valid time input'})
    else:
        token = str(token_hex(3))#token of length 6
        #dF = datetime.strptime(from_time, '%Y-%m-%d')
        print (from_time)
        print (to_time)
        print (token)
        coupon = Coupon.objects.create(couponCode=token, startTime=from_time, endTime=to_time)
        coupon.save()
        return JsonResponse({'status':'Success', 'msg': 'generate successfully','start':from_time, 'end': to_time, 'token': token})

@csrf_exempt 
def manage_course(request):
    template = loader.get_template('tutoria_admin/course_code.html')
    #context = {'courseList': Course.objects.all()}
    return HttpResponse(template.render(request))

@csrf_exempt 
def getCourseCode(request):
    page = int(request.POST.get('start', None))                                 #variable sent by datatable
    numOfDataToBeDisplay = int(request.POST.get('length', None))                #variable sent by datatable d
    allCourseCodes = Course.objects.all()
    CourseCodeList = allCourseCodes.order_by('id')[page:page+numOfDataToBeDisplay]
    jsonResponse = []
    for courseCode in CourseCodeList:
        a = 1
        tempCourseCode = [courseCode.university.name, courseCode.courseCode, courseCode.courseName]
        tempCourseCode.append('<a class="btn btn-primary btn-xl reset-password-btn" id="'+str(courseCode.id)+'" href="javascript:deleteCourseCode('+str(courseCode.id)+')" style="word-wrap:break-word;white-space:pre-wrap;">Delete</a>')
        jsonResponse.append(tempCourseCode)
    jsonr = json.dumps({'draw': 0, 'recordsTotal': allCourseCodes.count(), 'recordsFiltered': allCourseCodes.count(), "data": jsonResponse})
    return HttpResponse(jsonr,content_type='application/json')

@csrf_exempt
def deleteCourseCode(request):
    courseCodeToBeDeleted = int(request.POST.get('CourseCodeID', None))
    Course.objects.filter(id=courseCodeToBeDeleted).delete()
    jsonr = json.dumps({'result': 'success'})
    return HttpResponse(jsonr,content_type='application/json')

def websocket_test(request,userID):
    template = loader.get_template('websocket/user_list.html')
    context = {'userID': userID}
    return HttpResponse(template.render(context,request))

@csrf_exempt
def add_course(request):
    #courseList = request.POST.getlist('inputCourse',None)
    code = request.POST.get('addCourseCode',None)
    name = request.POST.get('addCourse',None)
    universities = University.objects.all()[0]
    """for course in courseList:
        a = course.strip().split(":")
        #a[0]course code a[1] course name
        result = Course.objects.filter(courseCode=a[0])
        if result.count() == 0:#not exist in the db
            newCourse = Course.objects.create(courseCode=a[0], courseName=a[1], university=universities)
            newCourse.save()"""
    newCourse = Course.objects.create(courseCode=code, courseName=name, university=universities)
    newCourse.save()         
    return JsonResponse({'status':'Success', 'msg': 'generate successfully'})
    
def add_new_course(request):
    template = loader.get_template('tutoria_admin/AddCourse.html')
    return HttpResponse(template.render(request))
    
def messagePage(request,userID):
    return_status = login_check(request, userID)
    if (return_status==1):
        true_id = request.session['userID']
        return redirect("/tutoria/message/"+str(true_id))
    elif (return_status==2):
        return redirect("/tutoria/login")
    template = loader.get_template('chat_room.html')
    #conversations = getLastMessageAndFriendList(userID)
    context = {'userID': int(userID), 'role': getRole(userID)}
    return HttpResponse(template.render(context, request))

@csrf_exempt
def getLastMessageAndFriendList(request):
    userID = request.POST.get('userID', None)
    return_status = login_check(request, userID)
    if (return_status==1):
        true_id = request.session['userID']
        return redirect("/tutoria/messagePage/"+str(true_id)+"/")
    elif (return_status==2):
        return redirect("/tutoria/login")
    user = TutoriaUser.objects.get(id=userID)
    conversations = Conversation.objects.filter(Q(user1=user) | Q(user2=user))
    messages = Message.objects.filter(conversation__in=conversations)
    lastMessageAndFriendList = []
    for conversation in conversations:
        message = Message.objects.filter(conversation=conversation).order_by('-dateTime')[0]
        temp = {'receiverID': message.receiver.id, 'senderID': message.sender.id, 'receiverName': message.receiver.getFullName(), 'senderName': message.sender.getFullName(), 'dateTime': str(message.dateTime), 'content': message.content}
        lastMessageAndFriendList.append(temp)
    
    lastMessageAndFriendList = sorted(lastMessageAndFriendList, key=lambda k: k['dateTime'], reverse=True)
    jsonr = json.dumps(lastMessageAndFriendList)
    return HttpResponse(jsonr,content_type='application/json')

@csrf_exempt
def getMessageHistory(request):
    friendID = request.POST.get('friendID', None)
    userID = request.POST.get('userID', None)
    return_status = login_check(request, userID)
    if (return_status==1):
        true_id = request.session['userID']
        return redirect("/tutoria/messagePage/"+str(true_id)+"/")
    elif (return_status==2):
        return redirect("/tutoria/login")
    conversation = Conversation.objects.get((Q(user1=friendID) & Q(user2=userID)) | (Q(user1=userID) & Q(user2=friendID)))
    messageHistory = Message.objects.filter(conversation=conversation).order_by('dateTime')
    messages = []
    for message in messageHistory:
        messages.append({'receiverID': message.receiver.id, 'receiverName': message.receiver.getFullName(), 'senderID': message.sender.id, 'senderName': message.sender.getFullName(), 'dateTime': str(message.dateTime), 'content': message.content})
    jsonr = json.dumps({'messageHistory': messages})
    return HttpResponse(jsonr,content_type='application/json')
    
@csrf_exempt
def sendMessage(request):
    receiverID = request.POST.get('receiverID', None)
    senderID = request.POST.get('senderID', None)
    messageToBeSent = request.POST.get('messageToBeSent', None)
    receiver = TutoriaUser.objects.filter(id=receiverID)[0]
    sender = TutoriaUser.objects.filter(id=senderID)[0]
    conversation = Conversation.objects.filter((Q(user1=receiverID) & Q(user2=senderID)) | (Q(user1=senderID) & Q(user2=receiverID)))
    
    if conversation.count() == 0:
        newConversation = Conversation.objects.create(user1=sender, user2=receiver)
        newConversation.save()
        newMsg = Message.objects.create(conversation=newConversation, receiver=receiver, sender=sender, content=messageToBeSent)
        newMsg.save()
        consumers.sendMessage(senderID, receiverID, messageToBeSent, str(newMsg.dateTime), sender.getFullName(), receiver.getFullName())
        jsonr = json.dumps({'result': 'success'})
        return HttpResponse(jsonr,content_type='application/json')
    else:
        newMsg = Message.objects.create(conversation=conversation[0], receiver=receiver, sender=sender, content=messageToBeSent)
        newMsg.save()
        consumers.sendMessage(senderID, receiverID, messageToBeSent, str(newMsg.dateTime), sender.getFullName(), receiver.getFullName())
        jsonr = json.dumps({'result': 'success'})
        return HttpResponse(jsonr,content_type='application/json')
    
    jsonr = json.dumps({'result': 'fail'})
    return HttpResponse(jsonr,content_type='application/json')
    
def update_info(request):
    if request.method == 'POST':
        #user
        firstName = request.POST.get('inputName_first', None)
        lastName = request.POST.get('inputName_last', None)
        username = request.POST.get('inputUsername', None)
        email = request.POST.get('inputEmail', None)
        mobilePhone = request.POST.get('inputMobilePhone', None)
        gender = request.POST.get('selectGender', None)
        #validate check before updating db
        #check for repeat userID
        result = TutoriaUser.objects.filter(username=username)
        userID = request.POST.get('userID', None)
        result2 =  TutoriaUser.objects.filter(pk=userID)[0]
        
        try:#if no avatar 
            avatar = request.FILES['inputAvatar']
        except KeyError:
            avatar = None
        
        print avatar
        if result.count()>0:
            if result2.username != username :#not equal to the original
                return JsonResponse({'status':'Fail', 'msg': 'username exist'})
        result = TutoriaUser.objects.filter(email=email)
        if result.count()>0 :
            if result2.email != email :
                return JsonResponse({'status':'Fail', 'msg': 'email exist'})
        #save to db
        TutoriaUser.objects.filter(id=userID).update(username=username, firstname=firstName, lastname=lastName, gender=gender, phoneNumber=mobilePhone, email = email)

        if avatar is not None:
            TutoriaUser.objects.filter(id=userID).update(avatar=avatar)
        print (avatar)
    return JsonResponse({'status':'Success', 'msg': 'updated'})
    
def change_password(request):
    if request.method == 'POST':
        #user
        oldPassword = request.POST.get('inputOldPassword', None)
        newPassword = request.POST.get('inputPassword', None)
        userID = request.POST.get('userID', None)
        #check for old password
        result = TutoriaUser.objects.filter(id=userID)[0]
        if result.password != oldPassword:
            return JsonResponse({'status':'Fail', 'msg': 'old password not match'})
        TutoriaUser.objects.filter(id=userID).update(password=newPassword)
    return JsonResponse({'status':'Success', 'msg': 'updated'})

def update_tutor_info(request):
    if request.method == 'POST':
        #user
        userID = request.POST.get('userID', None)
        university = request.POST.get('selectUniversity', None)
        courselist = request.POST.getlist('selectCourseCode', None)
        taglist = request.POST.getlist('inputTag', None)
        tutorType = request.POST.get('selectTutorType', None)
        hourlyRate = request.POST.get('inputHourlyRate', None)
        activated = request.POST.get('inputActive', None)
        if hourlyRate == None :
            hourlyRate = 0
        Biography = request.POST.get('inputBiography', None)
        #validate check before updating db
        result = TutoriaUser.objects.filter(id=userID)[0]
        tutor = Tutor.objects.filter(user=result)[0]
        #check for repeat userID
        tutor.tags.clear()
        for tags in taglist:
            result=SubjectTag.objects.filter(tagName=tags)
            if result.count() > 0:
                tutor.tags.add(result[0])
            else:
                tagObj = SubjectTag.objects.create(tagName = tags)
                tagObj.save()
                tutor.tags.add(tagObj)
        tutor.save()
        
        tutor.courseCode.clear()
        for courses in courselist:
            courseObj=Course.objects.filter(courseCode=courses)[0]
            tutor.courseCode.add(courseObj)
        tutor.save()

        print ("tutor type:"+tutorType)
        universityObj = University.objects.get(name = university)
        Tutor.objects.filter(id=tutor.id).update(university=universityObj, tutorType=int(tutorType), hourlyRate=hourlyRate, biography=Biography, activated = int(activated))
        
        #userObj=TutoriaUser.objects.filter(id=userID)
        #userObj.update(isActive=int(isActive))

    return JsonResponse({'status':'Success', 'msg': 'updated'})
    
def admin_login(request):
    if request.session.has_key('AdminLogin'):
        return redirect('/tutoria/tutoria_admin/index')
    template = loader.get_template('tutoria_admin/admin_login.html')
    return HttpResponse(template.render())

@csrf_exempt    
def admin_validate(request):
    username = request.POST.get('username', None)
    password = request.POST.get('password', None)
    #check for validity first
    jsonr = Admin.validate_admin(username, password)
    resp = json.loads(jsonr)
    if resp['isValid']:
        request.session['AdminLogin'] = 1
    return HttpResponse(jsonr,content_type='application/json')
    
def logout_admin(request):#call when logout
    if request.session.has_key('AdminLogin'):
        del request.session['AdminLogin']
    return redirect('/tutoria/index')

def logout_session(request):#call when logout
    if request.session.has_key('userID'):
        del request.session['userID']
    return redirect('/tutoria/index')
                
def login_check(request,userID):#called in every logged in page return the status for checking 
    if request.session.has_key('userID'):
        session_userid = int(request.session['userID'])
        if session_userid == int(userID):#same as userid
            return 0
        else:#login but different userID
            return 1
    else:#not logined
        return 2