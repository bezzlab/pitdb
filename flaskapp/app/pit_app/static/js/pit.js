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
      //{ "bVisible": false, "searchable": false },
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

  $("#tgeSeq").html(function(_, html){
    var val  = $('.peptide_seq').val();

    // var val  = $('#searchData').val();
    // var type = $('#searchType').val();
    // if (type != "exact"){
    //   var regex = new RegExp("(" + val + "+)", "g");
    //   return html.replace(regex, '<span class="red">$1</span>'); 
    // }  
  });

  $('#resTrs').dataTable({
    //"pagingType": "full_numbers",
    "bAutoWidth": false,
    "bProcessing": true,
    "aoColumns": [
      { "bVisible": true, "width": "10%" },
      { "bVisible": true, "width": "65%" },
      { "bVisible": true, "width": "25%" }
      
    ],
    // // "bJQueryUI": true,
    // "bProcessing": true,
    // "bAutoWidth": false,
  });

  $('#tgeSummary').dataTable({
    "bAutoWidth": false,
    "bProcessing": true,
  });

  var elem = $(".dna-seq");
    if(elem){
      if (elem.text().length > 150)
        elem.text(elem.text().substr(0,150)+"....")
  }

});

//$('.selectpicker').selectpicker();

