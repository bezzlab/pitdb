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

  var oTable = $('#searchRes').dataTable({
    //"pagingType": "full_numbers",
    "bAutoWidth": false,
    "bProcessing": true,
    "aoColumns": [
      { "bVisible": false, "searchable": false },
      { "bVisible": true, "width": "15%" },
      { "bVisible": true, "width": "85%" }
      
    ],
    // // "bJQueryUI": true,
    // "bProcessing": true,
    // "bAutoWidth": false,
  });

  $('#searchRes tbody tr').click( function () {
    var aData = oTable.fnGetData(this);
    window.open("http://localhost:5000/"+aData[0]+"/summary");
  });

  $(".wordwrap").html(function(_, html){
    var val  = $('#searchData').val();
    var type = $('#searchType').val();
    if (type != "exact"){
      var regex = new RegExp("(" + val + "+)", "g");
      return html.replace(regex, '<span class="red">$1</span>'); 
    }  
  });
});

//$('.selectpicker').selectpicker();

