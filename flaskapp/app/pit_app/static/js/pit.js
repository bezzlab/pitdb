$(function() {
  $('a[href*=#]:not([href=#])').click(function() {
    if (location.pathname.replace(/^\//,'') == this.pathname.replace(/^\//,'') && location.hostname == this.hostname) {
      var target = $(this.hash);
      target = target.length ? target : $('[name=' + this.hash.slice(1) +']');
      if (target.length) {
        $('html,body').animate({
          scrollTop: target.offset().top
        }, 1000);
        return false;
      }
    }
  });


  $('#searchOptions').change(function(){
    $('#searchFilter').html("Enter "+$(this).val()+":");
  });

  var oTable = $('#search-results').dataTable({
    "pagingType": "full_numbers",
    // "bJQueryUI": true,
    // "bProcessing": true,
    // "bAutoWidth": false,
    // // "aoColumns": [
    //   { "bVisible": false },
    //   null,
    //   null
    // ]
  });

  $('#search-results tbody tr').click( function () {
    var aData = oTable.fnGetData( this );
    // alert( aData[0] ); // assuming the id is in the first column
    window.open("http://localhost:5000/"+aData[0]+"/summary");
  });

});

//$('.selectpicker').selectpicker();

