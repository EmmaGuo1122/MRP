

$(document).ready(function() {
  show_activity_category_list();
  show_displayed_name();

  $('.dropdown-content-body > ul > li > a').click(function () {
    window.location = $(this).attr('href');
  });

  // add + in the table header
  var current_user = data.current_user;
  if(current_user.permission.can_add_activity_category){
    var insert_symbol = '<span class="jsgrid-button jsgrid-mode-button jsgrid-insert-mode-button ti-plus" type="button" title=""></span>';
    $('th.jsgrid-control-field').append(insert_symbol);
  }
  
  resgister_control_events();
});

function resgister_control_events(){
  // handle events on table
  $($('.jsgrid-header-cell')[0]).attr('style','display:none');
  
  // ADD
  $('.jsgrid-insert-mode-button').click(function() {
    show_activity_category_detail_form('ADD', null);
  });
  
  // EDIT
  $('.jsgrid-edit-button').click(function () {
    let activity_category_id = $($(this).parent().siblings()[0]).text().trim();
    $.ajax({
        type: "GET",
        url: "/api/activity_category/"+activity_category_id,
        success: function(activity_category_obj) {
          show_activity_category_detail_form('EDIT', activity_category_obj);
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
    var activity_category_id = $($(this).parent().siblings()[0]).text().trim();
    
    swal({
          title: "Are you sure to delete this activity category?",
          icon: "warning",
          buttons: ["No", "Yes"]
    }).then((willDelete) => {
      if (willDelete) {
        call_activity_category_deleting_api(activity_category_id);
      }
    });
  });
}

function show_activity_category_detail_form(mode, activity_category_obj){
  var title = (mode == 'ADD') ? 'Create New Activity Category' : 'Edit Activity Category';
  swal({
      title: title,
      className: 'swal-custom-width',
      content: render_html_activity_category_detail_form(),
      closeOnClickOutside: false,
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
        if(activity_category_obj != null && activity_category_obj['id']){
            save_obj.id = activity_category_obj.id;
        }

        save_obj.code = $('#code').val();
        save_obj.description = $('#description').val();
        save_obj.alert_level = $('#alert_level').val();

        $('.validation_error').text('');
        call_activity_category_saving_api(save_obj);
      }
  });

  setTimeout(function(){ when_activity_category_detail_modal_ready(mode, activity_category_obj); }, 100);
}

function when_activity_category_detail_modal_ready(mode, activity_category_obj) {
    if(activity_category_obj != null){
        $('#code').val(activity_category_obj.code);
        $('#description').val(activity_category_obj.description);
        $('#alert_level').val(activity_category_obj.alert_level);
    }
}

function render_html_activity_category_detail_form(){
  let div_element = document.createElement("div");
  let style_attr = document.createAttribute("style");
  style_attr.value = "width: 600px;";
  div_element.setAttributeNode(style_attr);

  html_str =   '    <div class="row">';
  html_str +=  '        <div class="col-lg-12">';
  html_str +=  '            <div class="row">';
  html_str +=  '              <label class="col-sm-3">Code</label>';
  html_str +=  '              <div class="col-sm-9"><input id="code" name="code" type="text" class="form-control" placeholder="Code"></div>';
  html_str +=  '            </div>';
  html_str +=  '            <div class="row">';
  html_str +=  '              <label class="col-sm-3">Description</label>';
  html_str +=  '              <div class="col-sm-9"><input id="description" name="description" type="text" class="form-control" placeholder="Description"></div>';
  html_str +=  '            </div>';
  html_str +=  '            <div class="row">';
  html_str +=  '              <label class="col-sm-3">Alert level</label>';
  html_str +=  '              <div class="col-sm-9"><select id="alert_level" name="alert_level" class="form-control">'+render_alert_level_options()+'</select></div>';
  html_str +=  '            </div>';
  html_str +=  '        </div>';
  html_str +=  '    </div>';
  html_str +=  '    <div class="row validation_error"></div>';

  div_element.innerHTML = html_str;
  return div_element;
}

function render_alert_level_options(){
  let alert_level_list = data.alert_level_list;
  let html_str = '';
  alert_level_list.forEach((element, index) => {
    let selected = '';
    if(index == 0){
      selected = ' selected';
    }
    html_str += '<option value="'+element+'" '+selected+'>'+element+'</option>'; 
  });

  return html_str;
}

function call_activity_category_deleting_api(activity_category_id){
  $.ajax({
    type: "DELETE",
    url: "/api/activity_category/delete",
    data: activity_category_id,
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
          title: "The activity category has been deleted!",
          icon: "success"
        }).then((result) => {
          window.location = '/activity_categories'; // refresh
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

function call_activity_category_saving_api(activity_category_obj){
    $.ajax({
        type: "POST",
        url: "/api/activity_category/save",
        data: JSON.stringify(activity_category_obj),
        success: function(result) {
          swal.stopLoading();
          swal.close();
          if (!result.is_successful){
            show_activity_category_detail_form((activity_category_obj.id != null && activity_category_obj.id != "") ? "EDIT" : "ADD", activity_category_obj);      
            setTimeout(function(){ $('.validation_error').text(result.error_message); }, 100);
          } else {
            swal({
              title: "The activity category has been "+(activity_category_obj.id ? "updated" : "created")+" !",
              icon: "success"
            }).then((result) => {
              window.location = '/activity_categories'; // refresh
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

function show_activity_category_list(){
  let activity_category_list = data.activity_category_list;
  var current_user = data.current_user;
  var can_edit_activity_category = current_user.permission.can_edit_activity_category;
  var can_delete_activity_category = current_user.permission.can_delete_activity_category;
  
  $("#activity_category_table").jsGrid({
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
            { name: "code", title: "Code", type: "text", width: 100 },
            { name: "description", title: "Description", type: "text", width: 300 },
            { name: "alert_level", title: "Alert Level", type: "text", width: 100 },
            { type: "control", editButton: can_edit_activity_category, deleteButton: can_delete_activity_category}
          ],
          data: activity_category_list,
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