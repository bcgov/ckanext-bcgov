function check_storage_location() {
	if ($("#field-resource_storage_location").val() == "001") {
		$("#object_name_container").show();
	}
	else {
		$("#field-object_name").val('');
		$("#object_name_container").hide();

	}
}


$(function() {
	check_storage_location();
	$("#field-data_collection_start_date").datepicker({ dateFormat: "yy-mm-dd", showOtherMonths: true, selectOtherMonths: true });
	$("#field-data_collection_end_date").datepicker({ dateFormat: "yy-mm-dd", showOtherMonths: true, selectOtherMonths: true });
	
});
