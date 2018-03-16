# DjangoWebsite

It is a group assignment for software engineering course. Not for business use.

## About this tutor-broking system demo:
### 1. Booking a tutorial session via the platform:
Tutoria provides a booking interface, by implementing the [dhtmlxScheduler schedular API](https://docs.dhtmlx.com/scheduler/api__refs__scheduler.html) with use of AJAX and JSON, to finish the necessary functions.
### 2. Real-time notification acknowledgement.
Tutoria provides real-time notification, which will be triggered by certain activities without refreshing the browser. This part is implemented by [websocket.js](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_client_applications).
### 3. Automatically close the session and transfer the payment after finishing a tutorial session.
Tutoria wants to make the effort to give the most efficient way for transaction. This part is implemented by [Celery API](http://www.celeryproject.org/) for Django.
