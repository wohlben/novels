//$(document).ready(function() {
//   $(".navbar-burger").click(function() {
//       $(".navbar-burger").toggleClass("is-active");
//       $(".navbar-menu").toggleClass("is-active");
//   });
// });

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

$(function(){
  $(document).on('beforeAjaxSend.ic', function(event, ajaxSetup, elt){
    ajaxSetup.headers['X-CSRFToken'] = Cookies.get('csrftoken');
  });
});


