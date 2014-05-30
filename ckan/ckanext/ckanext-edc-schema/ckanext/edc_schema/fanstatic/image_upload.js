var file;

$("#imageFile").change(function() {
	var filename = $("#imageFile").val().replace("C:\\fakepath\\","");
	$("#new_image_filename").val(filename);
	file = this.files[0];
});

$("#selectImageButton").click(function() {
	$("#imageFile").trigger('click');
});

$("#uploadButton").click(function() {
	var new_filename =  $("#new_image_filename").val();
	var data = new FormData();
	data.append("file", file);
	data.append("exisiting_filename", $("#uploaded_image").val());
	data.append("id", $("#edc_pkg_id").val());

	var requesst = $.ajax({
							url: "/dataset/upload_file",
        					type: 'POST',
        					data: data,
        					dataType: 'text',
        					processData: false,
        					contentType: false,
        					success : function (data) {
        						$("#removeImageBtn").removeAttr('disabled');
        						$("#uploaded_image").val(data)
        						$('#dataset_img').attr('src', data).load(function(){
        						    this.width;  
        						});
        					}
    				});
});


$("#removeImageBtn").click(function() {
	
	
	$("#uploaded_image").val('');
	$("#new_image_filename").val('');
	$('#dataset_img').attr('src', '');
	$("#removeImageBtn").attr('disabled', 'disabled');	
/*	
	var data = new FormData();
	data.append("filename", $("#uploaded_image").val());
	data.append("id", $("#edc_pkg_id").val());

	var requesst = $.ajax({
							url: "/dataset/remove_file",
        					type: 'POST',
        					data: data,
        					dataType: 'text',
        					processData: false,
        					contentType: false,
        					success : function (data) {
        						$("#removeImageBtn").attr('disabled', 'disabled');
        						$("#uploaded_image").val('');
        						$("#new_image_filename").val('');
        						$('#dataset_img').attr('src', '');
        					}
    				});
    				
*/
});


$(function() {
	var $dataset_image = $("#dataset_img");
	var image_src = $dataset_image.attr("src");
	
	if (image_src) {
		$("#removeImageBtn").removeAttr('disabled');
	}
	else {
		$("#removeImageBtn").attr('disabled', 'disabled');	
	}
});