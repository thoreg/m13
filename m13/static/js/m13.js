function openNav() {
  document.getElementById("m13-sidebar").style.width = "250px";
  document.getElementById("main").style.marginLeft = "250px";
}

function closeNav() {
  document.getElementById("m13-sidebar").style.width = "0";
  document.getElementById("main").style.marginLeft= "0";
}

$('.category').click(function(){
  if ($(this).hasClass('is-closed')) {
    $(this).removeClass('is-closed');
  }else{
    $(this).addClass('is-closed');
  }
});
