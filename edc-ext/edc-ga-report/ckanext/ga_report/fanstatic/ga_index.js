  $('a[data-toggle="dropdown"]').click(function(){
	    $("#graph-legend-container").hide();
  });
  
$("a[href=#totals]").click(function(e) {
    $("#graph-legend-container").hide();
 });

$(function() {
	$("#graph-legend-container").hide();
	CKAN.GA_Reports.bind_sparklines();
	CKAN.GA_Reports.bind_sidebar();
	CKAN.GA_Reports.bind_month_selector();
});
