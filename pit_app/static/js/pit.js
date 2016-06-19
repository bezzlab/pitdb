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

  $.fn.highlight = function (resTrs) {
    indx = resTrs.$('tr.selected').index()
    //var aData = resTrs.cell(indx, 2).data();
    //alert(aData)
    //   var arr = aData[2].split(',');

    //   $("#tgeSeq").html(function(_, html){
        
    //     var finalHtml = html;
    //     $.each(arr, function( index, value ) {
    //       var regex = null;
    //       var regex = new RegExp("(" + value + "+)", "g");
    //       alert(regex)
    //       finalHtml = finalHtml.replace(regex, '<span class="red">$1</span>');
    //       alert(finalHtml)
    //     });
    //     return finalHtml;
    //   });
  };

  $.fn.emphasis = function(str, className) {
    var regex = new RegExp(str, "gi");

    return this.each(function() {
      this.innerHTML = this.innerHTML.replace(regex, function(matched) {
        return '<span class="red">' + matched + '</span>';
      });
    });
  };

  $('#searchOptions').change(function(){
    $('#searchFilter').html("Enter "+$(this).val()+":");
  });

  // Create all DataTables 

  var tgeTable = $('.tgeTable').dataTable({
    "bAutoWidth": false,
    "bProcessing": true,
  });

  var proteinRes = $('#proteinRes').dataTable({
    "bAutoWidth": false,
    "bProcessing": true,
  });

  var pepTable = $('#pepTable').dataTable({
    "bAutoWidth": false,
    "bProcessing": true,
    "aoColumns": [
      { "bVisible": true, "width": "20%" },
      { "bVisible": true, "width": "80%" },
      
    ],
  });

  var smplTable = $('#smplTable').dataTable({
    "bAutoWidth": false,
    "bProcessing": true,
  }); 

  var orgTable = $('#orgTable').dataTable({
    "bAutoWidth": false,
    "bProcessing": true,
  }); 

  var resTrs = $('#resTrs').dataTable({
    "bAutoWidth": false,
    "bProcessing": true,
    "aoColumns": [
      { "bVisible": true, "width": "10%" },
      { "bVisible": true, "width": "65%" },
      { "bVisible": true, "width": "25%" }
      
    ],
  });

  $('#orgTable tbody tr').click( function () {
    if ( $(this).hasClass('selected') ) {
      $(this).removeClass('selected');
    }
    else {
      $('.test').html(original);
      orgTable.$('tr.selected').removeClass('selected');
      $(this).addClass('selected');
    }
  });


  // Select by default the first row (index 0)
  // $('.dataTable tbody tr:eq(0)').addClass('selected');

  // $(".wordwrap").html(function(_, html){
  //   var val  = $('#searchData').val();
  //   var type = $('#searchType').val();
  //   if (type != "exact"){
  //     var regex = new RegExp("(" + val + "+)", "g");
  //     return html.replace(regex, '<span class="red">$1</span>'); 
  //   }  
  // });

  $("#tgeSeq").html(function(_, html){
    var val  = $('.peptide_seq').val();

    // var val  = $('#searchData').val();
    // var type = $('#searchType').val();
    // if (type != "exact"){
    //   var regex = new RegExp("(" + val + "+)", "g");
    //   return html.replace(regex, '<span class="red">$1</span>'); 
    // }  
  });

  // Add on-click events
  $('#tgeSummary tbody').on( 'click', 'tr', function () {
    tgeSummary.$('tr.selected').removeClass('selected');
    $(this).addClass('selected');

    indx = $(this).index();
    resTrs.$('tr.selected').removeClass('selected');
    $('#resTrs tbody tr:eq('+indx+')').addClass('selected');
  });

  $('.table').highlight(resTrs);

  $('#resTrs tbody').on( 'click', 'tr', function () {
    resTrs.$('tr.selected').removeClass('selected');
    $(this).addClass('selected');

    var aData = resTrs.fnGetData(this);
    var arr = aData[2].split(',');

    var nol = arr.length; // find out the number of letters
    for(i=0;i<nol;i++){ // loop through each letters
      $(".in").emphasis(arr[i], 'red'); // The function "emphasis"
    }
    //});

    indx = $(this).index();
    tgeSummary.$('tr.selected').removeClass('selected');
    $('#tgeSummary tbody tr:eq('+indx+')').addClass('selected');
  });

  $("#searchOptions").change(function() {
    var str = $( "#searchOptions option:selected" ).text();
    var label = $(this.options[this.selectedIndex]).closest('optgroup').prop('label');
    $("#textArea").show();

    if (label == "Species") {
      $("#textArea").hide();
    } else {
      $("#textArea").show();

      if (str == "Amino Acid Sequence" || str == "Peptide Sequence"){
        $(".searchOptions").show();
      } else {
        $(".searchOptions").hide();
      }
    }
  });

  $('#tgeType').click(function(event) {  //on click
    if (this.checked) { // check select status
      $('.check_nested').each(function() { //loop through each checkbox
        this.checked = true;  //select all checkboxes with class "checkbox1"
      });
    }else{
      $('.check_nested').each(function() { //loop through each checkbox
        this.checked = false; //deselect all checkboxes with class "checkbox1"
      });
    }
  });
});

