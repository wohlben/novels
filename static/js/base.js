//$(document).ready(function() {
//   $(".navbar-burger").click(function() {
//       $(".navbar-burger").toggleClass("is-active");
//       $(".navbar-menu").toggleClass("is-active");
//   });
// });


function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            const csrf_token = Cookies.get('csrftoken');
            xhr.setRequestHeader("X-CSRFToken", csrf_token);
        }
    }
});

function resetTextSize(){
    try {
        window.fontSize = parseInt(Cookies.get("font-size"), 10);
        if (isNaN(window.fontSize)) {
            window.fontSize = 100;
        }
    } catch (e) {
        window.fontSize = 100;
    }
    document.getElementById("chapter-content").style.fontSize = window.fontSize + '%';
}
function resizeText (bigger) {
    if (bigger === true) {
        step = 1;
    } else {
        step = -1;
    }
    window.fontSize = window.fontSize * Math.pow(1.2, step);
    document.getElementById("chapter-content").style.fontSize = window.fontSize + '%';
    Cookies.set('font-size', window.fontSize);
    console.log(Cookies.get('font-size'));
}

function setGetParam(key, value = undefined){
    var url = new URL(window.location);
    var query_string = url.search;
    var search_params = new URLSearchParams(query_string);
    search_params.delete(key);
    if(value !== undefined){
      search_params.append(key, value);
    };
    url.search = search_params.toString();
    window.location.href = url.toString();
}

function getScrollPercentage(){
    const total_height = $(document).height();
    const current_position = $(window).scrollTop() + $(window).height();
    return Math.round(current_position / total_height * 100);
}

function scrollToPercentage(percentage){
    const total_height = $(document).height();
    const target_position = (total_height / 100 * percentage) - $(window).height();
    console.log('scrolled to ' + percentage + ' %')
    $(window).scrollTop(target_position);
}

function submitScrollPosition(callback=null) {
    const position = getScrollPercentage();
    const reading_progress = window.progress_id;
    const request = {
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        },
        url: '/api/progress/' + reading_progress + '/',
        type: 'PATCH',
        data: JSON.stringify({'chapter_id': window.chapter_id, 'progress': position}),
        success: function(){
            if(callback !== null ){
                callback()
            } else {
                console.log('submitted ' + position + ' %');
            }

        },
        error: function (jqXhr, textStatus, errorThrown) {
            console.log('couldnt update progress');
            return errorThrown;
        }
    };
    $.ajax(request);
}



