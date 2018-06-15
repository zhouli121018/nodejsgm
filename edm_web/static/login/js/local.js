//网站JS效果&Jquery效果

$(window).ready(function(){


$('li').hover(function(){
		$(this).addClass('hover');
	},function(){
		$(this).removeClass('hover');
	});


if ($(window).width()<1150) {
	$('.online_service').hide();
	$('.side_ad').hide();	
}
	else{
		$('.online_service').show();
		$('.side_ad').show();
	}
;

$(window).resize(function(){

	if ($(window).width()<1150) {
	$('.online_service').hide();
	$('.side_ad').hide();	
}
	else{
		$('.online_service').show();
		$('.side_ad').show();
	}
;
})




});