# DjangoWebsite

It is a group assignment for software engineering course. Not for business use.

## About this tutor-broking system demo:
### 1. Booking a tutorial session via the platform:
Tutoria provides a booking interface, by implementing the [dhtmlxScheduler schedular API](https://docs.dhtmlx.com/scheduler/api__refs__scheduler.html) with use of AJAX and JSON, working with the python back-end coding, to finish the necessary functions.
### 2. Real-time notification acknowledgement.
Tutoria provides real-time notification, which will be triggered by certain activities without refreshing the browser. This part is implemented by [websocket.js](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_client_applications).
### 3. Automatically close the session and transfer the payment after finishing a tutorial session.
Tutoria wants to make an effort to give the most efficient transaction. This part is implemented by [Celery API](http://www.celeryproject.org/) for Django, to update the database automatically.
### 4. [Instant messenger](https://github.com/Felixho19/DjangoWebsite/blob/master/template/chat_room.html)
Tutoria provides a messenger for students to communicate with tutors instantly. This part is implemented by AJAX and JSON, working with the python back-end coding, to finish the necessary functions. 
