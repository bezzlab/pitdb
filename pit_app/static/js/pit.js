$(function() {
  var url    = $(location).attr('href');
  var tgeSeq = $(".test").html();

  // Get the path of the URL and split in sections
  function get_path(url) {
      // following regex extracts the path from URL
    url = url.replace(/^https?:\/\/[^\/]+\//i, "").replace(/\/$/, "");
    url = url.replace(/\+/g, " ");
    arr = url.split(/\?|\=|\&/) 

    return arr
  }

  path = get_path(url)

  // Fix relevant page titles based on the URL path
  if (path[0]=="transcript") {
    document.title = "PITDB: Transcript "+ path[2];
  } else if (path[0]=="aminoseq") {
    document.title = "PITDB: AminoSeq "+ path[2];
  } else if (path[0] =="") {
    document.title = "PITDB"
  }else {
    document.title = "PITDB: "+path[2];
  }

  // $("a[rel='tooltip']").tooltip({'placement': 'right', 'z-index': '3000'});

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
  };

  // Add relevant placeholders in the search area for each selection in the dropdown list
  $('#searchOptions').change(function(){
    $('#searchFilter').html("Enter "+$(this).val()+":");
    var placeholder;

    switch ($(this).val()) {
      case 'Accession Number':
        placeholder = 'e.g. TGE001234'
        break;
      case 'Amino Acid Sequence':
        placeholder = 'e.g. MSCVNLPTVLPGSPSKT (partial sequence)';
        break;
      case 'Experiment ID':
        placeholder = 'e.g. PIT000001';
        break;
      case 'Uniprot ID':
        placeholder = 'e.g. P12111';
        break;
      case 'Peptide':
        placeholder = 'e.g. EMEENFAVEAANYQDTIGR (exact sequence)';
        break;
      default:
        placeholder = 'Enter a search term'
    }

    $('#searchArea').attr('placeholder', placeholder);
  });

  // Submit form on keydown (enter) 
  $('#submitSearch').keypress(function (e) {
    if (e.which == 13) {
      $('#searchform').submit();
      return false;    
    }
  });

  $('#searchArea').keydown(function(e) {
    if (e.which == 13) {
      $('#searchform').submit();
      return false;   
    }
  });

  // Create all the DataTables 
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

  var geneRes = $('#geneRes').dataTable({
    "bAutoWidth": false,
    "bProcessing": true,
    "aoColumns": [
      { "bVisible": false },
      { "bVisible": true, "width": "20%" },
      { "bVisible": true, "width": "20%" },
      { "bVisible": true, "width": "40%" },
      { "bVisible": true, "width": "20%" }
    ],
  });

  var exptgeTable = $('#exptgeTable').dataTable({
    "bAutoWidth": false,
    "bProcessing": true,
    "aoColumns": [
      { "bVisible": true, "width": "18%" },
      { "bVisible": true, "width": "20%" },
      { "bVisible": true, "width": "20%" },
      { "bVisible": true, "width": "42%" }
    ],
    "initComplete": function(settings, json) {
      // $("#spinnerTable").hide();
      $("#exptgeTable").show();
    },
  });

  var orgTable = $('#orgTable').dataTable({
    "bAutoWidth": false,
    "bProcessing": true,
    "initComplete": function(settings, json) {
      // $("#spinnerTable").hide();
      $("#orgTable").show();
    },
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

  $('#geneRes tbody tr').click( function () {
    var aData = geneRes.fnGetData( this );
    window.open("/protein?uniprot="+aData[0])
  } );

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


  $('#searchform').submit(function(e){
    var str = $( "#searchOptions option:selected" ).val();
    
    if (str == "default"){
      $(".modalWarning").html('** You need to select one option from the drop-down list.');
      return false;
    }
    
  });

  // Trigger the bootstrap tooltip functionality
  $('.popoverData').popover();

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
    $(".modalWarning").hide()
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

  if ( $( "#chart" ).length > 0 ) {
    // Set the dimensions of the sunburst graph
    var width = 500;
    var height = 400;
    var radius = Math.min(width, height) / 2;

    // Breadcrumb dimensions: width, height, spacing, width of tip/tail.
    var b = {
      w: 100, h: 34, s: 3, t: 10
    };

    // Total size of all segments; we set this later, after loading the data.
    var totalSize = 0; 

    var vis = d3.select("#chart").append("svg:svg")
      .attr("width", width)
      .attr("height", height)
      .append("svg:g")
      .attr("id", "container")
      .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");

    var partition = d3.layout.partition()
      .size([2 * Math.PI, radius * radius])
      .value(function(d) { return d.size; });

    var arc = d3.svg.arc()
      .startAngle(function(d) { return d.x; })
      .endAngle(function(d) { return d.x + d.dx; })
      .innerRadius(function(d) { return Math.sqrt(d.y); })
      .outerRadius(function(d) { return Math.sqrt(d.y + d.dy); });

    // Ordinal scales https://github.com/d3/d3/wiki/Ordinal-Scales#category20 
    var colors = d3.scale.category20c();

    d3.json("/"+path[0]+"/"+path[2]+".json", function(error, data) {
      createVisualization(data);
    });

  }

  // Main function to draw and set up the visualization, once we have the data.
  function createVisualization(json) {

    // Basic setup of page elements.
    initializeBreadcrumbTrail();
    drawLegend();
    d3.select("#togglelegend").on("click", toggleLegend);

    // Bounding circle underneath the sunburst, to make it easier to detect
    // when the mouse leaves the parent g.
    vis.append("svg:circle")
        .attr("r", radius)
        .style("opacity", 0);

    // For efficiency, filter nodes to keep only those large enough to see.
    var nodes = partition.nodes(json)
        .filter(function(d) {
        return (d.dx > 0.005); // 0.005 radians = 0.29 degrees
    });

    var path = vis.data([json]).selectAll("path")
        .data(nodes)
        .enter().append("svg:path")
        .attr("display", function(d) { return d.depth ? null : "none"; })
        .attr("d", arc)
        .attr("fill-rule", "evenodd")
        .style("fill", function(d) { return colors(d.name); })
        .style("opacity", 1)
        .on("mouseover", mouseover);

    // Add the mouseleave handler to the bounding circle.
    d3.select("#container").on("mouseleave", mouseleave);

    // Get total size of the tree = value of root node from partition.
    totalSize = path.node().__data__.value;
  };

  // Fade all but the current sequence, and show it in the breadcrumb trail.
  function mouseover(d) {

    var percentage = (100 * d.value / totalSize).toPrecision(3);
    var percentageString = percentage + "%";
    if (percentage < 0.1) {
      percentageString = "< 0.1%";
    }

    var sequenceArray = getAncestors(d);
    updateBreadcrumbs(sequenceArray, percentageString);

    d3.select("#percentage")
        .html('<h2>'+commaSeparateNumber(d.size)+'</h2>\n <div class="wordwrap">'+d.name+'</div>');

    // d3.select("#explanation")
    //     .style("visibility", "");

    // Fade all the segments.
    d3.selectAll("path")
      .style("opacity", 0.2)
      .style("stroke-width", 1)
      .style("stroke", "white");

    // Then highlight only those that are an ancestor of the current segment.
    vis.selectAll("path")
      .filter(function(node) {
        return (sequenceArray.indexOf(node) >= 0);
      })
      .style("opacity", 1)
      .style("stroke-width", 1.5)
      .style("stroke", "black");
  }

  // Restore everything to full opacity when moving off the visualization.
  function mouseleave(d) {

    // Hide the breadcrumb trail
    d3.select("#trail")
      .style("visibility", "hidden");

    // Deactivate all segments during transition.
    d3.selectAll("path").on("mouseover", null);

    // Transition each segment to full opacity and then reactivate it.
    d3.selectAll("path")
      .transition()
      .duration(1000)
      .style("opacity", 1)
      .style("stroke-width", 1)
      .style("stroke", "white")
      .each("end", function() {
        d3.select(this).on("mouseover", mouseover);
      });

    // d3.select("#explanation")
    //   .style("visibility", "hidden");
    d3.select("#percentage").html('<span class="sunburstInfo"><p>Rollover the map to see details</p></span>')
  }

  // Given a node in a partition layout, return an array of all of its ancestor
  // nodes, highest first, but excluding the root.
  function getAncestors(node) {
    var path = [];
    var current = node;
    while (current.parent) {
      path.unshift(current);
      current = current.parent;
    }
    return path;
  }

  function initializeBreadcrumbTrail() {
    // Add the svg area.
    var trail = d3.select("#sequence").append("svg:svg")
        .attr("width", width)
        .attr("height", 50)
        .attr("id", "trail");
    // Add the label at the end, for the percentage.
    trail.append("svg:text")
      .attr("id", "endlabel")
      .style("fill", "#000");
  }

  // Generate a string that describes the points of a breadcrumb polygon.
  function breadcrumbPoints(d, i) {
    var points = [];
    points.push("0,0");
    points.push(b.w + ",0");
    points.push(b.w + b.t + "," + (b.h / 2));
    points.push(b.w + "," + b.h);
    points.push("0," + b.h);
    if (i > 0) { // Leftmost breadcrumb; don't include 6th vertex.
      points.push(b.t + "," + (b.h / 2));
    }
    return points.join(" ");
  }

  // Update the breadcrumb trail to show the current sequence and percentage.
  function updateBreadcrumbs(nodeArray, percentageString) {

    // Data join; key function combines name and depth (= position in sequence).
    var g = d3.select("#trail")
        .selectAll("g")
        .data(nodeArray, function(d) { return d.name + d.depth; });

    // Add breadcrumb and label for entering nodes.
    var entering = g.enter().append("svg:g");

    entering.append("svg:polygon")
        .attr("points", breadcrumbPoints)
        .style("fill", function(d) { return colors(d.name); });

    entering.append("svg:text")
        .attr("x", (b.w + b.t) / 2)
        .attr("y", b.h / 2)
        .attr("dy", "0.35em")
        .attr("text-anchor", "middle")
        .text(function(d) { return d.type; });

    // Set position for entering and updating nodes.
    g.attr("transform", function(d, i) {
      return "translate(" + i * (b.w + b.s) + ", 0)";
    });

    // Remove exiting nodes.
    g.exit().remove();

    // Now move and update the percentage at the end.
    d3.select("#trail").select("#endlabel")
        .attr("x", (nodeArray.length + 0.5) * (b.w + b.s))
        .attr("y", b.h / 2)
        .attr("dy", "0.35em")
        .attr("text-anchor", "middle")
        .text(percentageString);

    // Make the breadcrumb trail visible, if it's hidden.
    d3.select("#trail")
        .style("visibility", "");

  }

  function drawLegend() {

    // Dimensions of legend item: width, height, spacing, radius of rounded rect.
    var li = {
      w: 75, h: 30, s: 3, r: 3
    };

    var legend = d3.select("#legend").append("svg:svg")
      .attr("width", li.w)
      .attr("height", d3.keys(colors).length * (li.h + li.s));

    var g = legend.selectAll("g")
      .data(d3.entries(colors))
      .enter().append("svg:g")
      .attr("transform", function(d, i) {
              return "translate(0," + i * (li.h + li.s) + ")";
           });

    g.append("svg:rect")
      .attr("rx", li.r)
      .attr("ry", li.r)
      .attr("width", li.w)
      .attr("height", li.h)
      .style("fill", function(d) { return d.value; });

    g.append("svg:text")
      .attr("x", li.w / 2)
      .attr("y", li.h / 2)
      .attr("dy", "0.35em")
      .attr("text-anchor", "middle")
      .text(function(d) { return d.key; });
  }

  function toggleLegend() {
    var legend = d3.select("#legend");
    if (legend.style("visibility") == "hidden") {
      legend.style("visibility", "");
    } else {
      legend.style("visibility", "hidden");
    }
  }

  function unique(array){
    return array.filter(function(el, index, arr) {
        return index === arr.indexOf(el);
    });
  }

  var original = $('#tgeSeq').html()

  var tgeTable = $('#tges').DataTable({
    "order": [[ 0, "desc" ]],
    "columnDefs": [{
      "targets": [ 0 ],
      "visible": false,
      "searchable": false
    }], 
    "bAutoWidth": false,
    "bProcessing": true,
    "aoColumns": [
      { "bVisible": false },
      { "bVisible": true, "width": "10%" },
      { "bVisible": true, "width": "10%" },
      { "bVisible": true, "width": "10%" },
      { "bVisible": true, "width": "20%" },
      { "bVisible": true, "width": "30%" },
      { "bVisible": true, "width": "10%" },
      { "bVisible": true, "width": "10%" },
    ],
  });

  $('.dataTable tbody tr:eq(0)').addClass('selected');

  if (path[0] == "tge") {
    setTimeout(function() {
      var indx  = tgeTable.row(this).index()
      var aData = tgeTable.cell(indx, 5).data()
      var arr   = aData.split('<li>');
      var posMatch = [];
      
      jQuery.each( arr, function( i, val ) {
        if (i > 0) {
          var searchKey = arr[i];
          var searchKey = searchKey.replace(/<\/li>/, "").replace(/\n/g, "").replace(/<\/ul>/, "")

          start = tgeSeq.indexOf(searchKey);

          $.each(searchKey.split(''), function(k, v) {
            posMatch.push(start+k)
          });

        }

        if (i == (arr.length-1)){
          ind = unique(posMatch)

          var ret  = "";

          for (var i = 0, len = tgeSeq.length; i < len; i++) {
            if ($.inArray(i, ind) !== -1 ){
              ret += '<span class="_code_string _tmp_span">' + tgeSeq.charAt(i) + "</span>";
            } else {
              ret += tgeSeq.charAt(i);
            }
          }
          $(".test").html(ret)
        }
      });
    }, 2);
  } 


  $('#tges tbody').on('click', 'tr', function () {
    if ( $(this).hasClass('selected') ) {
      $(this).removeClass('selected');
    }
    else {
      $(".test").html(tgeSeq)
      tgeTable.$('tr.selected').removeClass('selected');
      $(this).addClass('selected');

      var indx  = tgeTable.row(this).index()
      var aData = tgeTable.cell(indx, 5).data()
      var arr   = aData.split('<li>');
      var posMatch = [];
      
      jQuery.each( arr, function( i, val ) {
        if (i > 0) {
          var searchKey = arr[i];
          var searchKey = searchKey.replace(/<\/li>/, "").replace(/\n/g, "").replace(/<\/ul>/, "")
          
          start = tgeSeq.indexOf(searchKey);

          $.each(searchKey.split(''), function(k, v) {
            posMatch.push(start+k)
          });
        }

        if (i == (arr.length-1)){
          ind = unique(posMatch)

          var ret  = "";

          for (var i = 0, len = tgeSeq.length; i < len; i++) {
            if ($.inArray(i, ind) !== -1 ){
              ret += '<span class="_code_string _tmp_span">' + tgeSeq.charAt(i) + "</span>";
            } else {
              ret += tgeSeq.charAt(i);
            }
          }
          $(".test").html(ret)
        }
      });
    }
  });

  // searchKey3.setEvidence({
  //     parent: 'wordwrap',
  //     element: {
  //         name: 'container2',
  //         id: 'trialId3',
  //         class: '',
  //     },
  //     position: {
  //         begin: 230,
  //         end: 258
  //     }
  // });

  // searchKey4.setEvidence({
  //     parent: 'wordwrap',
  //     element: {
  //         name: 'container1',
  //         id: 'trialId4',
  //         class: '',
  //     },
  //     position: {
  //         begin: 249,
  //         end: 276
  //     }
  // });

  function commaSeparateNumber(val){
    while (/(\d+)(\d{3})/.test(val.toString())){
      val = val.toString().replace(/(\d+)(\d{3})/, '$1'+','+'$2');
    }
    return val;
  }

  $('#chart').ready(function() { 
    $('#percentage').html('<span class="sunburstInfo"><p>Rollover the map to see details</p></span>') 
  });

});

