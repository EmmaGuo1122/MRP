

$(document).ready(function() {
  show_activity_tracking_list();
  show_displayed_name();

  $('.dropdown-content-body > ul > li > a').click(function () {
    window.location = $(this).attr('href');
  });

  // add + in the table header
  var current_user = data.current_user;
  if(current_user.permission.can_add_activity_tracking){
    var insert_symbol = '<span class="jsgrid-button jsgrid-mode-button jsgrid-insert-mode-button ti-plus" type="button" title=""></span>';
    $('th.jsgrid-control-field').append(insert_symbol);

    var upload_symbol = '<span class="jsgrid-button jsgrid-mode-button jsgrid-upload-mode-button ti-upload" type="button" title=""></span>';
    $('th.jsgrid-control-field').append(upload_symbol);
  }

  resgister_control_events();
    
});

function resgister_control_events(){
  // handle events on table
  $($('.jsgrid-header-cell')[0]).attr('style','display:none');

  // ADD
  $('.jsgrid-insert-mode-button').click(function() {
    show_activity_tracking_detail_form('ADD', null);
  });

   // UPLOAD
   $('.jsgrid-upload-mode-button').click(function() {
    show_upload_form();
  });

  // EDIT
  $('.jsgrid-edit-button').click(function () {
    let activity_tracking_id = $($(this).parent().siblings()[0]).text().trim();
    $.ajax({
        type: "GET",
        url: "/api/activity_tracking/"+activity_tracking_id,
        success: function(activity_tracking_obj) {
          show_activity_tracking_detail_form('EDIT', activity_tracking_obj);
        },
        error: function(error){
          if(error.status == 0){
            window.location = '/login';
          } else {
            swal({
              title: "Error",
              text: error.status + ' ' + error.statusText,
              icon: "error",
              dangerMode: true
            });
          }
        }
    });
  });

  // DELETE
  $('.jsgrid-delete-button').click(function () {
    var activity_tracking_id = $($(this).parent().siblings()[0]).text().trim();
    
    swal({
          title: "Are you sure to delete this activity tracking?",
          icon: "warning",
          buttons: ["No", "Yes"]
    }).then((willDelete) => {
      if (willDelete) {
        call_activity_tracking_deleting_api(activity_tracking_id);
      }
    });
  });
}

function show_upload_form(){
  swal({
      title: "Import Tracking Records",
      className: 'swal-custom-width',
      closeOnClickOutside: false,
      content: render_html_activity_tracking_upload_form(),
      buttons: {
        cancel: {
          text: "Cancel",
          value: null,
          visible: true,
          className: "",
          closeModal: true,
        },
        confirm: {
          text: "Import",
          value: true,
          visible: true,
          className: "",
          closeModal: false
        }
      }
  }).then((willUpload) => {
    if (willUpload) {
      call_tracking_import_api();
    }
  }); 
}

function show_activity_tracking_detail_form(mode, activity_tracking_obj){
  var title = (mode == 'ADD') ? 'Create New Activity Tracking' : 'Edit Activity Tracking';
  swal({
      title: title,
      className: 'swal-custom-width',
      closeOnClickOutside: false,
      content: render_html_activity_tracking_detail_form(),
      buttons: {
        cancel: {
          text: "Cancel",
          value: null,
          visible: true,
          className: "",
          closeModal: true,
        },
        confirm: {
          text: "Save",
          value: true,
          visible: true,
          className: "",
          closeModal: false
        }
      }
  }).then((willSave) => {
      if(willSave){
        let save_obj = {};
        save_obj.id = '';
        if(activity_tracking_obj != null && activity_tracking_obj['id']){
            save_obj.id = activity_tracking_obj.id;
        }

        save_obj.site_id = $('#site_id').val();
        save_obj.tenant_id = $('#tenant_id').val();
        save_obj.activity_category_id = $('#activity_category_id').val();
        save_obj.date_of_record = $('#date_of_record').val();
        save_obj.time_of_record = $('#time_of_record').val();
        save_obj.comments = $('#comments').val();

        $('.validation_error').text('');
        call_activity_tracking_saving_api(save_obj);
      }
  });

  setTimeout(function(){ when_activity_tracking_detail_modal_ready(mode, activity_tracking_obj); }, 100);
}

String.prototype.lpad = function(padString, length) {
  var str = this;
  while (str.length < length)
      str = padString + str;
  return str;
}

