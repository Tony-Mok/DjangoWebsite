from django.core.mail import send_mail

def send_emailNotification(subject, message, from_email, to_list):
    #send_mail(subject, message, from_email, to_list, fail_silently = True)
    print ("to:"+to_list[0])
    print (subject)
    print (message)