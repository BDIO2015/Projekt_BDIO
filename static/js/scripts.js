
//po zaladowaniu glownego dokumentu
jQuery(document).ready(function(){

/* pokaż ukryj wybieranie składników */
	if(jQuery("#product_categories option:selected").attr("data-ingredients-demand") == 1)
		jQuery("#ingredients_for_product").show();
	else
		jQuery("#ingredients_for_product").hide();
		
	jQuery("#product_categories").change(function(){
		if(jQuery("#product_categories option:selected").attr("data-ingredients-demand") == 1)
			jQuery("#ingredients_for_product").show();
		else
			jQuery("#ingredients_for_product").hide();
	});
});