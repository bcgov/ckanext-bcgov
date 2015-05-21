


function select_sector() {
	var parent_org = $('#field-parent').val();
	
	if (parent_org) {
		$('#suborg_sector_box').css("display", "block");
	}
	else {
		$('#suborg_sector_box').css("display", "none");		
	}
}

$(function() {
	select_sector()
}
);