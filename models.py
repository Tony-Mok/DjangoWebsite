from __future__ import unicode_literals
from datetime import date,datetime
from datetime import timedelta
from django.db import models
import json
from django.db.models import Avg
import decimal
from django.db.models import Q
from . import consumers
from django.template import Context, Template
from django.template import loader
from . import emailNotification
from django.conf import settings

GENDER_LIST = (
    ('Male', 'Male'),
    ('Female', 'Female'),
)
ZEROONE_LIST = (
    (0,0),
    (1,1)
)
TUTOR_TYPE = (
    (0, 0),
    (1, 1),
)
DESCRIPTION_LIST=(
    ('0', 'addCoins'),
    ('1', 'removeCoins'),
    ('2', 'sessionPayment'),
    ('3', 'sessionSalary'),
    ('4', 'sessionRefund'),
)

def get_image_name(instance, filename):
    return "%s_%s" %(instance.id, filename)

class TutoriaUser(models.Model):#added
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    avatar = models.ImageField(upload_to=get_image_name, null=True, blank=True)
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    gender = models.CharField(max_length=255, choices=GENDER_LIST)
    phoneNumber = models.IntegerField()
    email = models.EmailField()
    isActive = models.IntegerField(choices=ZEROONE_LIST)
    isStudent = models.IntegerField(choices=ZEROONE_LIST)
    isTutor = models.IntegerField(choices=ZEROONE_LIST)
    balance = models.DecimalField(max_digits=255, decimal_places=1)
    
    def __str__(self):
        return self.username
    
    @classmethod
    def validate_user(cls, username, password):
        user = TutoriaUser.objects.filter(username=username, password=password)
        if user.count() == 1:
            jsonr = json.dumps({ 'isValid': True, 'id': user[0].id, 'isStudent': user[0].isStudent, 'isTutor': user[0].isTutor})
        else:
            jsonr = json.dumps({ 'isValid': False })
        return jsonr

    def getFullName(self):
        return str(self.firstname) + ' ' + str(self.lastname)
    
    def checkSessions(self):
        currentDate = datetime.now()
        tutorUserObj = self #blackout
        tutorObj = Tutor.objects.filter(user=tutorUserObj)[0]
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
                
        if(tutorObj.tutorType==0):
            for (k,lt) in results2:       
                for i in range(0,24):
                    if not lt[i]:
                        return True
        else:
            for (k,lt) in results2:       
                for i in range(0,48):
                    if not lt[i]:
                        return True
        return False
'''        
class Department(models.Model):#added
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name
'''
class University(models.Model):#added
    name = models.CharField(max_length=255)
    #department = models.ManyToManyField(Department)
    def __str__(self):
        return self.name

class Course(models.Model):#added
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    #department = models.ForeignKey(Department, on_delete=models.CASCADE)
    courseCode = models.CharField(max_length=255)
    courseName = models.CharField(max_length=255)
    def __str__(self):
        return str(self.courseCode) + ' ' + str(self.courseName)
     
class SubjectTag(models.Model):#added
    tagName = models.CharField(max_length=255)
    def __str__(self):
        return self.tagName
    
class Student(models.Model):#added
    user = models.ForeignKey(TutoriaUser, on_delete=models.CASCADE)
    def __str__(self):
        return self.user.username
        

'''        
def get_image_name(instance, filename):
    return "%s_%s" %(instance.user.id, filename)
'''
    
