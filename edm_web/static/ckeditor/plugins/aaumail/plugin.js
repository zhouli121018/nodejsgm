/*
 下拉选择
 */

CKEDITOR.plugins.add('aaumail', {
        requires: 'richcombo',

        init: function (editor) {
            var config = editor.config,
                lang = editor.lang.format;

            //下拉数据源
            var tags = config.customerUmailLinks.data;
            var title = config.customerUmailLinks.title;

            //添加下拉框
            editor.ui.addRichCombo( 'aaumail', {
                label :title,
                title : title,
                className : 'cke_format',
                toolbar: 'styles,' + 40,
                panel :
                {
                    css: [ CKEDITOR.skin.getPath( 'editor' ) ].concat( config.contentsCss ),
                    multiSelect : false,
                    attributes : { 'aria-label' : lang.panelTitle }
                },
                init : function() {
                    this.startGroup( title );
                    for (var this_tag in tags){
                        //function add( 值, html,文本 )
                        this.add( tags[this_tag][0], tags[this_tag][1], tags[this_tag][2] );
                    }
                },
                onClick : function( value )
                {
                    editor.focus();
                    editor.fire( 'saveSnapshot' );
                    // alert(value);
                    // 插入头部
                    var avalue = value + editor.getData()
                    editor.setData(avalue);
                    // editor.insertHtml(value + editor.getData());
                    editor.fire( 'saveSnapshot' );
                },
                onRender: function() {
                    editor.on( 'selectionChange', function( ev ) {
                        var currentValue = this.getValue();
                        var elementPath = ev.data.path,elements = elementPath.elements;
                        /*
                        for ( var i = 0, element; i < elements.length; i++ ) {
                            element = elements[ i ];
                            for ( var value in styles ) {
                                if ( styles[ value ].checkElementMatch( element, true, editor ) ) {
                                    if ( value != currentValue )
                                        this.setValue( value );
                                    return;
                                }
                            }
                        }
                        */
                        this.setValue( '', title );
                    }, this );
                },
                /*refresh: function() {
                 if ( !editor.activeFilter.check( style ) )
                 this.setState( CKEDITOR.TRISTATE_DISABLED );
                 }*/
            });

        }
    }
)
