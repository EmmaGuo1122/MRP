

$(document).ready(function() {
  show_tenant_list();
  show_displayed_name();

  $('.dropdown-content-body > ul > li > a').click(function () {
    window.location = $(this).attr('href');
  });

  // add + in the table header
  var current_user = data.current_user;
  if(current_user.permission.can_add_tenant){
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
    show_tenant_detail_form('ADD', null);
  });

  // EDIT
  $('.jsgrid-edit-button').click(function () {
    let tenant_id = $($(this).parent().siblings()[0]).text().trim();
    $.ajax({
        type: "GET",
        url: "/api/tenant/"+tenant_id,
        success: function(tenant_obj) {
          show_tenant_detail_form('EDIT', tenant_obj);
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
    var tenant_id = $($(this).parent().siblings()[0]).text().trim();
    
    swal({
          title: "Are you sure to delete this tenant?",
          icon: "warning",
          buttons: ["No", "Yes"]
    }).then((willDelete) => {
      if (willDelete) {
        call_tenant_deleting_api(tenant_id);
      }
    });
  });
}
 

function show_tenant_detail_form(mode, tenant_obj){
  var title = (mode == 'ADD') ? 'Create New Tenant' : 'Edit Tenant';
  swal({
      title: title,
      className: 'swal-custom-width',
      content: render_html_tenant_detail_form(),
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
        if(tenant_obj != null && tenant_obj['id']){
            save_obj.id = tenant_obj.id;
        }

        save_obj.unique_name = $('#unique_name').val();
        save_obj.unit = $('#unit').val();
        save_obj.site_id = $('#site').val();
        save_obj.status = $('#status').val();

        $('.validation_error').text('');
        call_tenant_saving_api(save_obj);
      }
  });

  setTimeout(function(){ when_tenant_detail_modal_ready(mode, tenant_obj); }, 100);
}

function when_tenant_detail_modal_ready(mode, tenant_obj) {
    if(tenant_obj != null){
        $('#unique_name').val(tenant_obj.unique_name);
        $('#unit').val(tenant_obj.unit);
        $('#site').val(tenant_obj.site_id);
        $('#status').val(tenant_obj.status);
    }

    if(mode == "EDIT"){
      $('#site').attr('disabled','disabled');
    }
}

function render_html_tenant_detail_form(){
  let div_element = document.createElement("div");
  let style_attr = document.createAttribute("style");
  style_attr.value = "width: 600px;";
  div_element.setAttributeNode(style_attr);

  html_str =   '    <div class="row">';
  html_str +=  '        <div class="col-lg-12">';
  html_str +=  '            <div class="row">';
  html_str +=  '              <label class="col-sm-3">Unique name</label>';
  html_str +=  '              <div class="col-sm-9"><input id="unique_name" name="unique_name" type="text" class="form-control" placeholder="Unique name"></div>';
  html_str +=  '            </div>';
  html_str +=  '            <div class="row">';
  html_str +=  '              <label class="col-sm-3">Unit</label>';
  html_str +=  '              <div class="col-sm-9"><input id="unit" name="unit" type="text" class="form-control" placeholder="Unit"></div>';
  html_str +=  '            </div>';
  html_str +=  '            <div class="row">';
  html_str +=  '              <label class="col-sm-3">Site</label>';
  html_str +=  '              <div class="col-sm-9"><select id="site" name="site" class="form-control">'+render_site_options()+'</select></div>';
  html_str +=  '            </div>';
  html_str +=  '            <div class="row">';
  html_str +=  '              <label class="col-sm-3">Status</label>';
  html_str +=  '              <div class="col-sm-9"><select id="status" name="status" class="form-control">'+render_tenant_status_options()+'</select></div>';
  html_str +=  '            </div>';
  html_str +=  '        </div>';
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

function render_tenant_status_options(){
  let status_list = data.status_list;
  let html_str = '';
  status_list.forEach((element, index) => {
    let selected = '';
    if(index == 0){
      selected = ' selected';
    }
    html_str += '<option value="'+element+'" '+selected+'>'+element+'</option>'; 
  });

  return html_str;
}

function call_tenant_deleting_api(tenant_id){
  $.ajax({
    type: "DELETE",
    url: "/api/tenant/delete",
    data: tenant_id,
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
          title: "The tenant has been deleted!",
          icon: "success"
        }).then((result) => {
          window.location = '/tenants'; // refresh
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

function call_tenant_saving_api(tenant_obj){
    $.ajax({
        type: "POST",
        url: "/api/tenant/save",
        data: JSON.stringify(tenant_obj),
        success: function(result) {
          swal.stopLoading();
          swal.close();
          if (!result.is_successful){
            show_tenant_detail_form((tenant_obj.id != null && tenant_obj.id != "") ? "EDIT" : "ADD", tenant_obj);
            setTimeout(function(){ $('.validation_error').text(result.error_message); }, 100);
          } else {
            swal({
              title: "The tenant has been "+(tenant_obj.id ? "updated" : "created")+" !",
              icon: "success"
            }).then((result) => {
              window.location = '/tenants'; // refresh
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

function show_tenant_list(){
  let tenant_list = data.tenant_list;
  var current_user = data.current_user;
  var can_edit_tenant = current_user.permission.can_edit_tenant;
  var can_delete_tenant = current_user.permission.can_delete_tenant;
  
  $("#tenant_table").jsGrid({
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
            { name: "unique_name", title: "Unique Name", type: "text", width: 150 },
            { name: "unit", title: "Unit", type: "text", width: 250 },
            { name: "site_name", title: "Site", type: "text", width: 150 },
            { name: "status", title: "Status", type: "text", width: 150 },
            { type: "control", editButton: can_edit_tenant, deleteButton: can_delete_tenant}
          ],
          data: tenant_list,
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