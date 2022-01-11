
$(document).ready(function() {
  show_user_list();
  show_displayed_name();

  $('.dropdown-content-body > ul > li > a').click(function () {
    window.location = $(this).attr('href');
  });

  // add + in the table header
  var current_user = data.current_user;
  if(current_user.permission.can_add_user){
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
    show_user_detail_form('ADD', null);
  });

  // EDIT
  $('.jsgrid-edit-button').click(function () {
    let user_id = $($(this).parent().siblings()[0]).text().trim();
    $.ajax({
        type: "GET",
        url: "/api/user/"+user_id,
        success: function(user_obj) {
          show_user_detail_form('EDIT', user_obj);
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
    var user_id = $($(this).parent().siblings()[0]).text().trim();
    
    swal({
          title: "Are you sure to delete this user?",
          icon: "warning",
          buttons: ["No", "Yes"]
    }).then((willDelete) => {
      if (willDelete) {
        call_user_deleting_api(user_id);
      }
    });
  });
}

function show_user_detail_form(mode, user_obj){
  var title = (mode == 'ADD') ? 'Create New User' : 'Edit User';
  swal({
      title: title,
      className: 'swal-custom-width',
      closeOnClickOutside: false,
      content: render_html_user_detail_form(),
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
        if(user_obj != null && user_obj['id']){
            save_obj.id = user_obj.id;
        }

        save_obj.first_name = $('#first_name').val();
        save_obj.last_name = $('#last_name').val();
        save_obj.username = $('#username').val();
        save_obj.status = $('#status').val();
        save_obj.role = $('#role').val();
        save_obj.email = $('#email').val();
        save_obj.site_id = $('#site').val();

        $('.validation_error').text('');

        call_user_saving_api(save_obj);
      }
  });

  setTimeout(function(){ when_user_detail_modal_ready(mode, user_obj); }, 100);
}

function when_user_detail_modal_ready(mode, user_obj) {
    $('#role').change(function () {
        let selected_role = $(this).val();
        if(selected_role == 'USER'){
            $('#site_div').attr("style", "display:flex;");
        } else {
            $('#site_div').attr("style", "display:none;");
        }
    });

    if(user_obj != null){
      $('#first_name').val(user_obj.first_name);
      $('#last_name').val(user_obj.last_name);
      $('#username').val(user_obj.username);
      
      $('#email').val(user_obj.email);
      $('#status').val(user_obj.status);
      $('#role').val(user_obj.role);
      $('#site').val(user_obj.site_id);
      var current_user = data.current_user;
      if(current_user.username == user_obj.username){
          $('#role').attr('disabled', 'disabled');
      }
    } 

    if(mode == "EDIT") {
      $('#username').attr('disabled', 'disabled');
    } else {
      $('#status').attr('disabled', 'disabled');
    }

    $('#role').change();
}

function render_html_user_detail_form(){
  let div_element = document.createElement("div");
  let style_attr = document.createAttribute("style");
  style_attr.value = "width: 900px;";
  div_element.setAttributeNode(style_attr);

  html_str =   '    <div class="row">';
  html_str +=  '        <div class="col-lg-6">';
  html_str +=  '            <div class="row">';
  html_str +=  '              <label class="col-sm-3">First name</label>';
  html_str +=  '              <div class="col-sm-8"><input id="first_name" name="first_name" type="text" class="form-control" placeholder="First name"></div>';
  html_str +=  '            </div>';
  html_str +=  '            <div class="row">';
  html_str +=  '              <label class="col-sm-3">Last name</label>';
  html_str +=  '              <div class="col-sm-8"><input id="last_name" name="last_name" type="text" class="form-control" placeholder="Last name"></div>';
  html_str +=  '            </div>';
  html_str +=  '            <div class="row">';
  html_str +=  '              <label class="col-sm-3">Username</label>';
  html_str +=  '              <div class="col-sm-8"><input id="username" name="username" type="text" class="form-control" placeholder="Username"></div>';
  html_str +=  '            </div>';
  html_str +=  '        </div>';
  html_str +=  '        <div class="col-lg-6">';
  html_str +=  '            <div class="row">';
  html_str +=  '              <label class="col-sm-3">Email</label>';
  html_str +=  '              <div class="col-sm-8"><input id="email" name="email" type="text" class="form-control" placeholder="Email"></div>';
  html_str +=  '            </div>';
  html_str +=  '            <div class="row">';
  html_str +=  '              <label class="col-sm-3">Role</label>';
  html_str +=  '              <div class="col-sm-8"><select id="role" name="role" class="form-control">'+render_user_role_options()+'</select></div>';
  html_str +=  '            </div>';
  html_str +=  '            <div class="row">';
  html_str +=  '              <label class="col-sm-3">Status</label>';
  html_str +=  '              <div class="col-sm-8"><select id="status" name="status" class="form-control">'+render_user_status_options()+'</select></div>';
  html_str +=  '            </div>';
  html_str +=  '            <div class="row" id="site_div" style="display:none;">';
  html_str +=  '              <label class="col-sm-3">Site</label>';
  html_str +=  '              <div class="col-sm-8"><select id="site" name="site" class="form-control">'+render_site_options()+'</select></div>';
  html_str +=  '            </div>';
  html_str +=  '        </div>';
  html_str +=  '    </div>';
  html_str +=  '    <div class="row validation_error"></div>';

  div_element.innerHTML = html_str;
  return div_element;
}

function render_user_status_options(){
  let user_status_list = data.user_status_list;
  let html_str = '';
  user_status_list.forEach((element, index) => {
    let selected = '';
    if(index == 0){
      selected = ' selected';
    }
    html_str += '<option value="'+element+'" '+selected+'>'+element+'</option>'; 
  });

  return html_str;
}

function render_user_role_options(){
  let user_role_list = data.user_role_list;
  let html_str = '';
  user_role_list.forEach((element, index) => {
    let selected = '';
    if(index == 0){
      selected = ' selected';
    }
    html_str += '<option value="'+element+'" '+selected+'>'+element+'</option>'; 
  });

  return html_str;
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

function call_user_deleting_api(user_id){
  $.ajax({
    type: "DELETE",
    url: "/api/user/delete",
    data: user_id,
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
          title: "The user has been deleted!",
          icon: "success"
        }).then((result) => {
          window.location = '/users'; // refresh
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

function call_user_saving_api(user_obj){
    $.ajax({
        type: "POST",
        url: "/api/user/save",
        data: JSON.stringify(user_obj),
        success: function(result) {
          swal.stopLoading();
          swal.close();
          if (!result.is_successful){
            show_user_detail_form((user_obj.id != null && user_obj.id != "") ? "EDIT" : "ADD", user_obj);
            setTimeout(function(){ $('.validation_error').text(result.error_message); }, 100);            
          } else {
            swal({
              title: "The user has been "+(user_obj.id ? "updated" : "created")+" !",
              icon: "success"
            }).then((result) => {
              window.location = '/users'; // refresh
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

function show_user_list(){
  let user_list = data.user_list;
  var current_user = data.current_user;
  var can_edit_user = current_user.permission.can_edit_user;
  var can_delete_user = current_user.permission.can_delete_user;
  
  $("#user_table").jsGrid({
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
            { name: "username", title: "Username", type: "text", width: 150 },
            { name: "first_name", title: "First Name", type: "text", width: 150 },
            { name: "last_name", title: "Last Name", type: "text", width: 150 },
            { name: "role", title: "Role", type: "text", width: 120 },
            { name: "email", title: "Email", type: "text", width: 180},
            { name: "status", title: "Status", type: "text", width: 120, align: "left" },
            { type: "control", editButton: can_edit_user, deleteButton: can_delete_user}
          ],
          data: user_list,
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