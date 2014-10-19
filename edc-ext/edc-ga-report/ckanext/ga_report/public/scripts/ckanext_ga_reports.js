var CKAN = CKAN || {};
CKAN.GA_Reports = {};

CKAN.GA_Reports.render_rickshaw = function( css_name, data, mode, colorscheme ) {
    var graphLegends = $('#graph-legend-container');

    function renderError(alertClass,alertText,legendText) {
        $("#chart_"+css_name)
          .html( '<div class="alert '+alertClass+'">'+alertText+'</div>')
          .closest('.rickshaw_chart_container').css('height',50);
        var myLegend = $('<div id="legend_'+css_name+'"/>')
          .html(legendText)
          .appendTo(graphLegends);
    }

    if (!Modernizr.svg) {
        renderError('','Your browser does not support vector graphics. No graphs can be rendered.','(Graph cannot be rendered)');
        return;
    }
    if (data.length==0) {
        renderError('alert-info','There is not enough data to render a graph.','(No graph available)');
        return
    }
    var myLegend = $('<div id="legend_'+css_name+'"/>').appendTo(graphLegends);

    var palette = new Rickshaw.Color.Palette( { scheme: colorscheme } );
    $.each(data, function(i, object) {
        object['color'] = palette.color();
    });
    // Rickshaw renders the legend in reverse order...
    data.reverse();

    var graphElement =  document.querySelector("#chart_"+css_name);

    var graph = new Rickshaw.Graph( {
        element: document.querySelector("#chart_"+css_name),
        renderer: mode,
        series: data ,
        height: 328
    });
    var x_axis = new Rickshaw.Graph.Axis.Time( { 
        graph: graph 
    } );
    var y_axis = new Rickshaw.Graph.Axis.Y( {
        graph: graph,
        orientation: 'left',
        tickFormat: Rickshaw.Fixtures.Number.formatKMBT,
        element: document.getElementById('y_axis_'+css_name)
    } );
    var legend = new Rickshaw.Graph.Legend( {
        element: document.querySelector('#legend_'+css_name),
        graph: graph
    } );
    var shelving = new Rickshaw.Graph.Behavior.Series.Toggle( {
      graph: graph,
      legend: legend
    } );
    myLegend.prepend('<div class="instructions">Click on a series below to isolate its graph:</div>');
    graph.render();
};

CKAN.GA_Reports.bind_sparklines = function() {
  /* 
   * Bind to the 'totals' tab being on screen, when the 
   * Sparkline graphs should be drawn.
   * Note that they cannot be drawn sooner.
   */
  var created = false;
  $('a[href="#totals"]').on(
    'shown', 
      function() {
        if (!created) {
          var sparkOptions = {
            enableTagOptions: true,
            type: 'line',
            width: 100,
            height: 26,
            chartRangeMin: 0,
            spotColor: '',
            maxSpotColor: '',
            minSpotColor: '',
            highlightSpotColor: '#000000',
            lineColor: '#3F8E6D',
            fillColor: '#B7E66B'
          };
          $('.sparkline').sparkline('html',sparkOptions);
          created = true;
        }
        $.sparkline_display_visible();
      }
  );
};

CKAN.GA_Reports.bind_sidebar = function() {
  /* 
   * Bind to changes in the tab behaviour: 
   * Show the correct rickshaw graph in the sidebar. 
   * Not to be called before all graphs load.
   */
  $('a[data-toggle="tab"]').on(
    'shown',
    function(e) {
      var href = $(e.target).attr('href');
      var pane = $(href);
      if (!pane.length) { console.err('bad href',href); return; }
      var legend_name = "none";
      var graph = pane.find('.rickshaw_chart');
      if (graph.length) {
        legend_name = graph.attr('id').replace('chart_','');
      }
      legend_name = '#legend_'+legend_name;
      $('#graph-legend-container > *').hide();
      $('#graph-legend-container .instructions').show();
      $(legend_name).show();
    }
  );
  /* The first tab might already have been shown */
  $('li.active > a[data-toggle="tab"]').trigger('shown');
};

CKAN.GA_Reports.bind_month_selector = function() {
  var handler = function(e) { 
    var target = $(e.delegateTarget);
    var form = target.closest('form');
    var url = form.attr('action')+'?month='+target.val()+window.location.hash;
    window.location = url;
  };
  var selectors = $('select[name="month"]');
  //assert(selectors.length>0);
  selectors.bind('change', handler);
};
