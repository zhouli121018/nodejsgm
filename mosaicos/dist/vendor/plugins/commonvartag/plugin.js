/**
 * plugin.js
 *
 * Released under LGPL License.
 * Copyright (c) 1999-2015 Ephox Corp. All rights reserved
 *
 * License: http://www.tinymce.com/license
 * Contributing: http://www.tinymce.com/contributing
 */

/*global tinymce:true */

tinymce.PluginManager.add('commonvartag', function(editor) {

    var var_menuItems = [], var_lastFormat, var_defaultButtonTimeFormat;
    var var_sourse_keys = [
        "{MOTTO}",
        "{JOKE}",
        "{NOVEL}",
        "{ENNOVEL}"
    ];

    var sourse_formats = {
        "{MOTTO}": "格言名句",
        "{JOKE}": "笑话库" ,
        "{NOVEL}":  "历史名著",
        "{ENNOVEL}":  "英文小说"
    };


    function getVarDesc(key) {
        return sourse_formats[key];
    }

    function insertCommonvar(key) {
        editor.insertContent(key);
    }

    editor.addButton('commonvartag', {
        type: 'splitbutton',
        text: '公共变量',
        title: '公共变量',
        onclick: function() {
            insertCommonvar(var_lastFormat || var_defaultButtonTimeFormat);
        },
        menu: var_menuItems
    });

    tinymce.each(var_sourse_keys, function(key) {
        if (!var_defaultButtonTimeFormat) {
            var_defaultButtonTimeFormat = key;
        }
        var_menuItems.push({
            text: getVarDesc(key),
            onclick: function() {
                var_lastFormat = key;
                insertCommonvar(key);
            }
        });
    });

    editor.addMenuItem('commonvartag', {
        text: '公共变量',
        menu: var_menuItems,
        context: 'insert'
    });

});