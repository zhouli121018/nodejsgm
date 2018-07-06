CKEDITOR.plugins.add('aashare', {


        init: function (editor) {
            var config = editor.config,
                lang = editor.lang.format;

            var data = config.customerShareLink.data;
            var title = config.customerShareLink.title;

            //创建一个按钮, editor代表ckeditor编辑框实例
            editor.ui.addButton('aashare', {
                lable: 'FButton',
                title: title,
                icon: this.path + "share.ico", //这个g.ico是你的插件图标，放在同目录下
                command: 'mycommand'  //通过命令的方式连接
            });
            //插件的逻辑主体写在命令里面, 并给他起个响亮的名字
            editor.addCommand('mycommand', {
                exec: function () {
                    editor.insertHtml(data);
                }
            });
        }
        /*,

         init: function (editor) {
         var config = editor.config,
         lang = editor.lang.format;

         var data = config.customerShareLink.data;
         var title = config.customerShareLink.title;

         //创建一个按钮, editor代表ckeditor编辑框实例
         editor.ui.addButton('aashare', {
         lable: 'FButton',
         title: title,

         onClick: function (value) {
         editor.focus();
         editor.fire('saveSnapshot');
         // alert(value);
         editor.insertHtml(data);
         editor.fire('saveSnapshot');
         },
         });
         }
         */
    }

)