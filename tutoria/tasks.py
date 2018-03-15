# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from .models import *
from datetime import datetime as dt
import datetime
import time
import decimal
from django.db.models import Q
from . import consumers

@shared_task
def payToTutor():
    hourNow = dt.now().hour
    todayDate = datetime.date.today()
    #bookings = Booking.objects.filter((Q(date__lte=todayDate)) | (Q(date=todayDate) & Q(endTime__lte=datetime.time(hourNow,0))), status='locked')
    bookings = Booking.objects.filter(status='locked')
    for booking in bookings:
        print booking.id
        booking.status = 'completed'
        #print Transaction.objects.filter(booking=booking,isProcessed=False).count()>0
        if Transaction.objects.filter(booking=booking,isProcessed=False).count()>0:
            trans = Transaction.objects.filter(user=booking.student.user,booking=booking,description='2')[0]
            c = trans.couponCode
            trans.isProcessed = True
            user = TutoriaUser.objects.get(id=booking.tutor.user.id)
            print user
            payment = decimal.Decimal(-1*trans.amount)
            payment_myTutor = decimal.Decimal(payment-trans.commision)
            payment_tutor = decimal.Decimal(payment-payment_myTutor)
            print payment_tutor
            print payment_myTutor
            print trans.commision
            #create a transaction record to tutor.
            Transaction.create(booking.tutor.user, booking,'sessionSalary', decimal.Decimal(payment_tutor),None).save()
            #update tutor balance.
            user.balance += decimal.Decimal(payment_tutor)
            if c is None:
                MyTutor = TutoriaUser.objects.filter(username='MyTutor')[0]
                Transaction.create(MyTutor, booking, 'sessionSalary', decimal.Decimal(payment_myTutor),None).save()
                MyTutor.balance += decimal.Decimal(payment_myTutor)
                MyTutor.save()
            trans.save()
            user.save()
            booking.save()
            consumers.sendEndSessionNotification(booking.student.user.id, booking.id)
            consumers.sendEndSessionNotification(booking.tutor.user.id, booking.id)
            consumers.sendReviewReminderNotification(booking.student.user.id, booking.id)

@shared_task
def lockSession():
    hour = dt.now().hour+24
    datetoday = datetime.date.today()
    dateNext = datetoday
    hourNext = hour
    if hour >= 24:
        hourNext = hour%24
        dateNext += datetime.timedelta(days=1)
    #bookings = Booking.objects.filter(Q(date=datetoday) & Q(startTime__lte=datetime.time(23,59)), Q(date=dateNext) & Q(startTime__lte=datetime.time(hourNext,0)), status='booked')
    bookings = Booking.objects.filter((Q(date=datetoday) & Q(startTime__lte=datetime.time(23,59))) | (Q(date=dateNext) & Q(startTime__lte=datetime.time(hourNext,0))), status='booked')
    for booking in bookings:
        booking.status = 'locked'
        booking.save()

