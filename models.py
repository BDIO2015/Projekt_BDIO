#-*- coding: utf-8 -*-
from django.db import models

# Create your models here.

class Schedule(models.Model):
	id = models.AutoField(primary_key=True)
	description = models.TextField()
	day = models.CharField(max_length=7)
	time_start = models.CharField(max_length=14)
	time_end = models.CharField(max_length=14)
	
class User_Type(models.Model):
	id = models.AutoField(primary_key=True)
	type_name = models.CharField(max_length=15)
	canCreate = models.BooleanField(default=False)
	canEdit = models.BooleanField(default=False)
	canDelete = models.BooleanField(default=False)
	canDeliver = models.BooleanField(default=False)
	canManage = models.BooleanField(default=False)

class User(models.Model):
	user_id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=30)
	second_name = models.CharField(max_length=30)
	address = models.CharField(max_length=60)
	city = models.CharField(max_length=30)
	postal_code = models.CharField(max_length=5)
	phone_number = models.CharField(max_length=15)
	password = models.CharField(max_length=512)
	username = models.CharField(max_length=64)
	scheduled = models.ForeignKey(Schedule, null=True, on_delete=models.SET_NULL)
	type = models.ForeignKey(User_Type, null=True, on_delete=models.SET_NULL)
	
class Delivery(models.Model):
	delivery_id = models.AutoField(primary_key=True)
	ord = models.IntegerField()
	user = models.ForeignKey(User)

class Payment_Type(models.Model):
	id = models.AutoField(primary_key=True)
	payment_name = models.CharField(max_length=30)

class Order(models.Model):
	ORDER_STATUS = (
			('0', 'Anulowane'),
			('1', 'Przyjete'),
			('2', 'Przygotowywane'),
			('3', 'Oczekujace'),
			('4', 'Dowoz'),
			('5', 'Zrealizowane'),
			('6', 'Transfer'),
		)
	order_code = models.AutoField(primary_key=True)
	status = models.CharField(max_length=1, choices=ORDER_STATUS)
	time_stamp = models.DateTimeField(auto_now_add=True)
	order_notes = models.TextField(blank=True)
	order_address = models.CharField(blank=True, max_length=60)
	price = models.DecimalField(max_digits=5, decimal_places=2)
	payment_name = models.CharField(max_length=30)
	payment_status = models.BooleanField(default=0)
	payment_time_stamp = models.DateTimeField(auto_now_add=True)
	delivery = models.ForeignKey(Delivery, null=True, on_delete=models.SET_NULL)
	user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
	payment_type = models.ForeignKey(Payment_Type)
	access_hash = models.CharField(max_length=512, blank=True)

class Discount(models.Model):
	id = models.AutoField(primary_key=True)
	type = models.CharField(max_length=30)
	value = models.IntegerField()

class Product(models.Model):
	product_code = models.AutoField(primary_key=True)
	product_name = models.CharField(max_length=30)
	price = models.DecimalField(max_digits=5, decimal_places=2)
	description = models.TextField()
	discount = models.ForeignKey(Discount, null=True, on_delete=models.SET_NULL)
	category = models.ForeignKey("Product_Category")

class Ingredient(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=30)
	price = models.DecimalField(max_digits=5, decimal_places=2)
	quantity = models.DecimalField(max_digits=5, decimal_places=2)
	default_quantity  = models.DecimalField(max_digits=5, decimal_places=2)
	units = models.CharField(max_length=5)
	min_quantity = models.DecimalField(max_digits=5, decimal_places=2)
	
class Order_Product(models.Model):
	quantity = models.IntegerField()
	remarks = models.TextField()
	order = models.ForeignKey(Order)
	product = models.ForeignKey(Product)
	
class Product_Category(models.Model):
	cat_id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=30)
	description = models.TextField()
	additional_price = models.DecimalField(max_digits=5, decimal_places=2)
	parent = models.ForeignKey("self", null=True)
	TYPE_STATUS= (
			('1', 'Kategoria'),
			('2', 'Nagłówek podkategorii'),
			('3', 'Podkategoria'),
		)
	type = models.CharField(max_length=1, choices=TYPE_STATUS)
	DEMAND_STATUS=(
			(0, 'NIE'),
			(1, 'TAK'),
		)
	demand_ingredients = models.IntegerField(choices=DEMAND_STATUS)

class Order_Product_Categories(models.Model):
	id = models.AutoField(primary_key=True)
	order_product_id = models.ForeignKey(Order_Product)
	category_id = models.ForeignKey(Product_Category)
	
class Ingredient_Product(models.Model):
	quantity = models.FloatField()
	ingredient = models.ForeignKey(Ingredient)
	product = models.ForeignKey(Product)
	
class Order_Ingredients(models.Model):
	product_order = models.ForeignKey(Order_Product)
	ingredient = models.ForeignKey(Ingredient)