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

  var oTable = $('#searchRes').dataTable({
   // "bAutoWidth": false,
    "bProcessing": true,
    // "aoColumns": [
    //   //{ "bVisible": false, "searchable": false },
    //   { "bVisible": true, "width": "15%" },
    //   { "bVisible": true, "width": "85%" }
      
    // ],
  });

  $('#searchRes tbody tr').click( function () {
    var aData = oTable.fnGetData(this);
    window.open("http://localhost:5000/tge/"+aData[0]);
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

  // Create DataTables 

  var tgeSummary = $('#tgeSummary').dataTable({
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

  // Select by default the first row (index 0)

  $('#tgeSummary tbody tr:eq(0)').addClass('selected');
  $('#resTrs tbody tr:eq(0)').addClass('selected');

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


  // $('#submitSearch').click(function() {
  //   $('#search-output').toggle();
  // });

  $("#searchOptions").change(function() {
    var str = $( "#searchOptions option:selected" ).text();
    if (str == "Amino Acid Sequence" || str == "Name" ){
      $(".searchOptions").toggle();
    } else {
      $(".searchOptions").hide();
    }
  });

  var elem = $(".dna-seq");
  
  // if(elem){
  //   if (elem.text().length > 100)
  //     elem.text(elem.text().substr(0,100)+" .... ").append('<i class="fa fa-plus-circle text-success"></i>')
  // }

  var pieOrganism = [{
    values: [19, 26, 55],
    labels: ['Residential', 'Non-Residential', 'Utility'],
    type: 'pie'
  }];

  var pieSample = [{
    values: [19, 26, 55],
    labels: ['Residential', 'Non-Residential', 'Utility'],
    type: 'pie'
  }];

  var layout = {
    autosize: false,
    width: 350,
    height: 350,
    margin: {
      l: 40,
      r: 40,
      b: 0,
      t: 20,
      pad: 0
    }
  };

  Plotly.newPlot('pie_organism', pieOrganism, layout);
  Plotly.newPlot('pie_sample',   pieSample,   layout);
});

