
$(document).ready(function () {

  // Start //

  $("#sidebar-menu .sub-menu > a").click(function(e) {
    $("#sidebar-menu ul ul").slideUp(), $(this).next().is(":visible") || $(this).next().slideDown(),
    e.stopPropagation()
  })

  /*------------------------------------------------------------------------------*/
    /*  Fixed-header
    /*------------------------------------------------------------------------------*/
    $(window).scroll(function(){
      if ( matchMedia( 'only screen and (min-width: 992px)' ).matches ) 
      {
          if ($(window).scrollTop() >= 80 ) {

              $('.header').addClass('sticky-header');
          }
          else {

              $('.header').removeClass('sticky-header');
          }
      }
  });
  
    // Mobile search //
    $(".mobile-search").click(function () {
      $(".searchbar").toggleClass("open");
    });

    // owlCarousel //
    $('.banner-slider').owlCarousel({
      autoplay:false,
      loop:true,
      dots:true,
      nav:false,
      autoplaySpeed:2000,
      smartSpeed:1500,
      margin:10,
      responsiveClass:true,
      responsive:{
          0:{
              items:1,
              
          },
          460:{
              items:1,
              
          },
          767:{
              items:1,
          },
          991:{
              items:1,
          }
      }
  })


  // End //
});


/*------------------------------------------------------------------------------*/
    /* Sidebar
    /*------------------------------------------------------------------------------*/

    const body = document.querySelector("body"),
    sidber = body.querySelector(".sidebar"),
    toggle = body.querySelector(".minimize_toggle");
    toggle.addEventListener("click", () =>{
      sidber.classList.toggle("close");
    });

    
    



   

   
  