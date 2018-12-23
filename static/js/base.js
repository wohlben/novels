//$(document).ready(function() {
//   $(".navbar-burger").click(function() {
//       $(".navbar-burger").toggleClass("is-active");
//       $(".navbar-menu").toggleClass("is-active");
//   });
// });

function setUrlGetParam(uri_get) {
  window.location = window.location.protocol + '//' + window.location.host + window.location.pathname + '?'+ uri_get;
}