class Tutor(models.Model):#added
    user = models.ForeignKey(TutoriaUser, on_delete=models.CASCADE)
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    hourlyRate = models.IntegerField()
    #tutorAvatar = models.ImageField(upload_to=get_image_name, null=True, blank=True)
    tutorType = models.IntegerField(choices=TUTOR_TYPE)
    biography = models.TextField()
    courseCode = models.ManyToManyField(Course, null=True, blank=True)
    tags = models.ManyToManyField(SubjectTag, null=True, blank=True)
    #reviews = models.ManyToManyField(Review, null=True, blank=True)
    score = models.DecimalField(max_digits=2, decimal_places=1, default=1.0)
    activated = models.IntegerField(choices=ZEROONE_LIST, default=1)
    def __str__(self):
        return self.user.username
    
    @classmethod
    def getTutorList(cls, userID, page, numOfDataToBeDisplay, filters):
        #users = TutoriaUser.objects.filter(firstname__icontains=filters['firstName'])
        #allTutor = Tutor.objects.filter(user__in=users)
        firstnameFilter = filters['firstName']
        lastnameFilter = filters['lastName']
        
        subjectTagFilter = filters['inputSubjectTag']
        taglist = SubjectTag.objects.filter(tagName__icontains=subjectTagFilter)
        minHourlyRateFilter = int(filters['inputMinHourlyRate'].strip() or 0)
        maxHourlyRateFilter = int(filters['inputMaxHourlyRate'].strip() or 0)
        universitiesFilter = filters['university']
        tutorTypeFilter = filters['selectTutorType']
        courseCodeFilter = filters['selectCourseCode']
        selectSorting = filters['selectSorting'] # 0 = sort for hourly rate, 1 = sort for score
        allTutor = Tutor.objects.all()
        users = TutoriaUser.objects.filter(firstname__icontains=firstnameFilter, lastname__icontains=lastnameFilter)
        #allTutor = Tutor.objects.filter(Q(hourlyRate__gte=minHourlyRateFilter) & Q(hourlyRate__lte=maxHourlyRateFilter), user__in=users, university__in=universitiesFilter )
        if users is not []:
            allTutor = allTutor.filter(user__in=users)
        if minHourlyRateFilter is not None and maxHourlyRateFilter is not None:
            if minHourlyRateFilter < maxHourlyRateFilter:
                allTutor = allTutor.filter(Q(hourlyRate__gte=minHourlyRateFilter) & Q(hourlyRate__lte=maxHourlyRateFilter))
        if len(subjectTagFilter) > 0:
            allTutor = allTutor.filter(tags__in=taglist)
        
        if len(universitiesFilter)>0:
            allTutor = allTutor.filter(university__in=universitiesFilter)
        
        if len(tutorTypeFilter) > 0:
            allTutor = allTutor.filter(tutorType__in=tutorTypeFilter)
        
        if len(courseCodeFilter) > 0:
            allTutor = allTutor.filter(courseCode__in=courseCodeFilter)
        
        #allTutor=allTutor.objects.distinct()
        allTutor = allTutor.filter(user__isActive=1).distinct()
        allTutor = allTutor.filter(activated=1).distinct()
        #default
        tutorList = allTutor.order_by('id')[page:page+numOfDataToBeDisplay]
        #sort type 1
        for i in selectSorting:
            if int(i) == 0:
                tutorList = allTutor.order_by('-hourlyRate')[page:page+numOfDataToBeDisplay]
        #sort type 2
            if int(i) == 1:
                tutorList = allTutor.order_by('-score')[page:page+numOfDataToBeDisplay]
            if int(i) == 2:
                print allTutor.count()
                ids = [tutor.user for tutor in allTutor if tutor.user.checkSessions()]
                tutorList = allTutor.filter(user__in=ids)
                print tutorList.count()

        jsonResponse = []

        for tutor in tutorList:
            tutorReviewList = Review.objects.filter(tutor=tutor)
            tutorAvgReview=tutorReviewList.aggregate(Avg('rating')).get('rating__avg', 0.0)
            tempTutor = [str(tutor.user.getFullName()), tutor.user.gender, str(tutor.university.name), tutor.hourlyRate]
            subtag = '<ul>'
            tags = SubjectTag.objects.filter(tutor=tutor)
            for tag in tags:
                subtag += '<li>'+tag.tagName+'</li>'
            subtag += '</ul>'
            tempTutor.append(subtag)
            if len(tutorReviewList) < 3:
                tempTutor.append('No Ratings')
                '''
                tutor.score = -1.0
                tutor.save()'''
            else:
                '''
                tutor.score = tutorAvgReview
                tutor.save()
                '''
                tempTutor.append('<div class="star-ratings-sprite"><span style="width:'+str(tutorAvgReview*20)+'%" class="star-ratings-sprite-rating"></span></div>')
            #bookingLink = str(str(userID)+"/student_booking/"+str(tutor.user.id))
            bookingLink = str("/tutoria/"+str(userID)+"/student_booking/"+str(tutor.user.id))
            profileLink = str("/tutoria/"+str(userID)+"/student_tutor_profile/"+str(tutor.user.id))
            tempTutor.append('<center><a class="btn btn-primary btn-xl js-scroll-trigger" href="'+profileLink+'" style="word-wrap:break-word;white-space:pre-wrap;">Tutor Details</a></center>')
            tempTutor.append('<center><a class="btn btn-primary btn-xl js-scroll-trigger" href="'+bookingLink+'" style="word-wrap:break-word;white-space:pre-wrap;">Book</a></center>')
            jsonResponse.append(tempTutor)
        
        jsonr = json.dumps({'draw': 0, 'recordsTotal': allTutor.count(), 'recordsFiltered': allTutor.count(), "data": jsonResponse})
        return jsonr
    
    def getHourlyrate(self):
        return self.hourlyRate
    
    
