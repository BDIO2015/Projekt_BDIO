
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
});