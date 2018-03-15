var userID = $("#userID").val();

var socket = new WebSocket('wss://' + window.location.host + '/' + userID);
socket.onopen = function open() {
    console.log('WebSockets connection created.');
    socket.send("hello");
};

if (socket.readyState == WebSocket.OPEN) {
    socket.onopen();
}

socket.onmessage = function message(event) {
    data = event.data;
    jsonData = JSON.parse(data);
    console.log(data);
    if(jsonData['type'] == 'notificationUpdate') {
        $("#notificationAlert").show();
        $.notify(jsonData['details'] ,{autoHideDelay: 10000, className: 'info'});
    }else if(jsonData['type'] == 'endSessionNotification') {
        $("#notificationAlert").show();
        $.notify(jsonData['details'] ,{autoHideDelay: 10000, className: 'info'});
    }else if(jsonData['type'] == 'reviewReminderNotification') {
        $("#notificationAlert").show();
        $.notify(jsonData['details'] ,{autoHideDelay: 10000, className: 'info'});
    }
    
    if(jsonData['type'] == 'message' && $("#chatArea").length != 0) {
        txt = "";
        if(jsonData['senderID'] == userID) {
            txt += "<li class=\"right clearfix\">";
            txt += "<div class=\"chat-body clearfix\">";
            txt += "<div class=\"header\">";
            txt += "<strong class=\"primary-font\">"+jsonData['senderName']+"</strong>";
            txt += "<small class=\"pull-right text-muted\"><i class=\"fa fa-clock-o\"></i> "+jsonData['dateTime']+"</small>";
            txt += "</div>";
            txt += "<p>";
            txt += jsonData['content'];
            txt += "</p>";
            txt += "</div>";
            txt += "</li>";
        }else{
            txt += "<li class=\"left clearfix\">";
            txt += "<div class=\"chat-body clearfix\">";
            txt += "<div class=\"header\">";
            txt += "<strong class=\"primary-font\">"+jsonData['senderName']+"</strong>";
            txt += "<small class=\"pull-right text-muted\"><i class=\"fa fa-clock-o\"></i> "+jsonData['dateTime']+"</small>";
            txt += "</div>";
            txt += "<p>";
            txt += jsonData['content'];
            txt += "</p>";
            txt += "</div>";
            txt += "</li>";
        }
        $("#chatArea").append(txt);
        $(".messageArea").scrollTop($(".messageArea")[0].scrollHeight);
        
    }
    
}