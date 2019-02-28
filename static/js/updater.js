$(document).ready(function () {
  var interval = 30 * 1000;   //number of mili seconds between each call
  var refresh = function() {
    $.ajax({
      url: "stat",
      cache: false,
      success: function(html) {
        $('#content').html(html);
        setTimeout(function() {
          refresh();
        }, interval);
      }
    });
  };
  refresh();
});
