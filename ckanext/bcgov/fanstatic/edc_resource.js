function check_storage_location() {
	if ($("#field-resource_storage_location").val() == "BCGW Data Store") {
		$("#object_name_container").show();
	}
	else {
		$("#field-object_name").val('');
		$("#object_name_container").hide();

	}
}

$('#field-image-upload').change(function() {
	
	var file = $('#field-image-upload')[0].files[0]
	if(file){
		var filename = file.name
		extension_index = filename.lastIndexOf('.');
		if (extension_index > 0) {
			filename = filename.substring(0, filename.lastIndexOf('.'));
		}
		
	    $("#field-name").val(filename);
	}
	
});

// workaround for firefox page caching when clicking the back button after adding a resource
window.onunload = function() {
	document.querySelector('.overlay-wrap').classList.remove('enable');
};

/**
 *  Issue #99 - Prevent user from clicking the add button more then one time	
 *	Disable the form and show a spinner when clicking the add button
**/
$('button[type="submit"]').click(function() {
	$(this).attr('disabled');
	$('.overlay-wrap').addClass('enable');	
});

$(function() {
	check_storage_location();
	$("#field-data_collection_start_date").datepicker({ dateFormat: "yy-mm-dd", showOtherMonths: true, selectOtherMonths: true });
	$("#field-data_collection_end_date").datepicker({ dateFormat: "yy-mm-dd", showOtherMonths: true, selectOtherMonths: true });

	var $resourceForm = $('.dataset-resource-form');
	if($resourceForm.hasClass('archived')) {
		$resourceForm.find('input, select, textarea, button, a.btn').each(function() {
			$(this).attr('disabled', 'disabled');
		});
	}

	$(document).ready(function() {
		setTimeout(function() {
			$('.image-upload').find('.control-group').each(function() {
				if($(this).hasClass('error')) {
					$(this).show();
					$('.image-upload .control-group:not(.error)').hide();
				}
			});
		}, 500);
	});
});