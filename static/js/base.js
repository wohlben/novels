//$(document).ready(function() {
//   $(".navbar-burger").click(function() {
//       $(".navbar-burger").toggleClass("is-active");
//       $(".navbar-menu").toggleClass("is-active");
//   });
// });

function setGetParam(key, value){
    var url = new URL(window.location);
    var query_string = url.search;
    var search_params = new URLSearchParams(query_string); 
    search_params.delete(key);
    search_params.append(key, value);
    url.search = search_params.toString();
    var new_url = url.toString();
    window.location.href = new_url;
};
function deleteGetParam(key){
    var url = new URL(window.location);
    var query_string = url.search;
    var search_params = new URLSearchParams(query_string); 
    search_params.delete(key);
    url.search = search_params.toString();
    var new_url = url.toString();
    window.location.href = new_url;
};