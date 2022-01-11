
$(document).ready(function() {
  if(data && 'is_error' in data && data.is_error){
    swal({
      title: "Error",
      text: data.error_message,
      icon: "error",
      dangerMode: true
    });
  } else {
    if(data && 'success_message' in data){
      swal({
        title: data.success_message,
        icon: "success"
      });
    }
  }
});