function when_activity_tracking_detail_modal_ready(mode, activity_tracking_obj) {
    if(activity_tracking_obj != null){
        $('#site_id').val(activity_tracking_obj.site_id);
        $('#tenant_id').val(activity_tracking_obj.tenant_id);
        $('#activity_category_id').val(activity_tracking_obj.activity_category_id);
        $('#date_of_record').val(activity_tracking_obj.date_of_record);
        $('#time_of_record').val(activity_tracking_obj.time_of_record);
        $('#comments').val(activity_tracking_obj.comments);
    }

    if(mode == "ADD" && activity_tracking_obj == null) {
      let _d = new Date();
      let date_str = _d.getFullYear().toString() + '/' + (_d.getMonth() + 1).toString().lpad("0", 2) + '/' + _d.getDate().toString().lpad("0", 2);
      let time_str = _d.getHours().toString().lpad("0", 2) +':'+ _d.getMinutes().toString().lpad("0", 2) + ':' + _d.getSeconds().toString().lpad("0", 2);

      $('#date_of_record').val(date_str);
      $('#time_of_record').val(time_str);
    }

    // site on change --> load corresponding tenants
    $('#site_id').change(function(){
      let new_html_str = render_tenant_options();
      $('#tenant_id').html(new_html_str);
      $("#tenant_id").val($("#tenant_id option:first").val());
    });

    $('#site_id').change();
}

function render_html_activity_tracking_detail_form(){
  let div_element = document.createElement("div");
  let style_attr = document.createAttribute("style");
  style_attr.value = "width: 600px;";
  div_element.setAttributeNode(style_attr);

  html_str =   '    <div class="row">';
  html_str +=  '        <div class="col-lg-12">';
  html_str +=  '            <div class="row">';
  html_str +=  '              <label class="col-sm-3">Site</label>';
  html_str +=  '              <div class="col-sm-9"><select id="site_id" name="site_id" class="form-control">'+render_site_options()+'</select></div>';
  html_str +=  '            </div>';
  html_str +=  '            <div class="row">';
  html_str +=  '              <label class="col-sm-3">Tenant</label>';
  html_str +=  '              <div class="col-sm-9"><select id="tenant_id" name="tenant_id" class="form-control"></select></div>';
  html_str +=  '            </div>';
  html_str +=  '            <div class="row">';
  html_str +=  '              <label class="col-sm-3">Activity Category</label>';
  html_str +=  '              <div class="col-sm-9"><select id="activity_category_id" name="activity_category_id" class="form-control">'+render_activity_category_options()+'</select></div>';
  html_str +=  '            </div>';
  html_str +=  '            <div class="row">';
  html_str +=  '              <label class="col-sm-3">Date</label>';
  html_str +=  '              <div class="col-sm-5"><input id="date_of_record" name="date_of_record" type="text" class="form-control" placeholder="YYYY/MM/DD"></div>';
  html_str +=  '            </div>';
  html_str +=  '            <div class="row">';
  html_str +=  '              <label class="col-sm-3">Time</label>';
  html_str +=  '              <div class="col-sm-5"><input id="time_of_record" name="time_of_record" type="text" class="form-control" placeholder="HH:MI:SS"></div>';
  html_str +=  '            </div>';
  html_str +=  '            <div class="row">';
  html_str +=  '              <label class="col-sm-3">Comments</label>';
  html_str +=  '              <div class="col-sm-9"><textarea row="4" col="50" id="comments" name="comments" class="form-control" placeholder="Comments"></textarea></div>';
  html_str +=  '            </div>';
  html_str +=  '        </div>';
  html_str +=  '    </div>';
  html_str +=  '    <div class="row validation_error"></div>';

  div_element.innerHTML = html_str;
  return div_element;
}

function render_html_activity_tracking_upload_form() {
  let div_element = document.createElement("div");
  let style_attr = document.createAttribute("style");
  style_attr.value = "width: 600px;";
  div_element.setAttributeNode(style_attr);

  html_str =   '    <div class="row">';
  html_str =   '    <form id="upload_form" method="post" enctype="multipart/form-data">';
  html_str +=  '        <div class="col-lg-12">';
  html_str +=  '            <div class="row">';
  html_str +=  '              <label class="col-sm-1"></label>';
  html_str +=  '              <div class="col-sm-11"><input class="form-control" name="record_file" type="file" accept=".csv,application/vnd.ms-excel" /></div>';
  html_str +=  '            </div>';
  html_str +=  '        </div>';
  html_str +=  '    </form>';
  html_str +=  '    </div>';
  html_str +=  '    <div class="row validation_error"></div>';

  div_element.innerHTML = html_str;
  return div_element;
}

function render_site_options(){
  let site_list = data.site_list;
  let html_str = '';
  site_list.forEach((element, index) => {
    let selected = '';
    if(index == 0){
      selected = ' selected';
    }
    html_str += '<option value="'+element.id+'" '+selected+'>'+element.name+'</option>'; 
  });

  return html_str;
}

function render_activity_category_options(){
  let activity_category_list = data.activity_category_list;
  let html_str = '';
  activity_category_list.forEach((element, index) => {
    let selected = '';
    if(index == 0){
      selected = ' selected';
    }
    html_str += '<option value="'+element.id+'" '+selected+'>'+element.displayed_name+'</option>'; 
  });

  return html_str;
}

