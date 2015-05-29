
//po zaladowaniu glownego dokumentu
jQuery(document).ready(function(){

/* pokaż ukryj wybieranie składników */
	if(jQuery("#product_categories option:selected").attr("data-ingredients-demand") == 1){
		jQuery("#ingredients_for_product").show();
		jQuery("p#cost").show();
	}
	else{
		jQuery("#ingredients_for_product").hide();
		jQuery("p#cost").hide();
	}
	jQuery("#product_categories").change(function(){
		if(jQuery("#product_categories option:selected").attr("data-ingredients-demand") == 1){
			jQuery("#ingredients_for_product").show();
			jQuery("p#cost").show();
		}
		else{
			jQuery("#ingredients_for_product").hide();
			jQuery("p#cost").hide();
		}
	});

	function calculate_cost(){
	var cost = 0;
	jQuery("#ingredients_for_product input").each(function(){
		cost += jQuery(this).val() * jQuery(this).attr("data-price");
		
	});
	jQuery("p#cost span#ingredients_cost").text(parseFloat(cost).toFixed(2));
	}
	
	calculate_cost();
	
	jQuery("#ingredients_for_product input").change(function(){
		calculate_cost();
	});
	
	//klikniete "informacje" na produkcie
	
	function get_number_of_elements_in_row()
	{
		var win_width = jQuery(window).width();
		if(win_width < 768)
			return 1;
		else if(win_width >= 768 && win_width < 992)
			return 2;
		else if(win_width >= 992 && win_width < 1200)
			return 3;
		else
			return 4;
	}
	
	function make_space(){
		// usun puste divy
		jQuery(".product_row").children().each(function(){
			if(jQuery(this).hasClass("empty-div"))
				jQuery(this).remove();
		});
		var elements = get_number_of_elements_in_row();
		//dodaj nowe
		var i = 0;
		if(elements != 1)
		{
			jQuery(".product_row").each(function(){
				jQuery(this).children().each(function(){
					var prod_box = parseInt(jQuery(this).attr("id")) + 1;
					if(prod_box % elements == 0)
						jQuery(this).after('<div class="col-xs-12 empty-div"></div>');
				});
			});
		}
	}
	make_space();
	jQuery(window).resize(function(){
		make_space();
	});
	
	jQuery(".category_title").click(function(){
		if(jQuery(this).attr("aria-expanded") == "false")
			jQuery(this).find(".expand_icon").addClass("glyphicon-minus").removeClass("glyphicon-plus");
		else
			jQuery(this).find(".expand_icon").addClass("glyphicon-plus").removeClass("glyphicon-minus");
	});

	jQuery(".delete-button").click(function(){
		return confirm("Czy na pewno chcesz usunąć ten element?");
	});
	
	jQuery(".change-order-status-button").click(function(){
		return confirm("Czy na pewno chcesz zmienić status zamówienia?");
	});
	
	jQuery(".cancel-order-button").click(function(){
		return confirm("Czy na pewno chcesz anulować zamówienie?");
	});
	
		
// set active menu button
	var l = window.location;
		jQuery("ul.menu li").each(function(){
			var str = l.toString();
			console.log(l.origin + '/' + jQuery(this).find("a").attr("href").substr(1))
			if(l == l.origin + '/' + jQuery(this).find("a").attr("href").substr(1))
			{
				jQuery(this).addClass("active");
			}
			else
			{
				if(str.substr(0,str.length-1) == l.origin + '/' + jQuery(this).find("a").attr("href").substr(1))
					jQuery(this).addClass("active");
			}
		});
});