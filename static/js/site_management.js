
var MAX_NOTIFICATION_EMAILS = 2;

$(document).ready(function() {
  show_site_list();
  show_displayed_name();

  $('.dropdown-content-body > ul > li > a').click(function () {
    window.location = $(this).attr('href');
  });

  // add + in the table header
  var current_user = data.current_user;
  if(current_user.permission.can_add_site){
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
    show_site_detail_form('ADD', null);
  });

  // EDIT
  $('.jsgrid-edit-button').click(function () {
    let site_id = $($(this).parent().siblings()[0]).text().trim();
    $.ajax({
        type: "GET",
        url: "/api/site/"+site_id,
        success: function(site_obj) {
          show_site_detail_form('EDIT', site_obj);
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
    var site_id = $($(this).parent().siblings()[0]).text().trim();
    
    swal({
          title: "Are you sure to delete this site?",
          icon: "warning",
          buttons: ["No", "Yes"]
    }).then((willDelete) => {
      if (willDelete) {
        call_site_deleting_api(site_id);
      }
    });
  });
}

function show_site_detail_form(mode, site_obj){
  var title = (mode == 'ADD') ? 'Create New Site' : 'Edit Site';
  swal({
      title: title,
      className: 'swal-custom-width',
      content: render_html_site_detail_form(),
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
        if(site_obj != null && site_obj['id']){
            save_obj.id = site_obj.id;
        }

        save_obj.name = $('#name').val();
        save_obj.address_line1 = $('#address_line1').val();
        save_obj.address_line2 = $('#address_line2').val();
        save_obj.city = $('#city').val();
        save_obj.province = $('#province').val();
        save_obj.postal_code = $('#postal_code').val();
        save_obj.manager_id = $('#manager_id').val();
        save_obj.notification_emails = [];
        let span_tags = $(".tdl-content ul li span");
        for(var i = 0; i < span_tags.length; i++){
          let span_tag = $(span_tags[i]);
          save_obj.notification_emails.push({"notification_email": span_tag.html()});
        }

        $('.validation_error').text('');
        call_site_saving_api(save_obj);
      }
  });

  setTimeout(function(){ when_site_detail_modal_ready(mode, site_obj); }, 100);
}

function when_site_detail_modal_ready(mode, site_obj) {
    if(site_obj != null){
        $('#name').val(site_obj.name);
        $('#address_line1').val(site_obj.address_line1);
        $('#address_line2').val(site_obj.address_line2);
        $('#city').val(site_obj.city);
        $('#province').val(site_obj.province);
        $('#postal_code').val(site_obj.postal_code);
        $('#manager_id').val(site_obj.manager_id);
        $(".tdl-content ul").html('');
        site_obj.notification_emails.forEach((email) => {
          $(".tdl-content ul").append("<li><label><i></i><span>"+email.notification_email+"</span><a href='#' class='ti-close'></a></label></li>");
        });
    } else {
      $('#manager_id').val(null);
    }

    $(".tdl-new").on('keypress', function(e) {
      $('.validation_error').text('');
      var code = (e.keyCode ? e.keyCode : e.which);
      if (code == 13) {
          var v = $(this).val();
          var s = v.replace(/ +?/g, '');
          if (s == "") {
              return false;
          } else {
              let li_count = $(".tdl-content ul").find('li').length;
              let span_tags = $(".tdl-content ul li span");
              for(var i = 0; i < span_tags.length; i++){
                let span_tag = $(span_tags[i]);
                if(v.trim() == span_tag.html()){
                  $('.validation_error').text('The email '+v.trim()+' is already added.');
                  return false;
                }
              }
              if (li_count < MAX_NOTIFICATION_EMAILS) {
                $(".tdl-content ul").append("<li><label><i></i><span>"+v.trim()+"</span><a href='#' class='ti-close'></a></label></li>");
                $(this).val("");
              } else {
                $('.validation_error').text('The maximun number of notification emails is '+MAX_NOTIFICATION_EMAILS);
              }
          }
      }
    });

    $(".tdl-content a").on("click", function() {
      $('.validation_error').text('');
      var _li = $(this).parent().parent("li");
      _li.addClass("remove").stop().delay(100).slideUp("fast", function() {
          _li.remove();
      });
      return false;
    });

    // for dynamically created a tags
    $(".tdl-content").on('click', "a", function() {
      $('.validation_error').text('');
      var _li = $(this).parent().parent("li");
      _li.addClass("remove").stop().delay(100).slideUp("fast", function() {
          _li.remove();
      });
      return false;
    });
}

function render_html_site_detail_form(){
  let div_element = document.createElement("div");
  let style_attr = document.createAttribute("style");
  style_attr.value = "width: 700px;";
  div_element.setAttributeNode(style_attr);

  html_str =   '    <div class="row">';
  html_str +=  '        <div class="col-lg-12">';
  html_str +=  '            <div class="row">';
  html_str +=  '              <label class="col-sm-2">Name</label>';
  html_str +=  '              <div class="col-sm-10"><input id="name" name="name" type="text" class="form-control" placeholder="Name"></div>';
  html_str +=  '            </div>';
  html_str +=  '            <div class="row">';
  html_str +=  '              <label class="col-sm-2">Address</label>';
  html_str +=  '              <div class="col-sm-5"><input id="address_line1" name="address_line1" type="text" class="form-control" placeholder="Address Line 1"></div>';
  html_str +=  '              <div class="col-sm-5"><input id="address_line2" name="address_line2" type="text" class="form-control" placeholder="Address Line 2"></div>';
  html_str +=  '            </div>';
  html_str +=  '            <div class="row">';
  html_str +=  '              <label class="col-sm-2">City</label>';
  html_str +=  '              <div class="col-sm-5"><input id="city" name="city" type="text" class="form-control" placeholder="City"></div>';
  html_str +=  '              <div class="col-sm-5"><select id="province" name="province" class="form-control">'+render_province_options()+'</select></div>';
  html_str +=  '            </div>';
  html_str +=  '            <div class="row">';
  html_str +=  '              <label class="col-sm-2">Postal Code</label>';
  html_str +=  '              <div class="col-sm-5"><input id="postal_code" name="postal_code" type="text" class="form-control" placeholder="Postal Code"></div>';
  html_str +=  '            </div>';
  html_str +=  '            <div class="row">';
  html_str +=  '              <label class="col-sm-2">Manager</label>';
  html_str +=  '              <div class="col-sm-5"><select id="manager_id" name="manager_id" class="form-control">'+render_manager_options()+'</select></div>';
  html_str +=  '            </div>';
  html_str +=  '            <div class="row">';
  html_str +=  '              <label class="col-sm-2">Notification Emails</label>';
  html_str +=  '              <div class="col-sm-5 todo-list">';
  html_str +=  '                <div class="tdl-holder">';
  html_str +=  '                  <div class="tdl-content">';
  html_str +=  '                    <ul id="notification_email_list">';
  html_str +=  '                    </ul>';
  html_str +=  '                  </div>';
  html_str +=  '                  <input id="notification_email_input" type="text" class="tdl-new form-control" placeholder="Write new email address and hit Enter...">';
  html_str +=  '                </div>';
  html_str +=  '              </div>';
  html_str +=  '            </div>';
  html_str +=  '        </div>';
  html_str +=  '    </div>';
  html_str +=  '    <div class="row validation_error"></div>';

  div_element.innerHTML = html_str;
  return div_element;
}

function render_province_options(){
  let province_list = data.province_list;
  let html_str = '';
  province_list.forEach((element, index) => {
    let selected = '';
    if(index == 0){
      selected = ' selected';
    }
    html_str += '<option value="'+element.code+'" '+selected+'>'+element.code+' - '+element.name+'</option>'; 
  });

  return html_str;
}

function render_manager_options(){
  let manager_list = data.manager_list;
  let html_str = '';
  manager_list.forEach((element, index) => {
    let selected = '';
    if(index == 0){
      selected = ' selected';
    }
    html_str += '<option value="'+element.id+'" '+selected+'>'+element.displayed_full_name+'</option>'; 
  });

  return html_str;
}

function call_site_deleting_api(site_id){
  $.ajax({
    type: "DELETE",
    url: "/api/site/delete",
    data: site_id,
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
          title: "The site has been deleted!",
          icon: "success"
        }).then((result) => {
          window.location = '/sites'; // refresh
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

function call_site_saving_api(site_obj){
    $.ajax({
        type: "POST",
        url: "/api/site/save",
        data: JSON.stringify(site_obj),
        success: function(result) {
          swal.stopLoading();
          swal.close();

          if (!result.is_successful){
            show_site_detail_form((site_obj.id != null && site_obj.id != "") ? "EDIT" : "ADD", site_obj);
            setTimeout(function(){ $('.validation_error').text(result.error_message); }, 100);
          } else {
            swal({
              title: "The site has been "+(site_obj.id ? "updated" : "created")+" !",
              icon: "success"
            }).then((result) => {
              window.location = '/sites'; // refresh
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

function show_site_list(){
  let site_list = data.site_list;
  var current_user = data.current_user;
  var can_edit_site = current_user.permission.can_edit_site;
  var can_delete_site = current_user.permission.can_delete_site;
  
  $("#site_table").jsGrid({
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
            { name: "name", title: "Name", type: "text", width: 150 },
            { name: "displayed_address", title: "Address", type: "text", width: 250 },
            { name: "manager_name", title: "Manager", type: "text", width: 150 },
            { type: "control", editButton: can_edit_site, deleteButton: can_delete_site}
          ],
          data: site_list,
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