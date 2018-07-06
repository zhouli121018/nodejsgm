/**
 * @license Copyright (c) 2003-2017, CKSource - Frederico Knabben. All rights reserved.
 * For licensing, see LICENSE.md or http://ckeditor.com/license
 */

/*
 http://www.cnblogs.com/pengyunjing/p/6241065.html
 http://www.chhua.com/web-note827
 http://www.cnblogs.com/ywjy/p/5036056.html
 */

CKEDITOR.editorConfig = function( config ) {
    // Define changes to default configuration here. For example:
    // config.language = 'fr';
    // config.uiColor = '#AADC6E';

    // 界面语言，默认为 'en'
    config.language = 'zh-cn';

    // 取消 “拖拽以改变尺寸”功能  //是否允许改变大小 plugins/resize/plugin.js
    config.resize_enabled = false;

    // 当提交包含有此编辑器的表单时，是否自动更新元素内的数据
    // config.autoUpdateElement = false;
    config.autoUpdateElement = true;

    // 编辑器的z-index值
    config.baseFloatZIndex = 10000;

    //设置前景色的取值 plugins/colorbutton/plugin.js  背景色
    //config.colorButton_colors = '000,800000,8B4513,2F4F4F,008080,000080,4B0082,696969,B22222,A52A2A,DAA520,006400,40E0D0,0000CD,800080,808080,F00,FF8C00,FFD700,008000,0FF,00F,EE82EE,A9A9A9,FFA07A,FFA500,FFFF00,00FF00,AFEEEE,ADD8E6,DDA0DD,D3D3D3,FFF0F5,FAEBD7,FFFFE0,F0FFF0,F0FFFF,F0F8FF,E6E6FA,FFF';
    //是否在选择颜色时显示“其它颜色”选项 plugins/colorbutton/plugin.js
    // config.colorButton_enableMore = false;
    /*
     //设置编辑内元素的背景色的取值 plugins/colorbutton/plugin.js.
     config.colorButton_backStyle = {
     element : 'span',
     styles : { 'background-color' : '#(color)' }
     };
     //区块的前景色默认值设置 plugins/colorbutton/plugin.js
     config.colorButton_foreStyle = {
     element : 'span',
     styles : { 'color' : '#(color)' }
     };
     */

    //界面编辑框的背景色 plugins/dialog/plugin.js
    config.dialog_backgroundCoverColor = 'rgb(255, 254, 253)'; //可设置参考
    // config.dialog_backgroundCoverColor = 'white' //默认

    //背景的不透明度 数值应该在：0.0～1.0 之间 plugins/dialog/plugin.js
    // config.dialog_backgroundCoverOpacity = 0.8;

    //进行表格编辑功能 如：添加行或列 目前仅firefox支持 plugins/wysiwygarea/plugin.js
    // config.disableNativeTableHandles = true; //默认为不开启

    //移动或者改变元素时 边框的吸附距离 单位：像素 plugins/dialog/plugin.js
    //config.dialog_magnetDistance = 20;

    //是否拒绝本地拼写检查和提示 默认为拒绝 目前仅firefox和safari支持 plugins/wysiwygarea/plugin.js.
    // config.disableNativeSpellChecker = true;
    config.disableNativeSpellChecker = false;

    //是否开启 图片和表格 的改变大小的功能 config.disableObjectResizing = true;
    //config.disableObjectResizing = false //默认为开启

    // 是否强制复制来的内容去除格式 plugins/pastetext/plugin.js
    config.forcePasteAsPlainText = false; //不去除

    //是否强制用“&”来代替“&amp;”plugins/htmldataprocessor/plugin.js
    // config.forceSimpleAmpersand = false;

    //当从word里复制文字进来时，是否进行文字的格式化去除 plugins/pastefromword/plugin.js
    // config.pasteFromWordIgnoreFontFace = true; //默认为忽略格式
    config.pasteFromWordRemoveFontStyles = false; //Word复制保留文字样式  //不去除样式
    //是否使用<h1><h2>等标签修饰或者代替从word文档中粘贴过来的内容 plugins/pastefromword/plugin.js
    // config.pasteFromWordKeepsStructure = false;
    //从word中粘贴内容时是否移除格式 plugins/pastefromword/plugin.js
    config.pasteFromWordRemoveStyle = false; //Word复制保留所有样式  //不去除样式


    //是否忽略段落中的空字符 若不忽略 则字符将以“”表示 plugins/wysiwygarea/plugin.js
    config.ignoreEmptyParagraph = true;

    // //编辑器中回车产生的标签
    //可选：CKEDITOR.ENTER_BR或CKEDITOR.ENTER_DIV
    //config.enterMode = CKEDITOR.ENTER_BR;
    config.enterMode = CKEDITOR.ENTER_BR;
    //config.enterMode =CKEDITOR.ENTER_P; //可选：CKEDITOR.ENTER_BR或CKEDITOR.ENTER_DIV
    config.shiftEnterMode = CKEDITOR.ENTER_P;
    config.allowedContent=true;

    //页面载入时，编辑框是否立即获得焦点 plugins/editingblock/plugin.js plugins/editingblock/plugin.js.
    config.startupFocus = false;

    //当执行“新建”命令时，编辑器中的内容plugins/newpage/plugin.js
    //config.newpage_html = '';

    //一组用逗号分隔的标签名称，显示在左下角的层次嵌套中 plugins/menu/plugin.js.
    // config.menu_groups ='clipboard,form,tablecell,tablecellproperties,tablerow,tablecolumn,table,anchor,link,image,flash,checkbox,radio,textfield,hiddenfield,imagebutton,button,select,textarea';

    //在清除图片属性框中的链接属性时 是否同时清除两边的<a>标签 plugins/image/plugin.js
    //config.image_removeLinkByEmptyURL = true

    //是否使用完整的html编辑模式 如使用，其源码将包含：<html><body></body></html>等标签
    // 用于是否留头
    config.fullPage = false;

    config.toolbar = 'Full';
    // config.toolbar = 'Basic';
    //config.toolbar = 'Cms';

    //自定义工具栏 ,大家可以根据需要进行删减
    config.toolbar_Full = [
        ['Source', 'Preview', 'Templates'],
        // ['Source','-','Save','NewPage','Preview','-','Templates'],
        ['Cut','Copy','Paste','PasteText','PasteFromWord','-','Print', 'SpellChecker', 'Scayt'],
        ['Undo','Redo','-','Find','Replace','-','SelectAll','RemoveFormat'],
        ['Form', 'Checkbox', 'Radio', 'TextField', 'Textarea', 'Select', 'Button', 'ImageButton', 'HiddenField'],
        '/',
        ['Bold','Italic','Underline','Strike','-','Subscript','Superscript'],
        ['NumberedList','BulletedList','-','Outdent','Indent','Blockquote'],
        ['JustifyLeft','JustifyCenter','JustifyRight','JustifyBlock', '-', "lineheight"],
        '/',
        ['Link','Unlink','Anchor'],
        ['Image','Flash','Table','HorizontalRule','Smiley','SpecialChar','PageBreak'],
        '/',
        ['Styles','Format','Font','FontSize'],
        ['TextColor','BGColor'],
        ['aaumail',  'aavar', 'aacommon', 'aashare','-', 'Maximize', 'ShowBlocks',]
    ];

    config.extraPlugins = 'lineheight,aaumail,aavar,aacommon,aashare';
    // 配置字体
    //config.font_names='楷体/楷体_GB2312;宋体/宋体;黑体/黑体;仿宋/仿宋_GB2312;隶书/隶书;幼圆/幼圆;微软雅黑/微软雅黑;'+ config.font_names;
    config.font_names='楷体/KaiTi;宋体/SimSun;新宋体/NSimSun;隶书/LiSu;华文楷体/STKaiti;华文中宋/STZhongsong;华文行楷/STXingkai;仿宋_GB2312/FangSong_GB2312;楷体_GB2312/KaiTi_GB2312;黑体/SimHei;' +
        '微软雅黑/Microsoft YaHei;Arial/Arial, Helvetica, sans-serif;Arial Black/Arial Black, Arial Black, Gadget, sans-serif;Calibri/Calibri;Cambria/Cambria;' +
        'Comic Sans/Comic Sans MS, Comic Sans MS5, cursive;Courier/Courier New, Courier New, monospace;Courier New/Courier New;Georgia/Georgia, serif;Impact/Impact, sans-serif' +
        'Lucida Console/Lucida Console, Monaco, monospace;Lucida Sans Unicode/Lucida Sans Unicode, Lucida Grande, sans-serif;MS PGothic/MS PGothic;Tahoma/Tahoma' +
        'Times New Roman/Times New Roman, Times, serif;Verdana/Verdana, Geneva, sans-serif;';

    //默认的字体名 plugins/font/plugin.js
    config.font_defaultLabel = 'KaiTi';
    //字体默认大小 plugins/font/plugin.js
    config.fontSize_defaultLabel = '14px';

    //工具栏是否可以被收缩
    config.toolbarCanCollapse = true;
    //工具栏的位置
    config.toolbarLocation = 'top';//可选：bottom

    //工具栏默认是否展开
    config.toolbarStartupExpanded = true;

    //字体编辑时可选的字体大小 plugins/font/plugin.js
    config.fontSize_sizes ='8px/8px;9px/9px;10px/10px;11px/11px;12px/12px;14px/14px;16px/16px;18px/18px;20px/20px;22px/22px;24px/24px;26px/26px;28px/28px;36px/36px;48px/48px;72px/72px'
    //config.fontSize_sizes = '8/8px;9/9px;10/10px;11/11px;12/12px;14/14px;16/16px;18/18px;20/20px;22/22px;24/24px;'
    //
    // KaiTi=楷体|SimSun=宋体|NSimSun=新宋体|LiSu=隶书|STKaiti=华文楷体|STZhongsong=华文中宋|STXingkai=华文行楷|
    // FangSong_GB2312=仿宋_GB2312|KaiTi_GB2312=楷体_GB2312|SimHei=黑体
    // |Microsoft YaHei=微软雅黑|Arial, Helvetica, sans-serif=Arial|Arial Black, Arial Black, Gadget, sans-serif=Arial Black|Calibri=Calibri|

    // Cambria=Cambria|Comic Sans MS, Comic Sans MS5, cursive=Comic Sans|Courier New, Courier New, monospace=Courier|Courier New=Courier New|
    // Georgia, serif=Georgia|Impact, sans-serif=Impact|Lucida Console, Monaco, monospace=Lucida Console|Lucida Sans Unicode, Lucida Grande, sans-serif=Lucida Sans Unicode|
    // Tahoma=Tahoma|Times New Roman, Times, serif=Times New Roman|Verdana, Geneva, sans-serif=Verdana}


    // 去除图片预览的文字
    // 可以打开ckeditor/plugins/image/dialogs/image.js文件，搜索“d.config.image_previewText”就能找到这段鸟语了，
    // (d.config.image_previewText||'')单引号中的内容全删了，注意别删多了。 或者以下配置
    // Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Maecenas feugiat consequat diam. Maecenas metus. Vivamus diam purus, cursus a, commodo non, facilisis vitae, nulla. Aenean dictum lacinia tortor. Nunc iaculis, nibh non iaculis aliquam, orci felis euismod neque, sed ornare massa mauris sed velit. Nulla pretium mi et risus. Fusce mi pede, tempor id, cursus ac, ullamcorper nec, enim. Sed tortor. Curabitur molestie. Duis velit augue, condimentum at, ultrices a, luctus ut, orci. Donec pellentesque egestas eros. Integer cursus, augue in cursus faucibus, eros pede bibendum sem, in tempus tellus justo quis ligula. Etiam eget tortor. Vestibulum rutrum, est ut placerat elementum, lectus nisl aliquam velit, tempor aliquam eros nunc nonummy metus. In eros metus, gravida a, gravida sed, lobortis id, turpis. Ut ultrices, ipsum at venenatis fringilla, sem nulla lacinia tellus, eget aliquet turpis mauris non enim. Nam turpis. Suspendisse lacinia. Curabitur ac tortor ut ipsum egestas elementum. Nunc imperdiet gravida mauris.
    //config.image_previewText = "";

    /*
     //示例2：工具栏为自定义类型
     CKEDITOR.replace( 'editor1',
     {
     toolbar :
     [
     //加粗     斜体，     下划线      穿过线      下标字        上标字
     ['Bold','Italic','Underline','Strike','Subscript','Superscript'],
     //数字列表          实体列表            减小缩进    增大缩进
     ['NumberedList','BulletedList','-','Outdent','Indent'],
     //左对齐             居中对齐          右对齐          两端对齐
     ['JustifyLeft','JustifyCenter','JustifyRight','JustifyBlock'],
     //超链接 取消超链接 锚点
     ['Link','Unlink','Anchor'],
     //图片    flash    表格       水平线            表情       特殊字符        分页符
     ['Image','Flash','Table','HorizontalRule','Smiley','SpecialChar','PageBreak'],
     '/',
     //样式       格式      字体    字体大小
     ['Styles','Format','Font','FontSize'],
     //文本颜色     背景颜色
     ['TextColor','BGColor'],
     //全屏           显示区块
     ['Maximize', 'ShowBlocks','-']
     ]
     }
     );
     */


};