function render_tenant_options(){
  let tenant_list = data.tenant_list;
  let html_str = '';
  tenant_list.forEach((element, index) => {
    if($('#site_id').val() == element.site.id){
      html_str += '<option value="'+element.id+'">'+element.unique_name+'</option>'; 
    }
  });

  return html_str;
}

function call_activity_tracking_deleting_api(activity_tracking_id){
  $.ajax({
    type: "DELETE",
    url: "/api/activity_tracking/delete",
    data: activity_tracking_id,
    success: function(result) {
      if (!result.is_successful){
        swal({
          title: "Error",
          text: result.error_message,
          icon: "error",
          dangerMode: true
        });
      } else {
        swal({
          title: "The activity tracking has been deleted!",
          icon: "success"
        }).then((result) => {
          window.location = '/tracking'; // refresh
        });
      }
    },
    error: function(error){
      if(error.status == 0){
        window.location = '/login';
      } else {
        swal({
          title: "Error",
          text: error.status + ' ' + error.statusText,
          icon: "error",
          dangerMode: true
        });
      }
    }
  });
}

function call_activity_tracking_saving_api(activity_tracking_obj){
    $.ajax({
        type: "POST",
        url: "/api/activity_tracking/save",
        data: JSON.stringify(activity_tracking_obj),
        success: function(result) {
          swal.stopLoading();
          swal.close();
          if (!result.is_successful){
            show_activity_tracking_detail_form((activity_tracking_obj.id != null && activity_tracking_obj.id != "") ? "EDIT" : "ADD", activity_tracking_obj);
            setTimeout(function(){ $('.validation_error').text(result.error_message); }, 100);
          } else {
            swal({
              title: "The activity tracking has been "+(activity_tracking_obj.id ? "updated" : "created")+" !",
              icon: "success"
            }).then((result) => {
              window.location = '/tracking'; // refresh
            });
          }
        },
        error: function(error){
          if(error.status == 0){
            window.location = '/login';
          } else {
            swal({
              title: "Error",
              text: error.status + ' ' + error.statusText,
              icon: "error",
              dangerMode: true
            });
          }
        }
      });
}

function call_tracking_import_api(){
  var formData = new FormData(document.getElementById('upload_form'));
  $.ajax({
      url: '/api/activity_tracking/upload',
      type: 'POST',
      data: formData,
      success: function (result) {
        swal.close();
        if (!result.is_successful){
          swal.stopLoading();
          swal({
            title: "Error",
            text: result.error_message,
            icon: "error",
            dangerMode: true
          });
        } else {          
          swal({
            title: "The tracking records have been imported successfully!",
            icon: "success"
          }).then((result) => {
            window.location = '/tracking'; // refresh
          });
        }
      },
      error: function(error){
        if(error.status == 0){
          window.location = '/login';
        } else {
          swal({
            title: "Error",
            text: error.status + ' ' + error.statusText,
            icon: "error",
            dangerMode: true
          });
        }
      },
      cache: false,
      contentType: false,
      processData: false
  });
}

function show_activity_tracking_list(){
  let activity_tracking_list = data.activity_tracking_list;
  var current_user = data.current_user;
  var can_edit_activity_tracking = current_user.permission.can_edit_activity_tracking;
  var can_delete_activity_tracking = current_user.permission.can_delete_activity_tracking;
  
  $("#activity_tracking_table").jsGrid({
          height: "100%",
          width: "100%",
          filtering: false,
          editing: false,
          inserting: false,
          deleting: false,
          sorting: true,
          paging: true,
          autoload: true,
          pageIndex: 1,
          pageSize: 20,
          pageButtonCount: 5,
          confirmDeleting: false,
          fields: [
            { 
              name: "id", title: "", type: "text", width: 0,
              cellRenderer : function(value, item){ return '<td style="display:none">'+item.id+'</td>';}
            },
            { name: "site_name", title: "Site", type: "text", width: 110 },
            { name: "tenant_name", title: "Tenant", type: "text", width: 100 },
            { name: "activity_category_name", title: "Activity Category", type: "text", width: 250 },
            { name: "date_of_record", title: "Date", type: "text", width: 70 },
            { name: "time_of_record", title: "Time", type: "text", width: 70 },
            { name: "comments", title: "Comments", type: "text", width: 250 },
            { type: "control", editButton: can_edit_activity_tracking, deleteButton: can_delete_activity_tracking}
          ],
          data: activity_tracking_list,
          controller: {
            deleteItem: function(args, item) {

            }
          },

          onItemDeleting: function(args){
            // cancel deleting from jsGrid
            args.cancel = true;
          },
          onItemDeleted: function(args){
            //console.log('Done deleting');
            //console.log(args);
          },
          onRefreshed: function(args){
            resgister_control_events();
          }

      });
}

function show_displayed_name(){
  var current_user = data.current_user;

  var angle_down = $("#displayed_name").find("i");
  $("#displayed_name").html(current_user.displayed_name+ ' ');
  $("#displayed_name").append(angle_down);
}