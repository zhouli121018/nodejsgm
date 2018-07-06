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

tinymce.PluginManager.add('commonvar', function(editor) {

    var var_menuItems = [], var_lastFormat, var_defaultButtonTimeFormat;
    var var_sourse_keys = [
        "{RECIPIENTS}",
        "{FULLNAME}",
        "{DATE}",
        "{RANDOM_NUMBER}",
        "{RANDOM_HTML}",
        "{SEX}",
        "{BIRTHDAY}",
        "{PHONE}",
        "{AREA}",
        "{VAR1}",
        "{VAR2}",
        "{VAR3}",
        "{VAR4}",
        "{VAR5}",
        "{VAR6}",
        "{VAR7}",
        "{VAR8}",
        "{VAR9}",
        "{VAR10}",
        "{VAR11}",
        "{VAR12}",
        "{VAR13}",
        "{VAR14}",
        "{VAR15}",
        "{VAR16}",
        "{VAR17}",
        "{VAR18}",
        "{VAR19}",
        "{VAR20}",
        "{VAR21}",
        "{VAR22}",
        "{VAR23}",
        "{VAR24}",
        "{VAR25}",
        "{VAR26}",
        "{VAR27}",
        "{VAR28}",
        "{VAR29}",
        "{VAR30}",
        "{VAR31}",
        "{VAR32}",
        "{VAR33}",
        "{VAR34}",
        "{VAR35}",
        "{VAR36}",
        "{VAR37}",
        "{VAR38}",
        "{VAR39}",
        "{VAR40}",
        "{VAR41}",
        "{VAR42}",
        "{VAR43}",
        "{VAR44}",
        "{VAR45}",
        "{VAR46}",
        "{VAR47}",
        "{VAR48}",
        "{VAR49}",
        "{VAR50}"
    ];
    var sourse_formats = {
        "{RECIPIENTS}": "收件人地址" ,
        "{FULLNAME}": "收件人姓名",
        "{DATE}":  "当前日期",
        "{RANDOM_NUMBER}": "随机10位数字" ,
        "{RANDOM_HTML}": "随机200中文字符（自动隐藏,Gmail无效）" ,
        "{SEX}": "性别" ,
        "{BIRTHDAY}": "生日" ,
        "{PHONE}": "手机" ,
        "{AREA}": "地区" ,

        "{VAR1}" : "变量1",
        "{VAR2}" : "变量2",
        "{VAR3}" : "变量3",
        "{VAR4}" : "变量4",
        "{VAR5}" : "变量5",
        "{VAR6}" : "变量6",
        "{VAR7}" : "变量7",
        "{VAR8}" : "变量8",
        "{VAR9}" : "变量9",
        "{VAR10}" : "变量10",
        "{VAR11}" : "变量11",
        "{VAR12}" : "变量12",
        "{VAR13}" : "变量13",
        "{VAR14}" : "变量14",
        "{VAR15}" : "变量15",
        "{VAR16}" : "变量16",
        "{VAR17}" : "变量17",
        "{VAR18}" : "变量18",
        "{VAR19}" : "变量19",
        "{VAR20}" : "变量20",
        "{VAR21}" : "变量21",
        "{VAR22}" : "变量22",
        "{VAR23}" : "变量23",
        "{VAR24}" : "变量24",
        "{VAR25}" : "变量25",
        "{VAR26}" : "变量26",
        "{VAR27}" : "变量27",
        "{VAR28}" : "变量28",
        "{VAR29}" : "变量29",
        "{VAR30}" : "变量30",
        "{VAR31}" : "变量31",
        "{VAR32}" : "变量32",
        "{VAR33}" : "变量33",
        "{VAR34}" : "变量34",
        "{VAR35}" : "变量35",
        "{VAR36}" : "变量36",
        "{VAR37}" : "变量37",
        "{VAR38}" : "变量38",
        "{VAR39}" : "变量39",
        "{VAR40}" : "变量40",
        "{VAR41}" : "变量41",
        "{VAR42}" : "变量42",
        "{VAR43}" : "变量43",
        "{VAR44}" : "变量44",
        "{VAR45}" : "变量45",
        "{VAR46}" : "变量46",
        "{VAR47}" : "变量47",
        "{VAR48}" : "变量48",
        "{VAR49}" : "变量49",
        "{VAR50}" : "变量50"
    };


    function getVarDesc(key) {
        return sourse_formats[key];
    }

    function insertCommonvar(key) {
        editor.insertContent(key);
    }

    editor.addButton('commonvar', {
        type: 'splitbutton',
        text: '变量',
        title: '变量',
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

    editor.addMenuItem('commonvar', {
        text: '变量',
        menu: var_menuItems,
        context: 'insert'
    });

});