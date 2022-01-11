

$(document).ready(function() {
  show_system_configuration_list();
  show_displayed_name();

  $('.dropdown-content-body > ul > li > a').click(function () {
    window.location = $(this).attr('href');
  });

  resgister_control_events();
    
});

function resgister_control_events(){
  // handle events on table
  $($('.jsgrid-header-cell')[0]).attr('style','display:none');

  // EDIT
  $('.jsgrid-edit-button').click(function () {
    let system_configuration_id = $($(this).parent().siblings()[0]).text().trim();
    $.ajax({
        type: "GET",
        url: "/api/system_configuration/"+system_configuration_id,
        success: function(system_configuration_obj) {
          show_system_configuration_detail_form(system_configuration_obj);
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
}

function show_system_configuration_detail_form(system_configuration_obj){
  var title = 'Edit System Configuration';
  swal({
      title: title,
      className: 'swal-custom-width',
      closeOnClickOutside: false,
      content: render_html_system_configuration_detail_form(),
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
        if(system_configuration_obj != null && system_configuration_obj['id']){
            save_obj.id = system_configuration_obj.id;
        }

        save_obj.conf_key = $('#conf_key').val();
        save_obj.conf_value = $('#conf_value').val();
        save_obj.description = $('#description').val();

        $('.validation_error').text('');
        call_system_configuration_saving_api(save_obj);
      }
  });

  setTimeout(function(){ when_system_configuration_detail_modal_ready(system_configuration_obj); }, 100);
}

function when_system_configuration_detail_modal_ready(system_configuration_obj) {
    if(system_configuration_obj != null){
        $('#conf_key').val(system_configuration_obj.conf_key);
        $('#conf_value').val(system_configuration_obj.conf_value);
        $('#description').val(system_configuration_obj.description);
        $('#conf_key').attr('disabled', 'disabled');
    }
}

function render_html_system_configuration_detail_form(){
  let div_element = document.createElement("div");
  let style_attr = document.createAttribute("style");
  style_attr.value = "width: 600px;";
  div_element.setAttributeNode(style_attr);

  html_str =   '    <div class="row">';
  html_str +=  '        <div class="col-lg-12">';
  html_str +=  '            <div class="row">';
  html_str +=  '              <label class="col-sm-3">Key</label>';
  html_str +=  '              <div class="col-sm-9"><input id="conf_key" name="conf_key" type="text" class="form-control" placeholder="Key"></div>';
  html_str +=  '            </div>';
  html_str +=  '            <div class="row">';
  html_str +=  '              <label class="col-sm-3">Value</label>';
  html_str +=  '              <div class="col-sm-9"><input id="conf_value" name="conf_value" type="text" class="form-control" placeholder="Value"></div>';
  html_str +=  '            </div>';
  html_str +=  '            <div class="row">';
  html_str +=  '              <label class="col-sm-3">Description</label>';
  html_str +=  '              <div class="col-sm-9"><input id="description" name="description" type="text" class="form-control" placeholder="Description"></div>';
  html_str +=  '            </div>';
  html_str +=  '        </div>';
  html_str +=  '    </div>';
  html_str +=  '    <div class="row validation_error"></div>';

  div_element.innerHTML = html_str;
  return div_element;
}

function call_system_configuration_saving_api(system_configuration_obj){
    $.ajax({
        type: "POST",
        url: "/api/system_configuration/save",
        data: JSON.stringify(system_configuration_obj),
        success: function(result) {
          swal.stopLoading();
          swal.close();
          if (!result.is_successful){
            show_system_configuration_detail_form(system_configuration_obj);
            setTimeout(function(){ $('.validation_error').text(result.error_message); }, 100);            
          } else {
            swal({
              title: "The configuration has been updated!",
              icon: "success"
            }).then((result) => {
              window.location = '/system_configurations'; // refresh
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

function show_system_configuration_list(){
  let system_configuration_list = data.system_configuration_list;
  var current_user = data.current_user;
  var can_edit_system_configuration = current_user.permission.can_edit_system_configuration;
  
  $("#system_configuration_table").jsGrid({
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
            { name: "conf_key", title: "Key", type: "text", width: 150 },
            { name: "conf_value", title: "Value", type: "text", width: 100 },
            { name: "description", title: "Description", type: "text", width: 250 },
            { type: "control", editButton: can_edit_system_configuration, deleteButton: false}
          ],
          data: system_configuration_list,
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