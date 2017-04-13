document.getElementById('$INSERT-SITE-ID$_passwd').innerHTML = '$INSERT-PASSWORD$';

var $INSERT-SITE-ID$_passwd_elm = document.getElementById('$INSERT-SITE-ID$_passwd');
var $INSERT-SITE-ID$_passwd_cipher = $INSERT-SITE-ID$_passwd_elm.innerHTML;
var $INSERT-SITE-ID$_passwd_plain = $INSERT-SITE-ID$_passwd_elm.innerHTML;
var $INSERT-SITE-ID$_passwd_show = 0;
var $INSERT-SITE-ID$_passwd_copy = 0;

$INSERT-SITE-ID$_passwd_elm.ondblclick = function() {
    if (document.selection) {
        var range = document.body.createTextRange();
        range.moveToElementText($INSERT-SITE-ID$_passwd_elm);
        range.select();
    } else if (window.getSelection) {
        var range = document.createRange();
        range.selectNode($INSERT-SITE-ID$_passwd_elm);
        window.getSelection().addRange(range);
    }
}

$INSERT-SITE-ID$_do_copy = function() {
    var body_element = document.getElementsByTagName('body')[0];
    var hidden_input = document.createElement('input');

    hidden_input.style.position='absolute';
    hidden_input.style.left='-9999px';
    body_element.appendChild(hidden_input);

    hidden_input.value = $INSERT-SITE-ID$_passwd_plain;
    (function (elm) {
        if (elm && elm.select) {
          elm.select();

          try {
            document.execCommand('copy');
            elm.blur();
          }
          catch (err) {}
        }
    })(hidden_input);
    body_element.removeChild(hidden_input);

    window.setTimeout(function() {
        var waiting = function() {
            copy_count--;
          
            if (copy_count == 0) {
                if (!has_left) {
                    copy_count++;

                    window.setTimeout(function() {
                      waiting();
                    }, 1000);
                } else {
                    prompt('Clear your clipboard: Ctrl+C, Enter', 'nothing');
                    has_left = false;
                }
            }
        };

        waiting();
    }, 30000);

    copy_count++;
    $INSERT-SITE-ID$_do_hide();
}
$INSERT-SITE-ID$_passwd_elm.oncopy = $INSERT-SITE-ID$_do_copy;

function $INSERT-SITE-ID$_decrypt() {
    $INSERT-SITE-ID$_passwd_show++;
    
    window.setTimeout(function() {
        $INSERT-SITE-ID$_passwd_show--;

        if ($INSERT-SITE-ID$_passwd_show == 0) {
            $INSERT-SITE-ID$_do_hide();
        }
    }, 5000);

    AES_Init();

    var key = $("#$INSERT-SITE-ID$_decrypt_key").val();
    var key_bytes = new Array(16);

    if (key == '') {
        $INSERT-SITE-ID$_do_hide();
        return;
    }

    for(var i = 0; i < 16; i++) {
        key_bytes[i] = 0;
    }

    for (var i = 0; i < key.length; i++) {
        key_bytes[i] = key.charCodeAt(i);
    }

    AES_ExpandKey(key_bytes);

    var val = window.atob($INSERT-SITE-ID$_passwd_cipher);
    var val_bytes = new Array(16);
    var passwd = '';

    for (var i = 0; i < val.length / 16; i++) {

        for(var j = 0; j < 16; j++) {
            val_bytes[j] = 0;
        }

        for (var j = 0; j < 16; j++) {
            val_bytes[j] = val.charCodeAt(j + 16 * i);
        }

        AES_Decrypt(val_bytes, key_bytes);
        passwd += new String(bin2string(val_bytes));
    }

    $INSERT-SITE-ID$_passwd_plain = passwd;
        
    if (!$("#$INSERT-SITE-ID$_toggle_input").is(":checked")) {
        $INSERT-SITE-ID$_passwd_elm.innerHTML = passwd;
    } else {
        bullets = '';
        
        for (var j = 0; j < passwd.length; j++) {
          if (passwd.charCodeAt(j) > 127)
              continue;
          else
              bullets += '&#8226';
        }
        
        $INSERT-SITE-ID$_passwd_elm.innerHTML = '<div style="font-weight:bolder">' + bullets + '</div>'
    }

    AES_Done();
}

function $INSERT-SITE-ID$_del() {
    var user = window.location.pathname.replace('/', '');
    var site = $("#$INSERT-SITE-ID$_site").html();
    
    while (site.includes('\'') || site.includes('\"') || site.includes(' ')) {
        site = site.replace('\'', '_APOS_');
        site = site.replace('\"', '_QUOT_');
        site = site.replace(' ', '_SPACE_');
    }

    $.ajax({
        url: "http://$INSERT-HOST-NAME$:$INSERT-POST-PORT$",
        type: "POST",
        data: {"command":"del", "user":user, "site":site},
        dataType: "text",
        success: function (result) {
            if (result != '')
                $('body').html(result);
        },
        error: function (xhr, ajaxOptions, thrownError) {
            alert(xhr.status);
            alert(thrownError);
        }
    });
}

function $INSERT-SITE-ID$_do_hide() {
    $("#$INSERT-SITE-ID$_decrypt_key").val('');

    $INSERT-SITE-ID$_passwd_elm.innerHTML = $INSERT-SITE-ID$_passwd_cipher;
    $INSERT-SITE-ID$_passwd_plain = $INSERT-SITE-ID$_passwd_cipher;

    $("#$INSERT-SITE-ID$_decrypt_key").focus();
    $("#$INSERT-SITE-ID$_decrypt_key").blur();
}