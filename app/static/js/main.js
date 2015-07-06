$(function() {



	if(isMobile()){

		$(".showMobile").show();
		$(".showDesktop").hide();
	} else {

		$(".showMobile").hide();
		$(".showDesktop").show();
	}
});

function showSection(page){
	if(isMobile()){
		location.href= 'privacy/' + page;
	} else {
		$("#iframe").attr('src', 'privacy/' + page);
	}

}


function isMobile(){
	var windowSize = window.parent.screenSize;
	if (typeof windowSize === "undefined") {
		windowSize = $(window).width();
	}
	if(windowSize <=767){
		return true;
	} else {
		return false;
	}
}

function closeContact(){
$(".contactOptions").hide();
}

function showContact(){
$(".contactOptions").show();

}

function showItemDetails(id){
	if($("#arrow-"+id).attr("src")=="img/arrow-up.png"){
		$("#arrow-"+id).attr("src","img/arrow-down.png");
		$("#details-"+id).slideDown();
	} else {
		$("#arrow-"+id).attr("src","img/arrow-up.png");
		$("#details-"+id).slideUp();
	}
}