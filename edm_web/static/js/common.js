/*
 *	JavaScript
 */

function E(name) {return document.getElementById(name);}
function Go(path) {window.location.href = path;}

/* 变量验证函数
 **********************************************************/

/*
 *	检测字符串格式
 *	调用方法：checkStringFormat(string, {type: 'custom', pattern: /^[a-zA-Z0-9_]{3,15}$/})
 */
function checkStringFormat(string, param) {
	var string;
	var pattern;
	var type;

	if(isInvalid(string)) {return false;}
	if(isInvalid(param.type)) {alert("参数错误！");return false;}
	if(!isInvalid(param.length) && (string.length > param.length)) {return false;}

	type = param.type;
	switch(type) {
		case "custom":
			if(isInvalid(param.pattern)) {alert("参数错误！");return false;}
			pattern = param.pattern;
		break;
		case "userid":
			pattern = /^[a-zA-Z0-9_]{3,15}$/;
		break;
		case "alphanum":
			pattern = /^[a-zA-Z0-9_.]*$/;
		break;
		case "mailname":
			pattern = /^\w+([-+.]\w+)*$/;
		break;
		case "number":
			pattern = /^\d+(\.(\d)+)?$/;
		break;
		case "integer":
			pattern = /^[-\+]?\d+$/;
		break;
		case "chinese":
			pattern = /^[\u4e00-\u9fa5_a-zA-Z0-9_.]+$/;
		break;
		case "email":
			pattern = /^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$/;
		break;
		case "domain":
			pattern = /^\w+([-.]\w+)*\.\w+([-.]\w+)*$/;
		break;
		case "url":
			pattern = /^http:\/\/[A-Za-z0-9]+\.[A-Za-z0-9]+[\/=\?%\-&_~`@[\]\':+!]*([^<>\"\"])*$/;
		break;
		case "phones":
			pattern = /^[0-9-]{3,15}$/;
		break;
		case "mobile":
			pattern = /(^[1][3][0-9]{9}$)|(^0[1][3][0-9]{9}$)/;
		break;
		case "phone":
			pattern = /(^([0][1-9]{2,3}[-])?\d{3,8}(-\d{1,6})?$)|(^\([0][1-9]{2,3}\)\d{3,8}(\(\d{1,6}\))?$)|(^\d{3,8}$)/;
		break;
		case "date":
			var re_dt = /^(\d{4})\-(\d{1,2})\-(\d{1,2})$/;
			pattern = function (s_date) {
				if (!re_dt.test(s_date))
					return false;
				if (RegExp.$3 > 31 || RegExp.$2 > 12)
					return false;
				var dt_test = new Date(RegExp.$1, Number(RegExp.$2-1), RegExp.$3);
				if (dt_test.getMonth() != Number(RegExp.$2-1))
					return false;
				return true;
			}
		break;
		case "time":
			var re_tm = /^(\d{1,2})\:(\d{1,2})\:(\d{1,2})$/;
			pattern = function (s_time) {
				if (!re_tm.test(s_time))
					return false;
				if (RegExp.$1 > 23 || RegExp.$2 > 59 || RegExp.$3 > 59)
					return false;
				return true;
			}
		break;
		case "ip":
			var re = /^(\d+)\.(\d+)\.(\d+)\.(\d+)$/;
			pattern = function (s_ip) {
				if (!re.test(s_ip))
					return false;
				if (RegExp.$1>255 || RegExp.$2>255 || RegExp.$3>255 || RegExp.$4>255)
					return false;
				return true;
			}
		break;
		case "mac":
			pattern = /^([0-9A-Fa-f]{2})(-[0-9A-Fa-f]{2}){5}|([0-9A-Fa-f]{2})(:[0-9A-Fa-f]{2}){5}/;
		break;
		case "port":
			var re = /^[-\+]?\d+$/;
			pattern = function(s_port) {
				if (!re.test(s_port))
					return false;
				if (s_port > 65535)
					return false;
				return true;
			}
		break;
	}

	if(typeof(pattern) != "function") {
		if(!pattern.test(string)) 
			return false;
		if(string.search(pattern) == -1) {
			return false;
		}
	} else if(!pattern(string)) {
		return false;
	}

	return true;
}

/*
 *	检测指定的值是否为无效或空值
 */
function isInvalid(v) {
	if(v == undefined || v == '') return true;
	else return false;
}

/*
 *	检测指定的值是否为空
 */
function isEmpty(v) {
	if(v == '') return true;
	else return false;
}


/* 编辑器用函数
 **********************************************************/

function getEditorHTMLContents(EditorName) {
	var oEditor = FCKeditorAPI.GetInstance(EditorName);
	return(oEditor.GetXHTML(true));
}


function setEditorContents(EditorName, ContentStr) {
	var oEditor = FCKeditorAPI.GetInstance(EditorName);
	oEditor.SetHTML(ContentStr);
}


/* 基础函数
 **********************************************************/

//css.js
function get_css(rule_name,stylesheet,delete_flag) {if(!document.styleSheets)return false;rule_name=rule_name.toLowerCase();stylesheet=stylesheet||0;for(var i=stylesheet;i<document.styleSheets.length;i++){var styleSheet=document.styleSheets[i];css_rules=document.styleSheets[i].cssRules||document.styleSheets[i].rules;if(!css_rules)continue;var j=0;do{if(css_rules.length&&j>css_rules.length+5)return false;if(css_rules[j].selectorText&&css_rules[j].selectorText.toLowerCase()==rule_name){if(delete_flag==true){if(document.styleSheets[i].removeRule)document.styleSheets[i].removeRule(j);if(document.styleSheets[i].deleteRule)document.styleSheets[i].deleteRule(j);return true}else return css_rules[j]}}while(css_rules[++j])}return false}
function add_css(rule_name,stylesheet) {rule_name=rule_name.toLowerCase();stylesheet=stylesheet||0;if(!document.styleSheets||get_css(rule_name,stylesheet))return false;(document.styleSheets[stylesheet].insertRule)?document.styleSheets[stylesheet].insertRule(rule_name+' { }',0):document.styleSheets[stylesheet].addRule(rule_name,null,0);return get_css(rule_name,stylesheet)}
function get_sheet_num(href_name) {if(!document.styleSheets)return false;for(var i=0;i<document.styleSheets.length;i++){if(document.styleSheets[i].href&&document.styleSheets[i].href.toString().match(href_name))return i}return false}
function remove_css(rule_name,stylesheet) {return get_css(rule_name,stylesheet,true)}
function add_sheet(url,media) {if(document.createStyleSheet){document.createStyleSheet(url)}else{var newSS=document.createElement('link');newSS.rel='stylesheet';newSS.type='text/css';newSS.media=media||"all";newSS.href=url;document.getElementsByTagName("head")[0].appendChild(newSS)}}

//出处:网上搜集
//made by yaosansi 2005-12-02
//For more visit http://www.yaosansi.com
// Trim() , Ltrim() , RTrim()
String.prototype.trim = function() {
	return this.replace(/(^\s*)|(\s*$)/g, "");
}
String.prototype.ltrim = function() {
	return this.replace(/(^\s*)/g, "");
}
String.prototype.rtrim = function() {
	return this.replace(/(\s*$)/g, "");
}

/*
 *	删除数组中指定位置的元素
 *	@param		array	array
 *	@param		int		dx
 *	@return		Array
 */
function removeArray(array, dx) {
	if(isNaN(dx)||dx>array.length){return false;}
	array.splice(dx,1);
}

/*
 *	删除数组中指定的元素
 */
function removeArrayItem(array, item) {
	for(var i=0; i<array.length; i++) {
		if(array[i] == item) {
			array.splice(i, 1);
			break;
		}
	}
}

//选择多个复选框
function selectCheckboxAll(form_name, prefix, checkall) {
	var form = E(form_name);
	var checkall = checkall ? checkall : 'chkall';
	for(var i = 0; i < form.elements.length; i++) {
		var e = form.elements[i];
		if(e.name && e.name != checkall && (!prefix || (prefix && e.name.match(prefix)))) {
			e.checked = form.elements[checkall].checked;
		}
	}
}

//取得指定复选框的值
function getCheckboxValue(form_name, prefix) {
	var form = E(form_name);
	var data_list = [];
	for(var i = 0; i < form.elements.length; i++) {
		var e = form.elements[i];
		if(e.name && e.name.match(prefix) && e.checked) {
			data_list.push(e.value);
		}
	}
	return data_list;
}

//查询数据组是否存在指定项目
function findArrayItem(array, item) {
	for(var i=0; i<array.length; i++) {
		if(array[i] == item) return true;
	}
	return false;
}

//从 FILE 类型的 INPUT 表单中取得文件名称
function getInputFileName(string) {
	var string;

	if(string.indexOf('\\') || string.indexOf('/')) {
		if(string.indexOf('\\')) {
			var split_char = '\\';
		} else {
			var split_char = '/';
		}
		var array = string.split(split_char);
		string = array[array.length - 1];
	}

	return string;
}


//检测是否存在指定名称的函数
function checkFunction(funcName) {
	try {
		if(typeof(eval(funcName)) == "function") {
			return true;
		} else {
			return false;
		}
	} catch(e) {
		return false;
	}
}

//密码强度检测
function evaluatePassword(word) {
	if (word == "") {
		return 0;
	} else if (word.length < 6) {
		return 1;
	} else {
		return word.match(/[a-z](?![^a-z]*[a-z])|[A-Z](?![^A-Z]*[A-Z])|\d(?![^\d]*\d)|[^a-zA-Z\d](?![a-zA-Z\d]*[^a-zA-Z\d])/g).length;
	}
}

//只能输入浮点数
function test_float(obj){
	var value = obj.value;
	if(/[^0123456789.]/g.test(value))
	obj.value=value.replace(/[^0123456789.]/g,'');	
}
//只能输入整数
function test_int(obj){
	var value = obj.value;
	if(/[^0123456789]/g.test(value))
	obj.value=value.replace(/[^0123456789]/g,'');	
}



// 语言包选择 add by lbh 20120813
function changeLang(obj) {
	var url = window.location.href;
	if(url.toLowerCase().indexOf('&lang=') != -1) {
		url = url.toLowerCase().replace(/lang=[^&]*/g,"lang="+obj.value);
	}else{
		url += "&lang=" + obj.value;
	}

	window.location.href = url;
}


// 加载页面 -- add by lbh 20130201
function loadPage(url,target) {
	if(target == 'blank') {
		window.open('index.php?module=clientsys&action=ajax&do=load-page&url='+encodeURIComponent(url));
	
	}else{
		Go('index.php?module=clientsys&action=load-page&url='+encodeURIComponent(url));
	}
}
