function validate_user() {
    var form = $("#login-form");

    $.ajax({
        url: 'validate_user',
        data: form.serialize(),
        type: 'POST',
        dataType: 'json',
        success: function (response) {
            if(response.isValid == true) {
                if(response.isStudent == 1 && response.isTutor == 0) {
                    window.location = response.id + "/student_home/";
                }else if(response.isStudent == 0 && response.isTutor == 1) {
                    window.location = response.id + "/tutor_home/";
                }else if(response.isStudent == 1 && response.isTutor == 1){
                    window.location = response.id + "/tutor_home/";
                }else{
                    console.log("hihihi");
                    window.location = response.id + "/wallet/";
                }
                
            }else{
                alert("invalid username or password");
            }
        },
        error: function (error) {
            console.log(error);
        }
    });
}

function blackTimeSlot(session,sd,st,et){
    $.ajax({
    url: 'blackTimeSlot',
    data: {user: session,b_date: sd,start_time: st,end_time: et},
    type: 'POST',
    dataType:'json',
    success: function (response) {
            console.log(response.result);
    },
    error: function (error) {
            console.log(error);
        }
    });
}

function getSessions() {
    
    $.ajax({
        url: 'getSessions',
        data: {tutorID: 1},
        type: 'POST',
        dataType: 'json',
        success: function (response) {
            console.log(response.result);
            //return response.result;
        },
        error: function (error) {
            console.log(error);
        }
    });
}

$.ajaxSetup({ 
    beforeSend: function(xhr, settings) {
        function getCookie(name) {
            var cookieValue = null;
            if (document.cookie && document.cookie != '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = jQuery.trim(cookies[i]);
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) == (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
        
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
     } 
});

$(function() {
    function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');
});