class Admin(models.Model):#added
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    isActive = models.IntegerField(choices=ZEROONE_LIST)
    def __str__(self):
        return self.username
        
    @classmethod
    def validate_admin(cls, username, password):
        user = Admin.objects.filter(username=username, password=password)
        if user.count() == 1:
            jsonr = json.dumps({ 'isValid': True})
        else:
            jsonr = json.dumps({ 'isValid': False })
        return jsonr
    
class Notification(models.Model):#added
    user = models.ForeignKey(TutoriaUser, on_delete=models.CASCADE)
    notificationDetails = models.CharField(max_length=255)
    dateTime = models.DateTimeField(auto_now_add=True, blank=True)
    isRead = models.BooleanField(default=False)
    
    @classmethod
    def generate_systemNotification(cls, user, notificationDetails):
        notification = cls(user=user, notificationDetails=notificationDetails)
        notification.save()
        consumers.ws_sendNotificationAlert(user.id, notificationDetails)
        
    @classmethod
    def getNotification(cls, userID, page, numOfDataToBeDisplay):
        allNotifications = Notification.objects.filter(user=userID).order_by('-id')
        notificationList = allNotifications.order_by('-id')[page:page+numOfDataToBeDisplay]
        jsonResponse = []
        for notification in notificationList:
            dateTime = notification.dateTime
            notificationDetail = notification.notificationDetails
            tempNotification = [dateTime.strftime('%Y-%m-%d %H:%M:%S'), notificationDetail]
            jsonResponse.append(tempNotification)
        jsonr = json.dumps({'draw': 0, 'recordsTotal': allNotifications.count(), 'recordsFiltered': allNotifications.count(), "data": jsonResponse})
   
        return jsonr
        
class Conversation(models.Model):
    user1 = models.ForeignKey(TutoriaUser, on_delete=models.CASCADE, related_name='user1')
    user2 = models.ForeignKey(TutoriaUser, on_delete=models.CASCADE, related_name='user2')
    
    def __str__(self):
        return str(self.user1.username) + " " + str(self.user2.username)
    
class Message(models.Model):#added
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    receiver = models.ForeignKey(TutoriaUser, on_delete=models.CASCADE, related_name='message_receiver')
    sender = models.ForeignKey(TutoriaUser, on_delete=models.CASCADE, related_name='message_sender')
    content = models.CharField(max_length=255)
    dateTime = models.DateTimeField(auto_now_add=True, blank=True)
    
    def __str__(self):
        return str(self.sender.username) + " sends to " + str(self.receiver.username)
    
class Coupon(models.Model):#added
    couponCode = models.CharField(max_length=255)
    startTime = models.DateTimeField()
    endTime = models.DateTimeField()
    
class BlackOutTimeSlot(models.Model):#added
    user = models.ForeignKey(TutoriaUser, on_delete=models.CASCADE)
    bdate = models.DateField()
    startTime = models.TimeField()
    endTime = models.TimeField()
    
