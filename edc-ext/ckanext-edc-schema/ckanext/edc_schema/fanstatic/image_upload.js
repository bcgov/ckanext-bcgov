$("#imageFile").change(function() {
	var filename = $("#imageFile").val().replace("C:\\fakepath\\","");
	$("#new_image_filename").val(filename);
});

$("#selectImageButton").click(function() {
//	console.log("Select Image button Clicked!");
	$("#imageFile").trigger('click');
});

$("#removeImageBtn").click(function() {
	
	
//	$("#uploaded_image").val('');
	$("#field-image_delete").val(1);
	$("#new_image_filename").val('');
	$('#dataset_img').attr('src', '');
	$("#removeImageBtn").attr('disabled', 'disabled');	
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
	
	$('#imageFile').fileupload({
		url: '/dataset/upload_file',
		forceIframeTransport: false,
		dataType: 'json',
		autoUpload: true,
		add: function (e, data) {
			data.context = $('#uploadButton').click(function () {
				data.submit();
			});
		},
		done: function (e, data) {
			$("#removeImageBtn").removeAttr('disabled');
			$("#uploaded_image").val(data.result.files[0].url);
			$("#field-image_delete").val('0');
			$('#dataset_img').attr('src', data.result.files[0].url).load(function(){
			    this.width;  
			});
		}
	}); 
		
});