'use strict';
let alink = document.querySelectorAll('a');
alink.forEach(function(myhref) {
    myhref.addEventListener('click', filter);
 });

function filter(event){
    if (event.target.tagName === 'A'){
      console.log(event.target.href);
      event.preventDefault();
      if (event.target.getAttribute('class') != 'no_action') {
        $.ajax({
          url: event.target.href,
          success: function (data) {
              $('.content').html(data);
               let alink = document.querySelectorAll('a');
                 alink.forEach(function(myhref) {
                    myhref.addEventListener('click', filter);
                 });
              },
          });
      }
      else {
          // window.location.href = event.target.href
      }
    }
  }