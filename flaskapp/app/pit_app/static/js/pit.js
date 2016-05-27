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

  var oTable = $('#proteinRes').dataTable({
    "bAutoWidth": false,
    "bProcessing": true,
  });

  $('#tgeSearch tbody tr').click( function () {
    var aData = oTable.fnGetData(this);
    window.open("http://localhost:5000/tge?accession="+aData[0]);
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

  

  // Select by default the first row (index 0)

  $('#tgeSummary tbody tr:eq(0)').addClass('selected');
  $('#resTrs tbody tr:eq(0)').addClass('selected');
  $('#tges tbody tr:eq(0)').addClass('selected');

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

  $('#tges tbody').on('click', 'tr', function () {
    
  });

  // $('#submitSearch').click(function() {
  //   $('#search-output').toggle();
  // });

  $("#searchOptions").change(function() {
    var str = $( "#searchOptions option:selected" ).text();
    var label = $(this.options[this.selectedIndex]).closest('optgroup').prop('label');
    $("#textArea").show();

    if (label == "Species") {
      $("#textArea").hide();
    } else {
      $("#textArea").show();

      if (str == "Amino Acid Sequence"){
        $(".searchOptions").toggle();
      } else {
        $(".searchOptions").hide();
      }
    }
  });

  var elem = $(".dna-seq");
  
  // if(elem){
  //   if (elem.text().length > 100)
  //     elem.text(elem.text().substr(0,100)+" .... ").append('<i class="fa fa-plus-circle text-success"></i>')
  // }

  // var pieOrganism = [{
  //   values: [19, 26, 55],
  //   labels: ['Residential', 'Non-Residential', 'Utility'],
  //   type: 'pie'
  // }];

  // var pieSample = [{
  //   values: [19, 26, 55],
  //   labels: ['Residential', 'Non-Residential', 'Utility'],
  //   type: 'pie'
  // }];

  // var layout = {
  //   autosize: false,
  //   width: 350,
  //   height: 350,
  //   margin: {
  //     l: 40,
  //     r: 40,
  //     b: 0,
  //     t: 20,
  //     pad: 0
  //   }
  // };

  // Plotly.newPlot('pie_organism', pieOrganism, layout);
  // Plotly.newPlot('pie_sample',   pieSample,   layout);

  var genoverseConfig = {
    container : '#genoverse',
    width     : 800,
    genome    : 'grch38',
    plugins   : [ 'controlPanel', 'karyotype', 'trackControls', 'resizer', 'fileDrop' ],
    tracks    : [
      Genoverse.Track.Scalebar,
      Genoverse.Track.extend({
        name      : 'Sequence',
        model     : Genoverse.Track.Model.Sequence.Ensembl,
        view      : Genoverse.Track.View.Sequence,
        resizable : 'auto',
        100000    : false
      }),
      Genoverse.Track.extend({
        name   : 'Genes',
        height : 200,
        info   : 'Ensembl API genes & transcripts, see <a href="http://beta.rest.ensembl.org/" target="_blank">beta.rest.ensembl.org</a> for more details',
        
        // Different settings for different zoom level
        2000000: { // This one applies when > 2M base-pairs per screen
          labels : false
        },
        100000: { // more than 100K but less then 2M
          labels : true,
          model  : Genoverse.Track.Model.Gene.Ensembl,
          view   : Genoverse.Track.View.Gene.Ensembl
        },
        1: { // > 1 base-pair, but less then 100K
          labels : true,
          model  : Genoverse.Track.Model.Transcript.Ensembl,
          view   : Genoverse.Track.View.Transcript.Ensembl
        }
      }),
      Genoverse.Track.extend({
          name   : 'Test',
          view   : Genoverse.Track.View.Transcript.extend({
            setFeatureColor : function () {}
          }),
          height : 300,
          url    : '/data/G10.assemblies.fasta.transdecoder.genome.gff3_identified.gff3',
          model  : Genoverse.Track.Model.extend({
            dataType : 'text',
            parseData: function (text) {
              var lines = text.split('\n');

              for (var i = 0; i < lines.length; i++) {
                if (!lines[i].length || lines[i].indexOf('#') === 0) {
                  continue;
                }
                
                var fields = lines[i].split('\t');

                if (fields[0] === this.browser.chr || fields[0].toLowerCase() === 'chr' + this.browser.chr || fields[0].match('[^1-9]' + this.browser.chr + '$')) {

                  var feature = {
                    id     : fields.slice(0, 5).join('|'),
                    start  : parseInt(fields[3], 10),
                    end    : parseInt(fields[4], 10),
                    exons  : [],
                    cds    : []
                  };

                  if (fields[8]) {
                    var extraFields = fields[8].split(';');
                    
                    for (var j = 0; j < extraFields.length; j++) {
                      var keyValue = extraFields[j].split('=');
                      
                      if (keyValue.length === 2 && !feature[keyValue[0]]) {
                        feature[keyValue[0].toLowerCase()] = keyValue[1];
                      }
                    }
                  }

                  feature.color = 'rgb(' + feature.color + ')';

                  // CIGAR Gap, here we assume it's always M or D, with D only being surrounded with Ms
                  if (feature.gap) {
                    var cursor = feature.start;
                    var chunks = feature.gap.split(' ');
                    for (var j=0; j<chunks.length; j++) {
                      if (chunks[j].charAt(0) === 'M') {
                        var length = parseInt( chunks[j].substr(1), 10 );
                        feature.exons.push({
                          start : cursor,
                          end   : cursor + length,
                        });
                        feature.cds.push({
                          start : cursor,
                          end   : cursor + length,
                          color : feature.color,
                        });
                        cursor = cursor + length;
                      }
                      else {
                        var length = parseInt(chunks[j].substr(1), 10);
                        cursor += length;
                      }
                    }
                  }

                  feature.labelColor = 'black';
                  feature.label = feature.name;

                  this.insertFeature(feature);
                }

              }
            }
          }),
        })
    ]
  };
  
  document.addEventListener('DOMContentLoaded', function () { window.genoverse = new Genoverse(genoverseConfig); });
});