class Booking(models.Model):#added
    STATUS_LIST = (
        ('booked', 'booked'),
        ('locked', 'locked'),
        ('in progress', 'in progress'),
        ('completed', 'completed'),
        ('reviewed', 'reviewed'),
    )
    date = models.DateField()
    startTime = models.TimeField()
    endTime = models.TimeField()
    status = models.CharField(max_length=255, choices=STATUS_LIST, null=True, blank=True)
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return str(self.date) + ' ' + str(self.startTime) + ' ' +str(self.endTime)

    @classmethod
    def bookASession(cls, date, startTime, endTime, student, tutor, coupon):
        checkExist = (Booking.objects.filter(date=date, startTime=startTime, endTime=endTime, tutor=tutor).count() == 0)
        S = TutoriaUser.objects.get(id = student.user.id)
        T = TutoriaUser.objects.get(id = tutor.user.id)
        start = datetime.strptime(date+' '+startTime, '%Y-%m-%d %H:%M')
        currentTime = datetime.now()
        #if diff>=1:
        #    jsonr = json.dumps({'result': 4})
        #    return jsonr
        #checkSelf = (TutoriaUser.model.gets(pk=student) == TutoriaUser.model.gets(pk=tutor))
        checkDuplicate = (Booking.objects.filter(date=date, student=student).count() == 0)
        payment = tutor.hourlyRate*1.05
        c = None;
        if Coupon.objects.filter(couponCode=coupon).count() > 0:
            c = Coupon.objects.filter(couponCode=coupon)[0]
            if c.startTime <= currentTime and c.endTime >= currentTime:
                payment = tutor.hourlyRate
        checkWallet = (student.user.balance >= payment)
        if checkWallet is False:
            jsonr = json.dumps({'result': 2})
            return jsonr
        if S==T:
            jsonr = json.dumps({'result': 5})
            return jsonr
        if checkExist is False:
            jsonr = json.dumps({'result': 0})
            return jsonr
        elif checkDuplicate is False:
            jsonr = json.dumps({'result': 3})
            return jsonr
        else:
            bookingRecord = cls(date = date, startTime = startTime, endTime = endTime, status = 'booked',tutor = tutor, student = student)
            bookingRecord.save()
            if tutor.tutorType == 0:
                transactionRecord = Transaction.create(student.user, bookingRecord, 'booking', -payment, c)
                transactionRecord.save()
                student.user.balance -= decimal.Decimal(payment)
                student.user.save()
            notificationDetails = "You have booked the tutorial session " + str(bookingRecord.id) + ". Go to \'Menu > View/Cancel Booked Sessions > Detail\' to view your tutor's contact details."
            Notification.generate_systemNotification(student.user, notificationDetails)
            notificationDetails = student.user.getFullName() + " has booked the tutorial session " + str(bookingRecord.id)
            Notification.generate_systemNotification(tutor.user, notificationDetails)
            #email notification
            #to tutor
            template = loader.get_template('email_templete/booking_tutor.txt')
            subject = "A student has booked your session"
            d = Context({ 'tutor_name': tutor.user.firstname, 'student_phoneNumber':tutor.user.phoneNumber, 'date':date, 'startTime': startTime, 'endTime': endTime, 'sID':bookingRecord.id, 'student_name': student.user.getFullName()})
            text_content = template.render(d)
            from_email = settings.EMAIL_HOST_USER
            to_list = [ tutor.user.email ]
            emailNotification.send_emailNotification(subject, text_content, from_email, to_list)
            #email to student
            subject = "Session booking comfirmation"
            template = loader.get_template('email_templete/booking_student.txt')
            d = Context({ 'student_name': student.user.firstname, 'date':date, 'startTime': startTime, 'endTime': endTime, 'sID':bookingRecord.id, 'tutor_name':tutor.user.getFullName(),
                'tutor_phoneNumber':tutor.user.phoneNumber
            })
            text_content = template.render(d)
            from_email = settings.EMAIL_HOST_USER
            to_list = [ student.user.email ]
            emailNotification.send_emailNotification(subject, text_content, from_email, to_list)
            jsonr = json.dumps({'result': 1})
            return jsonr
    
    
    @classmethod
    def getBooking(cls, userID, page, numOfDataToBeDisplay):
        allBookedSession = Booking.objects.filter(student__user__id=userID, status='booked')
        bookedSessionList = allBookedSession.order_by('-id')[page:page+numOfDataToBeDisplay]
        jsonResponse = []
        for bookedSession in bookedSessionList:
            sessionID = bookedSession.id
            studentUserID=bookedSession.student.user.id
            date = str(bookedSession.date)
            startTime = str(bookedSession.startTime)
            endTime = str(bookedSession.endTime)
            tutorName = bookedSession.tutor.user.getFullName()
            detailBtn = '<a class="btn btn-primary btn-xl js-scroll-trigger" id="'+str(sessionID)+'" href="/tutoria/'+str(studentUserID)+'/session_detail/'+str(sessionID)+'" style="word-wrap:break-word;white-space:pre-wrap;">Detail</a>'
            cancelBtn = '<a class="btn btn-primary btn-xl js-scroll-trigger cancelSession" id="'+str(sessionID)+'" href="javascript:cancelBooking('+str(sessionID)+');" style="word-wrap:break-word;white-space:pre-wrap;">Cancel</a>'
            tempSession = [sessionID, date, startTime, endTime, tutorName,detailBtn, cancelBtn]
            jsonResponse.append(tempSession)
        jsonr = json.dumps({'draw': 0, 'recordsTotal': allBookedSession.count(), 'recordsFiltered': allBookedSession.count(), "data": jsonResponse})
        return jsonr
    
class Review(models.Model):#added
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.CharField(max_length=255, null=True, blank=True)
    anonymous = models.BooleanField(default=False)
    
class Transaction(models.Model):#added
    user = models.ForeignKey(TutoriaUser, on_delete=models.CASCADE)
    booking = models.ForeignKey(Booking, null=True, blank=True)
    description = models.CharField(max_length=2, choices=DESCRIPTION_LIST, null=True, blank=True)
    otherParty = models.CharField(max_length=255, null=True, blank=True)
    amount = models.DecimalField(max_digits=255, decimal_places=1)
    dateTime = models.DateTimeField(auto_now_add=True, blank=True)
    couponCode = models.ForeignKey(Coupon, null=True, blank=True)
    isProcessed = models.BooleanField(default=False)
    commision = models.DecimalField(max_digits=255, decimal_places=1, default=0)
    
    def cancelBooking(self):
        #current Trans record handling
        NeedToRefund = -1*self.amount
        #user updating balance handling
        Customer = self.user
        Customer.balance += NeedToRefund
        buffer = TutoriaUser.objects.get(id=Customer.id)
        buffer.balance = Customer.balance
        self.isProcessed = True
        #booking record handling
        buffer2 = Booking.objects.get(id=self.booking.id)
        Transaction.create(buffer, self.booking,'sessionRefund',NeedToRefund,None)
        self.booking = None
        buffer.save()
        self.save()
        return True
    
    @classmethod
    def create(cls,user,booking,desc,amount,couponCode):
        MyTutor = TutoriaUser.objects.filter(username='MyTutor')[0]
        if user == MyTutor:
            trans = cls(user=MyTutor ,booking = booking, description = '3',amount = amount,couponCode = couponCode, isProcessed = True)
            trans.save()
            return trans
        if amount >=0:
            message = "$"+str(int(round(amount))) + " has been added to your wallet"
        else:
            message = "$"+str(int(round(-amount))) + " has been withdrawn from your wallet" 
        #n= Notification.objects.create(user=user, notificationDetails=message)
        #n.save()
        #print ("hello2")
        print (message)
        Notification.generate_systemNotification(user, message)
        if desc == 'booking':
            trans = cls(user=user ,booking = booking, description = '2',amount = amount,couponCode = couponCode, isProcessed = False, otherParty=str(booking.tutor.user.getFullName()),commision=booking.tutor.hourlyRate)
            trans.save()
            return trans
        if desc == 'sessionSalary':
            trans = cls(user=user ,booking = booking, description = '3',amount = amount,couponCode = couponCode, isProcessed = True, otherParty=str(booking.tutor.user.getFullName()))
            trans.save()
            return trans
        if desc == 'sessionRefund':
            trans = cls(user=user ,booking = None, description = '4',amount = amount,couponCode = couponCode, isProcessed = True, otherParty=str(booking.tutor.user.getFullName()))
            trans.save()
            return trans
        if desc == 'addCoins':
            trans = cls(user = user,booking = None,amount = amount,couponCode = None, description = '0', isProcessed=True)
            user.balance += amount
            user.save()
            trans.save()
            return trans
        if desc == 'removeCoins':
            trans = cls(user = user,booking = None,amount = amount,couponCode = None, description = '1', isProcessed=True)
            user.balance += amount
            user.save()
            trans.save()
            return trans
        
        return None
    
'''class Payment(models.Model):
    user = models.ForeignKey(TutoriaUser, on_delete=models.CASCADE)
    paymentAmount = models.DecimalField(max_digits=255, decimal_places=1)'''

class passwordToken(models.Model):
    userID = models.ForeignKey(TutoriaUser, on_delete=models.CASCADE)
    token = models.CharField(max_length=255)
    createDate = models.DateField(default=date.today)
    
