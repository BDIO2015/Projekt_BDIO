#-*- coding: utf-8 -*-
from django.shortcuts import render
import re, hashlib
# Create your views here.
from django.http import HttpResponse
from .models import *
from decimal import *
import time
import os

def user_logout(request):
	contents = {'title':'Błąd!', 'messageType':'danger', 'message':'Nieoczekiwany błąd!'}
	if('login_check' in request.session):
		del request.session['login_check']
		contents = {'title':'Wylogowano', 'messageType':'success', 'message':'Wylogowano poprawnie!'}
	return render(request, 'index.html', contents)

def user_check(request):
	users = User.objects.all()
	if(users.empty()):
		contents = {'title':'Błąd!', 'messageType':'danger', 'message':'Nieoczekiwany błąd!'}
	if not('login_check' in request.session):
		contents = {'title':'Zaloguj się!', 'messageType':'danger', 'message':'Musisz się zalogować!'}
		return contents
	else:
		for l_user in users:
			if(l_user.user_id==int(request.session['login_check']) and l_user.type_id==None):
				return {'user_id':l_user.user_id, 'canCreate':0, 'canEdit':0, 'canDelete':0, 'canDeliver':0, 'canManage':0} 
			elif(l_user.user_id==int(request.session['login_check'])):
				return {'user_id':int(l_user.user_id), 'canCreate':int(User_Type.objects.get(id=l_user.type_id).canCreate), 'canEdit':int(User_Type.objects.get(id=l_user.type_id).canEdit), 'canDelete':int(User_Type.objects.get(id=l_user.type_id).canDelete), 'canDeliver':int(User_Type.objects.get(id=l_user.type_id).canDeliver), 'canManage':int(User_Type.objects.get(id=l_user.type_id).canManage) }
			else:
				contents = {'title':'Zaloguj się!', 'messageType':'danger', 'message':'Mushisz się zalogować!'}
		return contents

def index(request):
	contents = {'title':'Testujemy', 'question':'test'}
	return render(request, 'index.html', contents)
	
def manage(request):
	contents = {'title':'Testujemy2', 'question':'test2'}
	return render(request, 'manage.html', contents)

def display_discount():
	discounts = Discount.objects.all()
	contents = {'title':'Zniżki', 'content':''}
	if(discounts.count() > 0):
		toDisp = []
		for curRow in discounts:
			formatType = curRow.type
			active = formatType[0]
			active = int(active)
			if(active == 1):
				active = 'Tak'
			else:
				active = 'Nie'
			days = formatType[1:4]
			days = int(days)
			isDay=[0,0,0,0,0,0,0]
			isDay[0] = days&0x1
			isDay[1] = (days>>1)&0x1
			isDay[2] = (days>>2)&0x1
			isDay[3] = (days>>3)&0x1
			isDay[4] = (days>>4)&0x1
			isDay[5] = (days>>5)&0x1
			isDay[6] = (days>>6)&0x1
			dayString = ''
			if(isDay[0] != 0):
				if(dayString != ''):
					dayString += ', '
				dayString += 'Poniedziałek'
			if(isDay[1] != 0):
				if(dayString != ''):
					dayString += ', '
				dayString += 'Wtorek'
			if(isDay[2] != 0):
				if(dayString != ''):
					dayString += ', '
				dayString += 'Środa'
			if(isDay[3] != 0):
				if(dayString != ''):
					dayString += ', '
				dayString += 'Czwartek'
			if(isDay[4] != 0):
				if(dayString != ''):
					dayString += ', '
				dayString += 'Piątek'
			if(isDay[5] != 0):
				if(dayString != ''):
					dayString += ', '
				dayString += 'Sobota'
			if(isDay[6] != 0):
				if(dayString != ''):
					dayString += ', '
				dayString += 'Niedziela'
			sHour = formatType[4:6]
			sMinutes = formatType[6:8]
			eHour = formatType[8:10]
			eMinutes = formatType[10:12]
			typeFor = formatType[12]
			disc = formatType[13:16]
			disc = int(disc)
			hourString = sHour + ':' + sMinutes + ' - ' + eHour + ':' + eMinutes
			forString = ''
			if(typeFor == "0"):
				forString = "Zarejestrowany"
			elif(typeFor == "1"):
				forString = "Niezarejestrowany"
			else:
				forString = "Wszyscy"
			discString = str(disc) + '%'
			row = {'active':active, 'days':dayString, 'hours':hourString, 'for':forString, 'disc':discString, 'id':curRow.id}
			toDisp.append(row)
		contents = {'title':'Zniżki','count':discounts.count(), 'content':toDisp}
	else:
		contents = {'title':'Zniżki', 'content':'Brak zdefiniowanych zniżek'}
	return contents
	
def discount(request):
	return render(request, 'manage_discount.html', display_discount())

def discount_delete(request, del_id):
	try:
		did = int(del_id)
	except ValueError:
		contents['messageType'] = 'danger'
		contents['message'] = 'Podano niepoprawny numer'
		return render(request, 'manage_discount.html', contents)
	mainContent = ''
	contents = display_discount()
	toDel = Discount.objects.filter(id=did)
	if(toDel.count() == 1):
		toDel[0].delete()
		contents = display_discount()
		contents['messageType'] = 'success'
		contents['message'] = 'Poprawnie usunięto wybraną zniżkę'
	elif(toDel.count() > 1):
		contents['messageType'] = 'danger'
		contents['message'] = 'Nieznany błąd'
	else:
		contents['messageType'] = 'danger'
		contents['message'] = 'Podano niepoprawny numer'
	return render(request, 'manage_discount.html', contents)

def discount_edit(request, edit_id):
	try:
		eid = int(edit_id)
	except ValueError:
		contents = {'title':'Zniżki', 'type':'danger', 'message':'Podano niepoprawny numer'}
		return render(request, 'manage_discount.html', contents)
	mainContent = ''
	contents = {'title':'Zniżki', 'type':'edit', 'content':mainContent}
	toEdit = Discount.objects.filter(id=eid)
	status = False
	if(toEdit.count() == 1):
		isSent = request.POST.get('sent', False);
		if(isSent):
			typeFormat = ''
			active = request.POST.get('active', False);
			if(active):
				typeFormat += '1'
			else:
				typeFormat += '0'
			isDay=[0,0,0,0,0,0,0]
			isDay[0] = request.POST.get('day0', False);
			isDay[1] = request.POST.get('day1', False);
			isDay[2] = request.POST.get('day2', False);
			isDay[3] = request.POST.get('day3', False);
			isDay[4] = request.POST.get('day4', False);
			isDay[5] = request.POST.get('day5', False);
			isDay[6] = request.POST.get('day6', False);
			dayNum = 0;
			step=0;
			for day in isDay:
				if(day != False):
					dayNum = dayNum|(1<<step)
				step += 1
			if(dayNum > 0):
				if(dayNum < 100):
					typeFormat += '0'
				if(dayNum < 10):
					typeFormat += '0'
				typeFormat += str(dayNum)
				sHour = request.POST.get('shour', False);
				sMinutes = sHour[3:5]
				sHour = sHour[:2]
				try:
					sHour = int(sHour)
				except ValueError:
					sHour = 8
				#sMinutes = request.POST.get('sminutes', False);
				try:
					sMinutes = int(sMinutes)
				except ValueError:
					sMinutes = 0

				eHour = request.POST.get('ehour', False);
				eMinutes = eHour[3:5]
				eHour = eHour[:2]
				try:
					eHour = int(eHour)
				except ValueError:
					eHour = 12
				#eMinutes = request.POST.get('eminutes', False);
				try:
					eMinutes = int(eMinutes)
				except ValueError:
					eMinutes = 0
				if(sHour > 23):
					sHour = 23
				if(sHour < 0):
					sHour = 0
				if(eHour > 23):
					eHour = 23
				if(eHour < 0):
					eHour = 0
				if(sMinutes > 59):
					sMinutes = 59
				if(sMinutes < 0):
					sMinutes = 0
				if(eMinutes > 59):
					eMinutes = 59
				if(eMinutes < 0):
					eMinutes = 0
				if(sHour<10):
					typeFormat += '0'
				typeFormat += str(sHour)
				if(sMinutes<10):
					typeFormat += '0'
				typeFormat += str(sMinutes)
				if(eHour<10):
					typeFormat += '0'
				typeFormat += str(eHour)
				if(eMinutes<10):
					typeFormat += '0'
				typeFormat += str(eMinutes)
				typeFor = request.POST.get('type', False);
				typeFormat += typeFor
				disc = request.POST.get('disc', False);
				try:
					disc = int(disc)
				except ValueError:
					disc = 0
				if(disc > 100):
					disc = 100
				if(disc < 0):
					disc = 0
				if(disc<100):
					typeFormat += '0'
				if(disc<10):
					typeFormat += '0'
				typeFormat += str(disc)
				dbSave = toEdit[0]
				dbSave.type = typeFormat
				dbSave.value = disc
				dbSave.save()
				status = True
				formatType = typeFormat
		formatType = toEdit[0].type
		days = formatType[1:4]
		days = int(days)
		isDay=[0,0,0,0,0,0,0]
		isDay[0] = days&0x1
		isDay[1] = (days>>1)&0x1
		isDay[2] = (days>>2)&0x1
		isDay[3] = (days>>3)&0x1
		isDay[4] = (days>>4)&0x1
		isDay[5] = (days>>5)&0x1
		isDay[6] = (days>>6)&0x1
		active = formatType[0]
		active = int(active)
		sHour = formatType[4:6]
		sMinutes = formatType[6:8]
		eHour = formatType[8:10]
		eMinutes = formatType[10:12]
		typeFor = formatType[12]
		disc = formatType[13:16]
		disc = int(disc)
		contents = {'title':'Zniżki', 'type':'edit', 'content':mainContent, 'id':eid, 'day0':isDay[0], 'day1':isDay[1], 'day2':isDay[2], 'day3':isDay[3], 'day4':isDay[4], 'day5':isDay[5], 'day6':isDay[6], 'sHour':sHour, 'sMinutes':sMinutes, 'eHour':eHour, 'eMinutes':eMinutes, 'typeFor':typeFor, 'disc':disc, 'active':active}
		if(status):
			contents['messageType'] = 'success'
			contents['message'] = 'Zapisano poprawnie'
	elif(toEdit.count() > 1):
		contents = {'title':'Zniżki', 'messageType':'danger', 'message':'Nieznany błąd'}
		return render(request, 'manage_discount.html', contents)
	else:
		contents = {'title':'Zniżki', 'messageType':'danger', 'message':'Podano niepoprawny numer'}
		return render(request, 'manage_discount.html', contents)
	return render(request, 'manage_discountaddedit.html', contents)

def discount_add(request):
	#TODO dodac sprawdzenie czy zalogowany i ma uprawnienia
	isSent = request.POST.get('sent', False);
	mainContent = '';
	contents = {'title':'Zniżki', 'type':'add'}
	if(isSent):
		typeFormat = '1';
		isDay=[0,0,0,0,0,0,0]
		isDay[0] = request.POST.get('day0', False);
		isDay[1] = request.POST.get('day1', False);
		isDay[2] = request.POST.get('day2', False);
		isDay[3] = request.POST.get('day3', False);
		isDay[4] = request.POST.get('day4', False);
		isDay[5] = request.POST.get('day5', False);
		isDay[6] = request.POST.get('day6', False);
		dayNum = 0;
		step=0;
		for day in isDay:
			if(day != False):
				dayNum = dayNum|(1<<step)
			step += 1
		if(dayNum > 0):
			if(dayNum < 100):
				typeFormat += '0'
			if(dayNum < 10):
				typeFormat += '0'
			typeFormat += str(dayNum)
			sHour = request.POST.get('shour', False);
			sMinutes = sHour[3:5]
			sHour = sHour[:2]
			try:
				sHour = int(sHour)
			except ValueError:
				sHour = 8
			#sMinutes = request.POST.get('sminutes', False);
			try:
				sMinutes = int(sMinutes)
			except ValueError:
				sMinutes = 0
			eHour = request.POST.get('ehour', False);
			eMinutes = eHour[3:5]
			eHour = eHour[:2]
			try:
				eHour = int(eHour)
			except ValueError:
				eHour = 12
			#eMinutes = request.POST.get('eminutes', False);
			try:
				eMinutes = int(eMinutes)
			except ValueError:
				eMinutes = 0
			if(sHour > 23):
				sHour = 23
			if(sHour < 0):
				sHour = 0
			if(eHour > 23):
				eHour = 23
			if(eHour < 0):
				eHour = 0
			if(sMinutes > 59):
				sMinutes = 59
			if(sMinutes < 0):
				sMinutes = 0
			if(eMinutes > 59):
				eMinutes = 59
			if(eMinutes < 0):
				eMinutes = 0
			if(sHour<10):
				typeFormat += '0'
			typeFormat += str(sHour)
			if(sMinutes<10):
				typeFormat += '0'
			typeFormat += str(sMinutes)
			if(eHour<10):
				typeFormat += '0'
			typeFormat += str(eHour)
			if(eMinutes<10):
				typeFormat += '0'
			typeFormat += str(eMinutes)
			typeFor = request.POST.get('type', False);
			typeFormat += typeFor
			disc = request.POST.get('disc', False);
			try:
				disc = int(disc)
			except ValueError:
				disc = 0
			if(disc > 100):
				disc = 100
			if(disc < 0):
				disc = 0
			if(disc<100):
				typeFormat += '0'
			if(disc<10):
				typeFormat += '0'
			typeFormat += str(disc)
			newDisc = Discount(type=typeFormat, value=disc)
			newDisc.save()
			contents = {'title':'Zniżki', 'messageType':'success', 'message':'Dodano nową zniżkę', 'type':'add'}
			return render(request, 'manage_discountaddedit.html', contents)
		else:
			contents = {'title':'Zniżki', 'messageType':'danger', 'message':'Nie wybrano żadnego dnia', 'type':'add'}
	return render(request, 'manage_discountaddedit.html', contents)
	
def user_register(request):
	mainContent = '';
	contents = {'title':'Rejestracja', 'name':'', 'second_name':'', 'password':'', 'address':'', 'city':'', 'postal_code':'', 'phone_number':'', 'username':''}
	if(request.POST.get('sent')):
		reg_username = request.POST.get('username')
		reg_name = request.POST.get('name')
		reg_password = request.POST.get('password')
		reg_postal_code = request.POST.get('postal_code1')+request.POST.get('postal_code2')
		reg_phone_number = request.POST.get('phone_number')
		reg_address = request.POST.get('address')
		reg_city = request.POST.get('city')
		reg_second_name = request.POST.get('second_name')
		if(not(request.POST.get('agg0')) or not(request.POST.get('agg1'))):
			contents = {'title':'Błąd!!!', 'messageType':'danger', 'message':'Zgody muszą być zaznaczone!', 'name':str(reg_name), 'second_name':str(reg_second_name), 'address':str(reg_address), 'city':str(reg_city), 'postal_code':str(reg_postal_code), 'phone_number':str(reg_phone_number), 'username':str(reg_username)}
			return render(request,'user_register.html',contents)
		if not(re.match('[a-zA-ZćśźżńłóąęĆŚŹŻŃŁÓĄĘ]+$',str(reg_name))):
			contents = {'title':'Błąd!!!', 'messageType':'danger', 'message':'Niepoprawne imię!', 'second_name':str(reg_second_name), 'address':str(reg_address), 'city':str(reg_city), 'postal_code':str(reg_postal_code), 'phone_number':str(reg_phone_number), 'username':str(reg_username)}
			return render(request,'user_register.html',contents)
		if not(re.match('[a-zA-ZćśźżńłóąęĆŚŹŻŃŁÓĄĘ]+$',str(reg_second_name))):
			contents = {'title':'Błąd!!!', 'messageType':'danger', 'message':'Niepoprawne nazwisko!', 'name':str(reg_name), 'address':str(reg_address), 'city':str(reg_city), 'postal_code':str(reg_postal_code), 'phone_number':str(reg_phone_number), 'username':str(reg_username) }
			return render(request,'user_register.html',contents)
		if not(re.match('[a-zA-ZćśźżńłóąęĆŚŹŻŃŁÓĄĘ]+$',str(reg_city))):
			contents = {'title':'Błąd!!!', 'messageType':'danger', 'message':'Niepoprawne miasto!', 'name':str(reg_name), 'second_name':str(reg_second_name), 'address':str(reg_address), 'postal_code':str(reg_postal_code), 'phone_number':str(reg_phone_number), 'username':str(reg_username)}
			return render(request,'user_register.html',contents)
		if not(re.match('[0-9]{5,5}',str(reg_postal_code))):
			contents = {'title':'Błąd!!!', 'messageType':'danger', 'message':'Niepoprawny kod pocztowy!', 'name':str(reg_name), 'second_name':str(reg_second_name), 'address':str(reg_address), 'city':str(reg_city), 'phone_number':str(reg_phone_number), 'username':str(reg_username)}
			return render(request,'user_register.html',contents)
		if not(re.match('[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]',str(reg_phone_number))):
			contents = {'title':'Błąd!!!', 'messageType':'danger', 'message':'Niepoprawny numer telefonu!', 'name':str(reg_name), 'second_name':str(reg_second_name), 'address':str(reg_address), 'city':str(reg_city), 'postal_code':str(reg_postal_code), 'username':str(reg_username)}
			return render(request,'user_register.html',contents)
		if (not(re.match('.{6,64}',str(reg_password)))):
				contents = {'title':'Błąd!!!', 'messageType':'danger', 'message':'Hasło musi mieć min 6 znaków i max 64 znaków!', 'name':str(reg_name), 'second_name':str(reg_second_name), 'address':str(reg_address), 'city':str(reg_city), 'postal_code':str(reg_postal_code), 'phone_number':str(reg_phone_number), 'username':str(reg_username)}
				return render(request,'user_register.html',contents)
		if (not(re.match('.{6,64}',str(reg_username)))):
				contents = {'title':'Błąd!!!', 'messageType':'danger', 'message':'Nazwa użytkownika musi mieć min 6 znaków i max 64 znaków!', 'name':str(reg_name), 'second_name':str(reg_second_name), 'address':str(reg_address), 'city':str(reg_city), 'postal_code':str(reg_postal_code), 'phone_number':str(reg_phone_number), 'username':str(reg_username)}
				return render(request,'user_register.html',contents)
		if (not(re.match('.{1,64}',str(reg_address)))):
				contents = {'title':'Błąd!!!', 'messageType':'danger', 'message':'Adres nie może być pusty!', 'name':str(reg_name), 'second_name':str(reg_second_name), 'address':str(reg_address), 'city':str(reg_city), 'postal_code':str(reg_postal_code), 'phone_number':str(reg_phone_number), 'username':str(reg_username)}
				return render(request,'user_register.html',contents)
		users = User.objects.all()
		for user in users:
			if(user.username == str(reg_username)):
				contents = {'title':'Błąd!!!', 'messageType':'danger', 'message':'Nazwa użytkownika zajęta!', 'name':str(reg_name), 'second_name':str(reg_second_name), 'address':str(reg_address), 'city':str(reg_city), 'postal_code':str(reg_postal_code), 'phone_number':str(reg_phone_number), 'username':''}	
				return render(request,'user_register.html',contents)	
		good=1
		if good:
			reg_password=hashlib.sha256(reg_password.encode()).hexdigest()
			##DOPOKI NIE MA TYPE I SCHEDULE, TRZEBA ZEZWOLIC CHWILOWO NA NULL!, PRZYJMUJEMY ZE UZYTKOWNICY ZE ZWYKLEGO REGISTER DOSTAJA SCHEDULE 0 CZYLI BRAK BO TO KLIENCI, TYP 0, ZMIANA TYPU MOZLIWA PRZEZ PANEL ADMINA KTORY KTOS ZROBI##
			newUser = User(name=reg_name, second_name=reg_second_name, username=reg_username, password=reg_password, postal_code=reg_postal_code, phone_number=reg_phone_number, city=reg_city, address=reg_address)
			newUser.save()
			contents = {'messageType':'success', 'message':'Użytkownik zarejestrowany','name':'', 'second_name':'', 'address':'', 'city':'', 'postal_code':'', 'phone_number':'', 'username':''}
	return render(request, 'user_register.html', contents)

def display_product_category():
	product_categories = Product_Category.objects.all()
	contents = {'title':'Kategorie Produktów', 'content':''}
	if(product_categories.count() > 0):
		toDisp = []
		for curRow in product_categories:
			if(curRow.parent != None):
				parent_name = curRow.parent.name
				parent_id = curRow.parent.cat_id
			else:
				parent_name = "-"
				parent_id = 0
			row = {'name':curRow.name, 'desc':curRow.description,'type':curRow.get_type_display() , 'add_price':curRow.additional_price, 'parent':parent_name, 'id':curRow.cat_id, 'parent_id': parent_id, 'demand': curRow.get_demand_ingredients_display()}
			toDisp.append(row)
			contents = {'title':'Kategorie Produktów','count':product_categories.count(), 'content':toDisp}
	else:
		contents = {'title':'Kategorie Produktów', 'content':'Brak zdefiniowanych kategorii', 'count':0}
	return contents	
	
def product_category(request):
	return render(request, 'manage_product_category.html', display_product_category())

def product_category_add(request):
	#zabezpieczyc zeby nie dawca nizej niz 3 poziom
	product_categories = Product_Category.objects.all()
	toDisp = []
	if(product_categories.count() > 0):
		for curRow in product_categories:
			if(curRow.parent != None):
				cpar = curRow.parent.cat_id
			else:
				cpar = 0
			row = {'name':curRow.name, 'id':curRow.cat_id, 'parent': cpar}
			toDisp.append(row)
			contents = {'title':'Kategorie Produktów','count':product_categories.count(), 'contents':'','parents':toDisp}
	isSent = request.POST.get('sent', False);
	if(isSent):
		cname =  request.POST.get('name', False)
		cdesc = request.POST.get('description', False)
		cdemand = request.POST.get('demand_ingredient',False)
		try:
			cdemand = int(cdemand)
		except:
			cdemand = 0
		if(cdemand != 1):
			cdemand = 0
		cadd_price = request.POST.get('additional_price', False)
		try:
			cadd_price = float(cadd_price)
		except:
			cadd_price = 0
		if(cadd_price >= 1000):
			cadd_price = 999.99
		elif(cadd_price < 0):
			cadd_price = 0
		cid = request.POST.get('parent', False);
		try:
			cparent = int(cid)
		except:
			cparent = 0
		if(cparent == 0):
			cparent = None
		else:
			try:
				cparent = Product_Category.objects.get(cat_id=cparent)
			except Product_Category.DoesNotExist:
				contents['messageType'] = 'danger'
				contents['message'] = 'Wystąpił nieoczekiwany błąd'
				return render(request, 'manage_product_category.html', contents)
			cdemand = 0
		if(cparent != None):	
			if(cparent.type == '1'):
				ctype = '2'
			else:
				ctype = '3'
		else:
			ctype = '1'
		contents = {'title':'Kategorie Produktów', 'type': 'add', 'parents':toDisp, 'count':product_categories.count()}
		if(cparent != None and cparent.type == '3' ):
			contents['messageType'] = 'danger'
			contents['message'] = 'Ta podkategoria nie może być kategorią nadrzędną'
		else:
			newCategory = Product_Category(name = cname, description = cdesc, additional_price = cadd_price, parent = cparent, type = ctype, demand_ingredients = cdemand)
			newCategory.save()
			contents['messageType'] = 'success'
			contents['message'] = 'Dodano nową kategorię'
	else:
		contents = {'title':'Kategorie Produktów', 'type': 'add', 'parents':toDisp, 'count':product_categories.count()}
	return render(request, 'manage_product_category_addedit.html', contents)

def product_category_edit(request, edit_id):
	#zabezpieczyc zeby nie dawac kategorii nizej niz 3 poziom drzewa
	#contents = display_product_category()
	try:
		editid = int(edit_id)
	except ValueError:
		contents['messageType'] = 'danger'
		contents['message'] = 'Podano niepoprawny numer kategorii'
		return render(request, 'manage_product_category.html', contents)
	try:
		editCat = Product_Category.objects.get(cat_id=edit_id)
	except Product_Category.DoesNotExist:
		contents['messageType'] = 'danger'
		contents['message'] = 'Wybrana kategoria nie istnieje'
		return render(request, 'manage_product_category.html', contents)
	contents = {'title':'Kategorie Produktów', 'type':'edit'}
	contents['id']=editCat.cat_id
	contents['name']=editCat.name
	contents['desc']=editCat.description
	contents['add_price']=editCat.additional_price
	contents['demand']=editCat.demand_ingredients
	if(editCat.parent != None):
		contents['parent']=editCat.parent.cat_id
	else:
		contents['parent']=0
		
	product_categories = Product_Category.objects.all()
	toDisp = []
	contents['count']=0
	if(product_categories.count() > 0):
		for curRow in product_categories:
			if(curRow.parent != None):
				cpar = curRow.parent.cat_id
			else:
				cpar = 0
			row = {'name':curRow.name, 'id':curRow.cat_id, 'parent': cpar}
			toDisp.append(row)
			contents['count']=product_categories.count()
			contents['parents']=toDisp
			
	if(request.POST.get('sent', False)):
		cid = request.POST.get('id',False);
		try:
			cid = int(cid)
		except:
			contents['messageType'] = 'danger'
			contents['message'] = 'Wystąpił nieoczekiwany błąd'
			return render(request, 'manage_product_category.html', contents)
		cname =  request.POST.get('name', False)
		cdesc = request.POST.get('description', False)
		cdemand = request.POST.get('demand_ingredient',False)
		try:
			cdemand = int(cdemand)
		except:
			cdemand = 0
		if(cdemand != 1):
			cdemand = 0
		print (cdemand)
		cadd_price = request.POST.get('additional_price', False)
		try:
			cadd_price = float(cadd_price)
		except:
			cadd_price = 0
		if(cadd_price >= 1000):
			cadd_price = 999.99
		elif(cadd_price < 0):
			cadd_price = 0
		cparent = request.POST.get('parent', False);
		try:
			cparent = int(cparent)
		except:
			cparent = 0
		if(cparent == 0):
			cparent = None
		else:
			try:
				cparent = Product_Category.objects.get(cat_id=cparent)
			except Product_Category.DoesNotExist:
				contents['messageType'] = 'danger'
				contents['message'] = 'Wystąpił nieoczekiwany błąd'
				return render(request, 'manage_product_category.html', contents)
			cdemand = 0
		if(cparent != None):	
			if(cparent.type == '1'):
				ctype = '2'
			else:
				ctype = '3'
		else:
			ctype = '1'
		editCat.name = cname
		editCat.description = cdesc
		editCat.additional_price = cadd_price
		editCat.parent = cparent
		editCat.type = ctype
		editCat.demand_ingredients = cdemand
		if(cparent != None and cparent.type == '3'):
			contents['messageType'] = 'danger'
			contents['message'] = 'Ta podkategoria nie może być kategorią nadrzędną'
		else:
			editCat.save()
			contents['messageType'] = 'success'
			contents['message'] = 'Kategoria poprawnie zapisana'
		contents['id']=editCat.cat_id
		contents['name']=editCat.name
		contents['ctype']=editCat.type
		contents['desc']=editCat.description
		contents['add_price']=editCat.additional_price
		contents['demand']=editCat.demand_ingredients
		if(editCat.parent != None):
			contents['parent']=editCat.parent.cat_id
		else:
			contents['parent']=0
	return render(request, 'manage_product_category_addedit.html', contents)

def product_category_delete(request, del_id):
	contents = display_product_category()
	try:
		delete = int(del_id)
	except:
		contents['messageType'] = 'danger'
		contents['message'] = 'Podano niepoprawny numer kategorii'
		return render(request, 'manage_product_category.html', contents)
	try:
		delCat = Product_Category.objects.get(cat_id=delete)
	except Product_Category.DoesNotExist:
		contents['messageType'] = 'danger'
		contents['message'] = 'Wybrana kategoria nie istnieje'
		return render(request, 'manage_product_category.html', contents)
	delCat.delete()
	contents = display_product_category()
	contents['messageType'] = 'success'
	contents['message'] = 'Poprawnie usunięto wybraną kategorię'
	return render(request, 'manage_product_category.html', contents)

	
def display_user_type():
	types = User_Type.objects.all()
	contents = {'title':'Typy użytkowników', 'content':''}
	if(types.count() > 0):
		toDisp = []
		for curRow in types:
			add = "Nie"
			if(curRow.canCreate == 1):
				add = "Tak"
			edit = "Nie"
			if(curRow.canEdit == 1):
				edit = "Tak"
			delete = "Nie"
			if(curRow.canDelete == 1):
				delete = "Tak"
			deliver = "Nie"
			if(curRow.canDeliver == 1):
				deliver = "Tak"
			manage = "Nie"
			if(curRow.canManage == 1):
				manage = "Tak"
			row = {'name':curRow.type_name, 'add':add,'edit':edit , 'delete':delete, 'deliver':deliver, 'manage':manage, 'id':curRow.id}
			toDisp.append(row)
			contents = {'title':'Typy użytkowników','count':types.count(), 'content':toDisp}
	else:
		contents = {'title':'Typy użytkowników', 'content':'Brak zdefiniowanych typów', 'count':0}
	return contents

def user_type(request):
	return render(request, 'manage_user_type.html', display_user_type())
	
def user_type_add(request):
	contents = {'title':'Typy użytkowników', 'type':'add'}
	if(request.POST.get('sent', False)):
		name = request.POST.get('name', False)
		create = request.POST.get('create', False)
		edit = request.POST.get('edit', False)
		delete = request.POST.get('delete', False)
		deliver = request.POST.get('deliver', False)
		manage = request.POST.get('manage', False)
		if(len(name) < 3):
			contents['messageType'] = 'danger'
			contents['message'] = 'Nazwa nie może być krótsza niż 3 znaki'
			return render(request, 'manage_user_type_addedit.html', contents)
		try:
			check = User_Type.objects.get(type_name=name)
		except User_Type.DoesNotExist:
			toSave = User_Type(type_name=name, canCreate=create, canEdit=edit, canDelete=delete, canDeliver=deliver, canManage=manage)
			toSave.save()
			contents['messageType'] = 'success'
			contents['message'] = 'Dodano nowy typ użytkowników'
			return render(request, 'manage_user_type_addedit.html', contents)
		contents['messageType'] = 'danger'
		contents['message'] = 'Nazwa jest już używana'
	return render(request, 'manage_user_type_addedit.html', contents)
	
def user_type_delete(request, del_id):
	contents = display_user_type()
	try:
		delete = int(del_id)
	except ValueError:
		contents['messageType'] = 'danger'
		contents['message'] = 'Podano niepoprawny numer typu'
		return render(request, 'manage_user_type.html', contents)
	try:
		user = User_Type.objects.get(id=delete)
	except User_Type.DoesNotExist:
		contents['messageType'] = 'danger'
		contents['message'] = 'Wybrany typ nie istnieje'
		return render(request, 'manage_user_type.html', contents)
	user.delete()
	contents = display_user_type()
	contents['messageType'] = 'success'
	contents['message'] = 'Poprawnie usunięto wybrany typ'
	return render(request, 'manage_user_type.html', contents)

def user_type_edit(request, edit_id):
	contents = display_user_type()
	try:
		editid = int(edit_id)
	except ValueError:
		contents['messageType'] = 'danger'
		contents['message'] = 'Podano niepoprawny numer typu'
		return render(request, 'manage_user_type.html', contents)
	try:
		user = User_Type.objects.get(id=editid)
	except User_Type.DoesNotExist:
		contents['messageType'] = 'danger'
		contents['message'] = 'Wybrany typ nie istnieje'
		return render(request, 'manage_user_type.html', contents)
	contents = {'title':'Typy użytkowników', 'type':'edit'}
	contents['id']=user.id
	contents['name']=user.type_name
	contents['create']=user.canCreate
	contents['edit']=user.canEdit
	contents['delete']=user.canDelete
	contents['deliver']=user.canDeliver
	contents['manage']=user.canManage
	if(request.POST.get('sent', False)):
		name = request.POST.get('name', False)
		create = request.POST.get('create', False)
		edit = request.POST.get('edit', False)
		delete = request.POST.get('delete', False)
		deliver = request.POST.get('deliver', False)
		manage = request.POST.get('manage', False)
		if(len(name) < 3):
			contents['messageType'] = 'danger'
			contents['message'] = 'Nazwa nie może być krótsza niż 3 znaki'
			return render(request, 'manage_user_type_addedit.html', contents)
		goodToGo = False
		try:
			check = User_Type.objects.get(type_name=name)
		except User_Type.DoesNotExist:
			goodToGo = True
		if(goodToGo == False and check.id != user.id):
			contents['messageType'] = 'danger'
			contents['message'] = 'Nazwa jest już używana'
			return render(request, 'manage_user_type_addedit.html', contents)
		user.type_name = name
		user.canCreate = create
		user.canEdit = edit
		user.canDelete = delete
		user.canDeliver = deliver
		user.canManage = manage
		user.save()
		contents = display_user_type()
		contents['messageType'] = 'success'
		contents['message'] = 'Typ został zmieniony'
		return render(request, 'manage_user_type.html', contents)
	return render(request, 'manage_user_type_addedit.html', contents)

	
def magazine(request):
	check = user_check(request)
	if ('messageType' in check and check['messageType'] == 'danger'):
		return render(request, 'user_login.html', check)
	elif not check['canManage'] == True:
		return render(request, 'index.html', check)		
	
	ingredients = Ingredient.objects.all()
	
	contents = {'ingredients': ingredients, 'title': "Magazyn", 'messageType':'None'}
	return render(request, 'manage_magazine.html', contents)
	
def magazine_add(request):
	check = user_check(request)
	if ('messageType' in check and check['messageType'] == 'danger'):
		return render(request, 'user_login.html', check)
	elif not check['canManage'] == True:
		return render(request, 'index.html', check)		

	if(request.POST.get('sent')):		
		ingredient_name = request.POST.get('ingredient_name', False);
		quantityx = request.POST.get('count', False);
		min_quantityx = request.POST.get('min_count', False)
		pricex = request.POST.get('price', False)
		unitsx = request.POST.get('units', False)
		
		ingredient_name = str(ingredient_name)
		if ingredient_name: 	
			

			if(pricex.count(",") > 1 or pricex.count(".") > 1 or quantityx.count(",") > 1 or quantityx.count(".") > 1 or min_quantityx.count(",") > 1 or min_quantityx.count(".") > 1):
				contents = {'title': "Magazyn", 'messageType':'danger', 'message':'Błędna/e wartości cena, ilość, min. ilość!', 'type': 'add'}		
				return render(request, 'manage_magazine_addedit.html', contents)
			
			for ingredient in ingredients:
				if(ingredient.name == ingredient_name):		
					contents = {'title': "Magazyn", 'messageType':'danger', 'message':'Składnik o takiej nazwie już istnieje!'}		
					return render(request, 'manage_magazine_addedit.html', contents)
			
			pricex = pricex.replace(',', '.');	
			quantityx = quantityx.replace(',', '.');
			min_quantityx = min_quantityx.replace(',', '.');
			
			if(unitsx == 'Kilogram'):
				unitsx = 'kg'
			elif(unitsx == 'Litr'):
				unitsx = 'l'
			else:
				unitsx = 'szt'
				
			try:	
				quantityx = float(quantityx)
			except ValueError:
				quantityx = 0
			try:		
				min_quantityx = float(min_quantityx)
			except ValueError:
				min_quantityx = 0
			try:	
				pricex = float(pricex)
			except ValueError:
				pricex = 0
		
			newIngredient = Ingredient(name=ingredient_name, price=pricex, quantity=quantityx, units=unitsx, min_quantity=min_quantityx)
			newIngredient.save()			
			contents = {'title': "Magazyn", 'messageType':'success', 'message': 'Pomyślnie dodano składnik do bazy!', 'type': 'add'}
			return render(request, 'manage_magazine_addedit.html', contents)
			
		else:	
			contents = {'title': "Magazyn", 'messageType':'danger', 'message': 'Niepoprawna nazwa składnika!', 'type': 'add'}
	else:
		contents = {'title': "Magazyn", 'messageType':'none', 'type': 'add'}
		
	return render(request, 'manage_magazine_addedit.html', contents)	

def magazine_edit(request, edit_id):
	check = user_check(request)
	if ('messageType' in check and check['messageType'] == 'danger'):
		return render(request, 'user_login.html', check)
	elif not check['canManage'] == True:
		return render(request, 'index.html', check)		
		
	try:
		eid = int(edit_id)
	except ValueError:
		contents = {'title':'Magazyn', 'type':'danger', 'content':'Podany element nie istnieje!'}
		return render(request, 'manage_magazine.html', contents)
	ingredients = Ingredient.objects.all()
	toEdit = Ingredient.objects.get(id=edit_id)
	if(toEdit):		
		contents = {'title': "Magazyn", 'messageType':'none', 'type': 'edit', 'toEdit': toEdit}
		
		if(request.POST.get('sent')):		
			ingredient_name = request.POST.get('ingredient_name', False);
			quantityx = request.POST.get('count', False);
			min_quantityx = request.POST.get('min_count', False)
			pricex = request.POST.get('price', False)
			unitsx = request.POST.get('units', False)
			
			ingredient_name = str(ingredient_name)
			if ingredient_name: 	
				

				if(pricex.count(",") > 1 or pricex.count(".") > 1 or quantityx.count(",") > 1 or quantityx.count(".") > 1 or min_quantityx.count(",") > 1 or min_quantityx.count(".") > 1):
					contents = {'title': "Magazyn", 'messageType':'danger', 'message':'Błędna/e wartości cena, ilość, min. ilość!'}		
					return render(request, 'manage_magazine_addedit.html', contents)
				
				for ingredient in ingredients:
					if(ingredient.name == ingredient_name and ingredient.id != eid):		
						contents = {'title': "Magazyn",'messageType':'danger', 'message':'Składnik o takiej nazwie już istnieje!'}		
						return render(request, 'manage_magazine_addedit.html', contents)
				
				pricex = pricex.replace(',', '.');	
				quantityx = quantityx.replace(',', '.');
				min_quantityx = min_quantityx.replace(',', '.');
				
				if(unitsx == 'Kilogram'):
					unitsx = 'kg'
				elif(unitsx == 'Litr'):
					unitsx = 'l'
				else:
					unitsx = 'szt'
					
				try:	
					quantityx = float(quantityx)
				except ValueError:
					quantityx = 0
				try:		
					min_quantityx = float(min_quantityx)
				except ValueError:
					min_quantityx = 0
				try:	
					pricex = float(pricex)
				except ValueError:
					pricex = 0
			
				toEdit.name = ingredient_name
				toEdit.price = pricex
				toEdit.quantity = quantityx
				toEdit.units = unitsx
				toEdit.min_quantity = min_quantityx
				toEdit.save()	
				
				contents = {'title': "Magazyn", 'messageType':'success', 'message': 'Edycja składnika zakończyła się powodzeniem!', 'type': 'add'}
				return render(request, 'manage_magazine_addedit.html', contents)
				
			else:	
				contents = {'title': "Magazyn", 'messageType':'danger', 'message': 'Niepoprawna nazwa składnika!', 'type': 'edit', 'toEdit': toEdit }
	else:	
		contents = {'title': "Magazyn", 'messageType':'danger', 'message': 'Podany element nie istnieje!', 'type': 'edit', 'toEdit': toEdit}
		
	return render(request, 'manage_magazine_addedit.html', contents)
	
def magazine_delete(request, del_id):
	check = user_check(request)
	if ('messageType' in check and check['messageType'] == 'danger'):
		return render(request, 'user_login.html', check)
	elif not check['canManage'] == True:
		return render(request, 'index.html', check)		
	
	ingredients = Ingredient.objects.all()	
	try:
		did = int(del_id)
	except ValueError:
		contents = {'title':'Magazyn','messageType':'danger', 'message':'Taki element nie instnieje!','ingredients': ingredients,}
		return render(request, 'manage_magazine.html', contents)
	toDel = Ingredient.objects.filter(id=did)
	if(toDel.count() == 1):
		toDel[0].delete()		
		contents = {'title':'Magazyn','messageType':'success', 'message':'Składnik został usunięty!','ingredients': ingredients,}
		return render(request, 'manage_magazine.html', contents)
	elif(toDel.count() > 1):
		contents = {'title':'Magazyn','messageType':'danger', 'message':'Nieznany błąd','ingredients': ingredients}
	else:
		contents = {'title':'Magazyn','messageType':'danger', 'message':'Taki element nie instnieje!','ingredients': ingredients}
	
	return render(request, 'manage_magazine.html', contents)

def get_subcategories(maincat):
	subcategories = {}
	categories = maincat
	subcategory = Product_Category.objects.filter(parent=maincat)
	for subcat in subcategory:
		if(subcat.type == '2'):
			subsubcat = Product_Category.objects.filter(parent=subcat.cat_id)
			for curcat in subsubcat:
				if not((subcat.name) in subcategories):
					subcategories[subcat.name] = []
				subcategories[subcat.name].append([curcat.cat_id, curcat.name])
		else:
			if not((categories.name) in subcategories):
				subcategories[categories.name] = []
			subcategories[categories.name].append([subcat.cat_id, subcat.name])
	todel = []
	for key, each in subcategories.iteritems():
		if(len(each) == 0):
			todel.append(key)
	for k in todel:
		del subcategories[k]
	return subcategories
	
def basket(request):
	contents = {'title':'Koszyk'}
	if('basket_products' in request.session):
		products = request.session['basket_products'].split(';')
		prodCount = 0
		prodDisp = []
		orderPrice = 0
		for product in products:
			prodPrice = 0
			unpack = product.split(':')
			prodId = int(unpack[0])
			prodNum = int(unpack[1])
			prodRem = unpack[2]
			try:
				getProduct = Product.objects.get(product_code=prodId)
			except Product.DoesNotExist:
				toDel.append(product)
				continue
			prodId = getProduct.product_name
			prodPrice += getProduct.price
			prodCats = []
			if(len(unpack[3])>0):
				prodCats = unpack[3].split('-')
			prodIngs = []
			if(len(unpack[4])>0):
				prodIngs = unpack[4].split('-')
			badCats = []
			prodCatsNamed = []
			for cat in prodCats:
				try:
					checkCat = Product_Category.objects.get(cat_id=int(cat))
				except Product_Category.DoesNotExist:
					badCats.append(cat)
					continue
				prodCatsNamed.append(checkCat.name)
				prodPrice += checkCat.additional_price
			badIngs = []
			prodIngsNamed = []
			for ing in prodIngs:
				try:
					checkIng = Ingredient.objects.get(id=int(ing))
				except Ingredient.DoesNotExist:
					badIngs.append(ing)
					continue
				prodIngsNamed.append(checkIng.name)
				prodPrice += checkIng.price
			for badCat in badCats:
				if(len(badCat)>0):
					prodCats.remove(badCat)
			for badIng in badIngs:
				if(len(badIng)>0):
					prodIngs.remove(badIng)
			prodCount += 1
			prodPrice *= prodNum
			prodPriceDisc = prodPrice
			if(getProduct.discount != None and getProduct.discount.type[0] == '1'):
				disc = getProduct.discount.value
				days = getProduct.discount.type[1:4]
				days = int(days)
				isDay=[0,0,0,0,0,0,0]
				isDay[0] = days&0x1
				isDay[1] = (days>>1)&0x1
				isDay[2] = (days>>2)&0x1
				isDay[3] = (days>>3)&0x1
				isDay[4] = (days>>4)&0x1
				isDay[5] = (days>>5)&0x1
				isDay[6] = (days>>6)&0x1
				os.environ['TZ'] = 'Poland'
				time.tzset()
				timeFormat = time.strftime("%c")
				timeFormat = timeFormat.split(' ')
				onlyTime = timeFormat[3].split(':')
				cHour = int(onlyTime[0])
				cMin = int(onlyTime[1])
				sHour = int(getProduct.discount.type[4:6])
				sMin = int(getProduct.discount.type[6:8])
				eHour = int(getProduct.discount.type[8:10])
				eMin = int(getProduct.discount.type[10:12])
				checkDisc = False
				if((sHour < cHour or (sHour == cHour and sMin <= cMin)) and (eHour > cHour or (eHour==cHour and eMin >= cMin))):
					if(timeFormat[0] == 'Sun' and isDay[6] != 0):
						checkDisc = True
					elif(timeFormat[0] == 'Mon' and isDay[0] != 0):
						checkDisc = True
					elif(timeFormat[0] == 'Tue' and isDay[1] != 0):
						checkDisc = True
					elif(timeFormat[0] == 'Wed' and isDay[2] != 0):
						checkDisc = True
					elif(timeFormat[0] == 'Thu' and isDay[3] != 0):
						checkDisc = True
					elif(timeFormat[0] == 'Fri' and isDay[4] != 0):
						checkDisc = True
					elif(timeFormat[0] == 'Sat' and isDay[5] != 0):
						checkDisc = True
				if(checkDisc):
					TWOPLACES = Decimal(10) ** -2
					if(disc < 100):
						todec = '0.' + str(getProduct.discount.value)
					else:
						todec = '1.00'
					prodPriceDisc = (prodPrice * (Decimal('1.00') - Decimal(todec))).quantize(TWOPLACES)
			orderPrice += prodPriceDisc
			row = {'prodId':prodId, 'prodNum':prodNum, 'prodRem': prodRem, 'prodCats': ', '.join(prodCatsNamed), 'prodIngs': ', '.join(prodIngsNamed), 'prodCode': product, 'prodPrice':prodPrice, 'prodPriceDisc':prodPriceDisc}
			prodDisp.append(row)
		contents['orderPrice'] = orderPrice
		contents['productsList'] = prodDisp
		contents['products'] = prodCount
	else:
		contents['messageType'] = 'danger'
		contents['message'] = 'Koszyk jest pusty'
	return render(request, 'basket.html', contents)
	
def basket_order(request):
	action = request.POST.get('act', False)
	contents = {'title':'Koszyk'}
	contents['messageType'] = 'success'
	contents['message'] = action
	if(action == 'Aktualizuj'):
		newproducts = ''
		products = request.session['basket_products'].split(';')
		for curProd in products:
			unpack = curProd.split(':')
			try:
				id = int(unpack[0])
				amount = int(unpack[1])
			except ValueError:
				contents['messageType'] = 'danger'
				contents['message'] = 'Nieznany błąd'
				return render(request, 'basket.html', contents)
			getNums = request.POST.get(curProd, False)
			if(not getNums == False):
				prod_in = unpack[4]
				cat_in = unpack[3]
				amount = int(getNums)
				if(amount == 0):
					continue
				unpack[1] = str(amount)
				packed = ':'.join(unpack)
				if(len(newproducts) == 0):
					newproducts = packed
				else:
					newproducts += ';' + packed
		request.session['basket_products'] = newproducts
		contents['messageType'] = 'success'
		contents['message'] = 'Koszyk został zaktalizowany'
	elif(not action == False):
		if('basket_products' in request.session):
			products = request.session['basket_products'].split(';')
			orderPrice = 0
			for product in products:
				prodPrice = 0
				unpack = product.split(':')
				prodId = int(unpack[0])
				prodNum = int(unpack[1])
				prodRem = unpack[2]
				try:
					getProduct = Product.objects.get(product_code=prodId)
				except Product.DoesNotExist:
					toDel.append(product)
					continue
				prodId = getProduct.product_name
				prodPrice += getProduct.price
				prodCats = []
				if(len(unpack[3])>0):
					prodCats = unpack[3].split('-')
				prodIngs = []
				if(len(unpack[4])>0):
					prodIngs = unpack[4].split('-')
				badCats = []
				prodCatsNamed = []
				for cat in prodCats:
					try:
						checkCat = Product_Category.objects.get(cat_id=int(cat))
					except Product_Category.DoesNotExist:
						badCats.append(cat)
						continue
					prodCatsNamed.append(checkCat.name)
					prodPrice += checkCat.additional_price
				badIngs = []
				prodIngsNamed = []
				for ing in prodIngs:
					try:
						checkIng = Ingredient.objects.get(id=int(ing))
					except Ingredient.DoesNotExist:
						badIngs.append(ing)
						continue
					prodIngsNamed.append(checkIng.name)
					prodPrice += checkIng.price
				for badCat in badCats:
					if(len(badCat)>0):
						prodCats.remove(badCat)
				for badIng in badIngs:
					if(len(badIng)>0):
						prodIngs.remove(badIng)
				prodPrice *= prodNum
				prodPriceDisc = prodPrice
				if(getProduct.discount != None and getProduct.discount.type[0] == '1'):
					disc = getProduct.discount.value
					days = getProduct.discount.type[1:4]
					days = int(days)
					isDay=[0,0,0,0,0,0,0]
					isDay[0] = days&0x1
					isDay[1] = (days>>1)&0x1
					isDay[2] = (days>>2)&0x1
					isDay[3] = (days>>3)&0x1
					isDay[4] = (days>>4)&0x1
					isDay[5] = (days>>5)&0x1
					isDay[6] = (days>>6)&0x1
					os.environ['TZ'] = 'Poland'
					time.tzset()
					timeFormat = time.strftime("%c")
					timeFormat = timeFormat.split(' ')
					onlyTime = timeFormat[3].split(':')
					cHour = int(onlyTime[0])
					cMin = int(onlyTime[1])
					sHour = int(getProduct.discount.type[4:6])
					sMin = int(getProduct.discount.type[6:8])
					eHour = int(getProduct.discount.type[8:10])
					eMin = int(getProduct.discount.type[10:12])
					checkDisc = False
					if((sHour < cHour or (sHour == cHour and sMin <= cMin)) and (eHour > cHour or (eHour==cHour and eMin >= cMin))):
						if(timeFormat[0] == 'Sun' and isDay[6] != 0):
							checkDisc = True
						elif(timeFormat[0] == 'Mon' and isDay[0] != 0):
							checkDisc = True
						elif(timeFormat[0] == 'Tue' and isDay[1] != 0):
							checkDisc = True
						elif(timeFormat[0] == 'Wed' and isDay[2] != 0):
							checkDisc = True
						elif(timeFormat[0] == 'Thu' and isDay[3] != 0):
							checkDisc = True
						elif(timeFormat[0] == 'Fri' and isDay[4] != 0):
							checkDisc = True
						elif(timeFormat[0] == 'Sat' and isDay[5] != 0):
							checkDisc = True
					if(checkDisc):
						TWOPLACES = Decimal(10) ** -2
						if(disc < 100):
							todec = '0.' + str(getProduct.discount.value)
						else:
							todec = '1.00'
						prodPriceDisc = (prodPrice * (Decimal('1.00') - Decimal(todec))).quantize(TWOPLACES)
				orderPrice += prodPriceDisc
			contents['messageType'] = 'success'
			contents['message'] = orderPrice
		else:
			contents['messageType'] = 'danger'
			contents['message'] = 'Twój koszyk jest pusty'
	else:
		return basket(request)
	return render(request, 'basket.html', contents)
	
def basket_add(request, product_id):
	contents = {'title':'Dodaj do koszyka'}
	product_id = int(product_id)
	try:
		check = Product.objects.get(product_code=product_id)
	except Product.DoesNotExist:
		contents['messageType'] = 'danger'
		contents['message'] = 'Wybranego produktu nie ma w bazie'
		return render(request, 'basket.html', contents)
	subcategories = get_subcategories(check.category)

	if(request.POST.get('sent', False)):
		pingreds = request.POST.getlist('basket_products_ingredients', [])
		pingreds.sort()
		pingredsToCheck = '-'.join(pingreds)
		premarks = request.POST.get('basket_products_remarks', '')
		premarks = premarks.replace(':', ' ').replace(';', ' ').replace('-', ' ')
		selections = request.POST.getlist('selections', [])
		selections.sort()
		selectionsToCheck = '-'.join(selections)
		if('basket_products' in request.session):
			products = request.session['basket_products'].split(';')
			for curProd in products:
				unpack = curProd.split(':')
				try:
					id = int(unpack[0])
					amount = int(unpack[1])
				except ValueError:
					contents['messageType'] = 'danger'
					contents['message'] = 'Nieznany błąd'
					return render(request, 'basket.html', contents)
				if(id == product_id):
					prod_in = unpack[4]
					cat_in = unpack[3]
					if(prod_in == pingredsToCheck and premarks == unpack[2] and cat_in == selectionsToCheck):
						amount += 1
						products.remove(curProd)
						unpack[1] = str(amount)
						packed = ':'.join(unpack)
						products.append(packed)
						request.session['basket_products'] = ';'.join(products)
						contents['messageType'] = 'success'
						contents['message'] = 'Dodano wybrany produkt do koszyka'
						return render(request, 'basket.html', contents)
			forStr = ';' + str(product_id) + ':1' + ':' + premarks + ':'
			if(len(selections) > 0):
				forStr += '-'.join(selections)
			forStr += ':'
			if(len(pingreds) > 0):
				forStr += '-'.join(pingreds)
			request.session['basket_products'] += forStr
		else:
			forStr = str(product_id) + ':1' + ':' + premarks + ':'
			if(len(selections) > 0):
				forStr += '-'.join(selections)
			forStr += ':'
			if(len(pingreds) > 0):
				forStr += '-'.join(pingreds)
			request.session['basket_products'] = forStr
		contents['messageType'] = 'success'
		contents['message'] = 'Dodano wybrany produkt do koszyka'
		return render(request, 'basket.html', contents)
	availableIn = Ingredient.objects.filter(quantity__gt=0)
	if(availableIn.count() > 0):
		allIngreds = []
		for ingredient in availableIn:
			row = {'name':ingredient.name, 'id':ingredient.id, 'price':ingredient.price}
			allIngreds.append(row)
		contents['ingredients'] = allIngreds
		contents['count'] = availableIn.count()
	contents['name'] = check.product_name
	contents['categories'] = subcategories
	contents['id'] = product_id
	return render(request, 'basket_step2.html', contents)
def basket_remove(request, product_id):
	contents = {'title':'Usuń z koszyka'}
	if('basket_products' in request.session):
		products = request.session['basket_products'].split(';')
		for curProd in products:
			if(curProd == product_id):
				products.remove(curProd)
				if(len(products) > 0):
					request.session['basket_products'] = ";".join(products)
				else:
					del request.session['basket_products']
				contents['messageType'] = 'success'
				contents['message'] = 'Usunięto wybrany produkt'
				return render(request, 'basket.html', contents)
		contents['messageType'] = 'danger'
		contents['message'] = 'Wybranego produktu nie ma w Twoim koszyku'
		return render(request, 'basket.html', contents)
	else:
		contents['messageType'] = 'danger'
		contents['message'] = 'Twój koszyk jest pusty'
	return render(request, 'basket.html', contents)

def basket_clear(request):
	contents = {'title':'Wyczyść koszyk'}
	if('basket_products' in request.session):
		del request.session['basket_products']
	contents['messageType'] = 'success'
	contents['message'] = 'Koszyk jest pusty'
	return render(request, 'basket.html', contents)
	
def display_product():
	products = Product.objects.all()
	contents = {'title':'Produkty', 'content':''}
	if(products.count() > 0):
		toDisp = []
		for curRow in products:
			if(curRow.discount != None):
				disc_count = "TAK"
			else:
				disc_count = "NIE"
			
			count_product_ingredients = Ingredient_Product.objects.filter(product=curRow).count()
			row = {'id':curRow.product_code, 'name':curRow.product_name, 'price':curRow.price, 'desc': curRow.description, 'discount': curRow.discount, 'disc_count' : disc_count, 'prod_count': count_product_ingredients}
			toDisp.append(row)
			contents = {'title':'Produkty','count':products.count(), 'content':toDisp}
	else:
		contents = {'title':'Produkty', 'content':'Brak zdefiniowanych produktów', 'count':0}
	return contents	
	
def product(request):
	return render(request,'manage_product.html',display_product())
	
def product_add(request):
	contents = {'title':'Produkty', 'content':'', 'type': 'add'}
	toDisp = []
	### Wyswietlanie formularza ###
	#pobierz kategorie główne
	categories = Product_Category.objects.all()
	if(categories.count() > 0): #przypisz do zmiennej
		for curRow in categories:
			if(curRow.parent == None):
				row = {'name':curRow.name, 'id':curRow.cat_id, 'demand':curRow.demand_ingredients }
				toDisp.append(row)
			contents["categories_count"]=categories.count()
			contents["categories"]=toDisp
	#pobierz składniki
	toDisp = []
	ingredients = Ingredient.objects.all()
	if(ingredients.count() > 0):
		for curRow in ingredients:
			row = {'name': curRow.name, 'units': curRow.units, 'id': curRow.id, 'price': curRow.price}
			toDisp.append(row)
			contents["ingredients"] = toDisp
			contents["ingredients_count"] = ingredients.count()
	
	#pobierz zniżki
	contents["discounts"] = display_discount()
	for curRow in contents["discounts"]["content"]:
		if(curRow["days"]!= ""):
			days = curRow["days"].split(', ');
			curRow["days"] = ""
			for r in days:
				if(r == "Poniedziałek"):
					curRow["days"] += "Pn"
				elif(r == "Wtorek"):
					curRow["days"] += "-"
					curRow["days"] += "Wt"
				elif(r == "Środa"):
					curRow["days"] += "-"
					curRow["days"] += "Śr"
				elif(r == "Czwartek"):
					curRow["days"] += "-"
					curRow["days"] += "Cz"
				elif(r == "Piątek"):
					curRow["days"] += "-"
					curRow["days"] += "Pt"
				elif(r == "Sobota"):
					curRow["days"] += "-"
					curRow["days"] += "Sb"
				else:
					curRow["days"] += "-"
					curRow["days"] += "Nd"
	###Wczytywanie danych ###
	if(request.POST.get('sent')):
		pname = request.POST.get('name')
		pprice = request.POST.get('price')
		try:
			pprice = float(pprice)
		except:
			contents["messageType"] = 'danger'
			contents["message"] = 'Nie prawidłowa cena produktu'
			return render(request,'manage_product_addedit.html',contents)
		if(pprice < 0 or pprice >= 1000):
			contents["messageType"] = 'danger'
			contents["message"] = 'Nie prawidłowa cena produktu'
			return render(request,'manage_product_addedit.html',contents)	
		pdesc = request.POST.get('description')
		pcat = request.POST.get('category')
		try:
			pcat = Product_Category.objects.get(cat_id=pcat)
		except Product_Category.DoesNotExist:
			contents["messageType"] = 'danger'
			contents["message"] = 'Nie istnieje taka kategoria'
			return render(request,'manage_product_addedit.html',contents)
		if(pcat.parent != None):
			contents["messageType"] = 'danger'
			contents["message"] = 'Produkt nie może należeć do tej kategorii'
			return render(request,'manage_product_addedit.html',contents)
		pdisc = request.POST.get('discount')
		try:
			pdisc = int(pdisc)
		except:
			contents["messageType"] = 'danger'
			contents["message"] = 'Nie poprawny parametr zniżki'
			return render(request,'manage_product_addedit.html',contents)
		if(pdisc == 0):
			pdisc = None
		elif(pdisc > 0):
			try:
				pdisc = Discount.objects.get(id=pdisc)
			except Discount.DoesNotExist:
				contents["messageType"] = 'danger'
				contents["message"] = 'Wybrana zniżka nie istnieje'
				return render(request,'manage_product_addedit.html',contents)	
		pproduct = Product(product_name = pname, price = pprice, description = pdesc, discount = pdisc, category = pcat)
		pproduct.save()
		#powiazanie skladnikow dodac na samym koncu
		pingredients = Ingredient.objects.filter(units="kg")
		for curRow in pingredients:
			#pobiera skladnik po nazwie
			name = curRow.name+"--"+str(curRow.id)
			value = request.POST.get(name)
			try:
				value = float(value)
			except:
				contents["messageType"] = 'danger'
				contents["message"] = 'Niepoprawna wartość parametru'
				pproduct.delete()
				return render(request,'manage_product_addedit.html',contents)
			if(value < 0 and value >= 1000):
				contents["messageType"] = 'danger'
				contents["message"] = 'Niepoprawna wartość parametru'
				pproduct.delete()
				return render(request,'manage_product_addedit.html',contents)
			if(value > 0):			
				product_ing = Ingredient_Product(quantity=value, ingredient = curRow, product = pproduct)
				product_ing.save()
			
			contents["messageType"] = 'success'
			contents["message"] = 'Produkt poprawnie dodany '
		
	return render(request,'manage_product_addedit.html',contents)

def product_edit(request,edit_id):
	contents = {'title':'Produkty', 'content':'', 'type': 'edit'}
	try:
		edit_id = int(edit_id)
	except:
		contents["messageType"] = 'danger'
		contents["message"] = 'Podany parametr jest nieprawidłowy'
		return render(request,"manage_product.html", display_product())
	###pobierz produkt z bazy ###
	try:
		pproduct = Product.objects.get(product_code=edit_id)
	except Product.DoesNotExist:
		contents["messageType"] = 'danger'
		contents["message"] = 'Ten produkt nie istnieje'
		return render(request,"manage_product.html", display_product())
	contents["id"] = pproduct.product_code
	contents["name"] = pproduct.product_name
	contents["price"] = pproduct.price
	contents["desc"] = pproduct.description
	contents["category"] = pproduct.category.cat_id
	if(pproduct.discount != None):
		contents["discount_id"] = pproduct.discount.id
	else:
		contents["discount_id"] = 0
	
	toDisp = []
	### Wyswietlanie formularza ###
	#pobierz kategorie główne
	categories = Product_Category.objects.all()
	if(categories.count() > 0): #przypisz do zmiennej
		for curRow in categories:
			if(curRow.parent == None):
				row = {'name':curRow.name, 'id':curRow.cat_id, 'demand':curRow.demand_ingredients }
				toDisp.append(row)
			contents["categories_count"]=categories.count()
			contents["categories"]=toDisp
	#pobierz składniki
	toDisp = []
	ingredients = Ingredient.objects.all()
	if(ingredients.count() > 0):
		for curRow in ingredients:
			row = {'name': curRow.name, 'units': curRow.units, 'id': curRow.id, 'price': curRow.price}
			if(Ingredient_Product.objects.filter(ingredient = curRow, product = pproduct).count() > 0):
				row["quantity"] = Ingredient_Product.objects.get(ingredient = curRow, product = pproduct).quantity
			else:
				row["quantity"] = 0.0
			toDisp.append(row)
			contents["ingredients"] = toDisp
			contents["ingredients_count"] = ingredients.count()
	#pobierz zniżki
	contents["discounts"] = display_discount()
	for curRow in contents["discounts"]["content"]:
		if(curRow["days"]!= ""):
			days = curRow["days"].split(', ');
			curRow["days"] = ""
			for r in days:
				if(r == "Poniedziałek"):
					curRow["days"] += "Pn"
				elif(r == "Wtorek"):
					curRow["days"] += "-"
					curRow["days"] += "Wt"
				elif(r == "Środa"):
					curRow["days"] += "-"
					curRow["days"] += "Śr"
				elif(r == "Czwartek"):
					curRow["days"] += "-"
					curRow["days"] += "Cz"
				elif(r == "Piątek"):
					curRow["days"] += "-"
					curRow["days"] += "Pt"
				elif(r == "Sobota"):
					curRow["days"] += "-"
					curRow["days"] += "Sb"
				else:
					curRow["days"] += "-"
					curRow["days"] += "Nd"
	###Wczytywanie danych ###
	if(request.POST.get('sent')):
		pname = request.POST.get('name')
		pprice = request.POST.get('price')
		try:
			pprice = float(pprice)
		except:
			contents["messageType"] = 'danger'
			contents["message"] = 'Nie prawidłowa cena produktu'
			return render(request,'manage_product_addedit.html',contents)
		if(pprice < 0 or pprice >= 1000):
			contents["messageType"] = 'danger'
			contents["message"] = 'Nie prawidłowa cena produktu'
			return render(request,'manage_product_addedit.html',contents)	
		pdesc = request.POST.get('description')
		pcat = request.POST.get('category')
		try:
			pcat = Product_Category.objects.get(cat_id=pcat)
		except Product_Category.DoesNotExist:
			contents["messageType"] = 'danger'
			contents["message"] = 'Nie istnieje taka kategoria'
			return render(request,'manage_product_addedit.html',contents)
		if(pcat.parent != None):
			contents["messageType"] = 'danger'
			contents["message"] = 'Produkt nie może należeć do tej kategorii'
			return render(request,'manage_product_addedit.html',contents)
		pdisc = request.POST.get('discount')
		try:
			pdisc = int(pdisc)
		except:
			contents["messageType"] = 'danger'
			contents["message"] = 'Nie poprawny parametr zniżki'
			return render(request,'manage_product_addedit.html',contents)
		if(pdisc == 0):
			pdisc = None
		elif(pdisc > 0):
			try:
				pdisc = Discount.objects.get(id=pdisc)
			except Discount.DoesNotExist:
				contents["messageType"] = 'danger'
				contents["message"] = 'Wybrana zniżka nie istnieje'
				return render(request,'manage_product_addedit.html',contents)	
		try:
			pproduct = Product.objects.get(product_code=edit_id)
		except Product.DoesNotExist:
			contents["messageType"] = 'danger'
			contents["message"] = 'Ten obiekt nie istnieje w bazie danych'
			return render(request,'manage_product.html',display_product())
		pproduct.product_name = pname
		pproduct.price = pprice
		pproduct.description = pdesc
		pproduct.discount = pdisc
		pproduct.category = pcat
		pproduct.save()
		contents["id"] = pproduct.product_code
		contents["name"] = pproduct.product_name
		contents["price"] = pproduct.price
		contents["desc"] = pproduct.description
		contents["category"] = pproduct.category.cat_id
		if(pproduct.discount != None):
			contents["discount_id"] = pproduct.discount.id
		else:
			contents["discount_id"] = 0
		#edycja istniejacych skladnikow, dodanie nowego jesli go nie ma
		pingredients = Ingredient.objects.filter(units="kg")
		for curRow in pingredients:
			#pobiera skladnik po nazwie
			name = curRow.name+"--"+str(curRow.id)
			value = request.POST.get(name)
			try:
				value = float(value)
			except:
				contents["messageType"] = 'danger'
				contents["message"] = 'Niepoprawna wartość parametru'
				pproduct.delete()
				return render(request,'manage_product_addedit.html',contents)
			if(value < 0 and value >= 1000):
				contents["messageType"] = 'danger'
				contents["message"] = 'Niepoprawna wartość parametru'
				pproduct.delete()
				return render(request,'manage_product_addedit.html',contents)
			#usun wszystkie i przypisz istniejace
			
			if(Ingredient_Product.objects.filter(ingredient = curRow, product = pproduct).count() > 0): #usun jesli jest taki wiersz
				toDel = Ingredient_Product.objects.get(ingredient = curRow, product = pproduct)
				toDel.delete()
			if(value > 0):
				product_ing = Ingredient_Product(quantity=value, ingredient = curRow, product = pproduct)
				product_ing.save()
			
			#aktualizacja tresci
			toDisp = []
			ingredients = Ingredient.objects.all()
			if(ingredients.count() > 0):
				for curRow in ingredients:
					row = {'name': curRow.name, 'units': curRow.units, 'id': curRow.id, 'price': curRow.price}
					if(Ingredient_Product.objects.filter(ingredient = curRow, product = pproduct).count() > 0):
						row["quantity"] = Ingredient_Product.objects.get(ingredient = curRow, product = pproduct).quantity
					else:
						row["quantity"] = 0.0
					toDisp.append(row)
					contents["ingredients"] = toDisp
					contents["ingredients_count"] = ingredients.count()
			contents["messageType"] = 'success'
			contents["message"] = 'Produkt poprawnie zapisany '
		
	return render(request,'manage_product_addedit.html',contents)
	
def product_delete(request, del_id):
	contents = display_product()
	try:
		del_id = int(del_id)
	except:
		contents["messageType"]= 'danger'
		contents["message"]= 'Nieprawidłowa wartość parametru'
		return render(request,"manage_product.html", contents)
	try:
		delProd = Product.objects.get(product_code=del_id)
	except Product.DoesNotExist:
		contents["messageType"]= 'danger'
		contents["message"]= 'Ten produkt nie istnieje'
		return render(request,"manage_product.html", contents)
		
	delProd.delete()
	contents = display_product()
	contents["messageType"]= 'success'
	contents["message"]= 'Poprawnie usunięto wybrany produkt'
	return render(request,"manage_product.html", contents)
	
	
def user_login(request):
	contents = {'title':'Logowanie', 'username':'', 'password':''} 
	c_username=request.POST.get('username')
	c_password=request.POST.get('password')
	users = User.objects.all()
	if(request.POST.get('sent')):
		c_password=hashlib.sha256(c_password.encode()).hexdigest()
		for c_user in users:
			if((c_user.username==str(c_username)) and (c_password==c_user.password)):
				contents = {'messageType':'success', 'message':'Zalogowano poprawnie!'}
				request.session['login_check']=c_user.user_id
				return render(request,'user_login.html',contents)
			else:
				contents = {'title':'Błąd!!!', 'messageType':'danger', 'message':'Podaj poprawną nazwę użytkownika i/lub hasło!', 'username':'', 'password':''}
	return render(request, 'user_login.html', contents)

def payment_types(request):
	payments = Payment_Type.objects.all()

	contents = {'title':'Płatności','messageType':'none', 'payments': payments}
	return render(request, 'manage_payment_types.html', contents)
	
def payment_types_delete(request, del_id):
	try:
		did = int(del_id)
	except ValueError:
		contents = {'title':'Płatności','messageType':'danger', 'message':'Taki element nie instnieje!'}
		return render(request, 'manage_payment_types.html', contents)
		
	toDel = Payment_Type.objects.filter(id=did)
	if(toDel.count() == 1):
		toDel[0].delete()
		return payment_types(request)
	elif(toDel.count() > 1):
		contents = {'title':'Płatności','messageType':'danger', 'message':'Nieznany błąd'}
	else:
		contents = {'title':'Płatności','messageType':'danger', 'message':'Taki element nie instnieje!'}

	return render(request, 'manage_payment_types.html', contents)
	
def payment_types_add(request):
	payments = Payment_Type.objects.all()
	payment_namex = request.POST.get('payment_name', False)
	
	contents = {'title':'Płatności','messageType':'none'}
	
	if(request.POST.get('sent')):
		if(payment_namex):
			if(not payment_namex == 'Nazwa płatności'):
				newPayment = Payment_Type(payment_name=payment_namex)
				newPayment.save()
				return payment_types(request)
			else:
				contents = {'title':'Płatności','messageType':'danger', 'message':'Błąd wprowadzania!'}
		else:
			contents = {'title':'Płatności','messageType':'danger', 'message':'Pole puste!'}
			
				
				
	return render(request, 'manage_payment_types_add.html', contents)

def user_management_edit(request, edit_id):
	check = user_check(request)
	if ('messageType' in check and check['messageType'] == 'danger'):
		return render(request, 'user_login.html', check)
	elif not check['canManage'] == True:
		return render(request, 'index.html', check)	
		
	try:
		eid = int(edit_id)
	except ValueError:
		contents = {'title':'Zarządzanie użytkownikami', 'type':'danger', 'content':'Podany użytkownik nie istnieje!'}
		return render(request, 'manage_magazine.html', contents)
		
	toEdit = User.objects.get(user_id=eid)	
	user_types = User_Type.objects.all()
	if(request.POST.get('sent')):
		reg_username = request.POST.get('username')
		reg_name = request.POST.get('name')
		reg_postal_code = request.POST.get('postal_code')
		reg_phone_number = request.POST.get('phone_number')
		reg_address = request.POST.get('address')
		reg_city = request.POST.get('city')
		reg_second_name = request.POST.get('second_name')
		reg_usertype = request.POST.get('usertype')
		contents = {'title':'Błąd!!!', 'messageType':'danger', 'usertypes': user_types, 'toEdit': toEdit, 'type': 'edit'}
		if not(re.match('[a-zA-ZćśźżńłóąęĆŚŹŻŃŁÓĄĘ]+$',str(reg_name))):
			contents['message'] = 'Niepoprawne imię!'
			return render(request,'manage_usermanagement_edit.html',contents)
		if not(re.match('[a-zA-ZćśźżńłóąęĆŚŹŻŃŁÓĄĘ]+$',str(reg_second_name))):
			contents['message'] ='Niepoprawne nazwisko!'
			return render(request,'manage_usermanagement_edit.html',contents)
		if not(re.match('[a-zA-ZćśźżńłóąęĆŚŹŻŃŁÓĄĘ]+$',str(reg_city))):
			contents['message'] = 'Niepoprawne miasto!'
			return render(request,'manage_usermanagement_edit.html',contents)
		if not(re.match('[0-9][0-9][0-9][0-9][0-9]',str(reg_postal_code))):
			contents['message'] = 'Niepoprawny kod pocztowy!'
			return render(request,'manage_usermanagement_edit.html',contents)
		if not(re.match('[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]',str(reg_phone_number))):
			contents['message'] = 'Niepoprawny numer telefonu!'
			return render(request,'manage_usermanagement_edit.html',contents)
		if (not(re.match('.{6,64}',str(reg_username)))):
			contents['message'] = 'Nazwa użytkownika musi mieć min 6 znaków i max 64 znaków!'
			return render(request,'manage_usermanagement_edit.html',contents)
		if (not(re.match('.{1,64}',str(reg_address)))):
			contents['message'] = 'Adres nie może być pusty!'
			return render(request,'manage_usermanagement_edit.html',contents)

		exist = False
		if not reg_usertype == 'user':
			if(User_Type.objects.filter(id=reg_usertype).count() == 1):
				exist = True
		elif reg_usertype == 'user':
			exist = True
				
		if not exist:
			contents['message'] = 'Nie ma takiego typu użytkownika!'
			contents['username'] = reg_username
			contents['name'] = reg_name	
			contents['second_name'] = reg_second_name	
			contents['city'] = reg_city	
			contents['phone_number'] = reg_phone_number	
			contents['address'] = reg_address	
			contents['postal_code'] = reg_postal_code				
			contents['type'] = 'editafail'				
			contents['typeid'] = reg_usertype
			return render(request,'manage_usermanagement_edit.html',contents)	
	
		users = User.objects.all()	
		for user in users:
			if(user.username == str(reg_username) and eid != user.user_id):
				contents['message'] = 'Nazwa użytkownika zajęta!'
				contents['username'] = toEdit.username
				contents['name'] = reg_name	
				contents['second_name'] = reg_second_name	
				contents['city'] = reg_city	
				contents['phone_number'] = reg_phone_number	
				contents['address'] = reg_address	
				contents['postal_code'] = reg_postal_code				
				contents['type'] = 'editafail'	
				contents['usertype'] = reg_usertype
				return render(request,'manage_usermanagement_edit.html',contents)	
				
		toEdit.name = reg_name
		toEdit.username = reg_username
		toEdit.second_name = reg_second_name
		toEdit.city = reg_city
		toEdit.phone_number = reg_phone_number
		toEdit.address = reg_address
		toEdit.postal_code = reg_postal_code
		if(reg_usertype == 'user'):
			toEdit.type_id = None
		else:
			toEdit.type_id = reg_usertype
		toEdit.save()	
		toEdit = User.objects.get(user_id=eid)	
		contents = {'title':'Zarządzanie użytkownikami','messageType':'success', 'message':'Edycja użytkownika powiodła się!', 'usertypes': user_types, 'toEdit': toEdit, 'type': 'edit'}
		return render(request, 'manage_usermanagement_edit.html', contents)
		
	contents = {'title':'Zarządzanie użytkownikami','messageType':'none', 'message':'none', 'usertypes': user_types, 'toEdit': toEdit, 'type': 'edit'}
	return render(request, 'manage_usermanagement_edit.html', contents)
	
def user_management(request):
	check = user_check(request)
	if ('messageType' in check and check['messageType'] == 'danger'):
		return render(request, 'user_login.html', check)
	elif not check['canManage'] == True:
		return render(request, 'index.html', check)	

	user_types = User_Type.objects.all()
	users = User.objects.all()
	
	for user in users:
		for type in user_types:
			if not user.type_id == None:
				if user.type_id == type.id:
					user.type_id = type.type_name
	
	contents = {'title':'Zarządzanie użytkownikami','messageType':'none', 'message':'none', 'users': users}
	return render(request, 'manage_usermanagement.html', contents)
	
def user_management_delete(request, del_id):
	check = user_check(request)
	if ('messageType' in check and check['messageType'] == 'danger'):
		return render(request, 'user_login.html', check)
	elif not check['canManage'] == True:
		return render(request, 'index.html', check)	
		
	user_types = User_Type.objects.all()
	users = User.objects.all()
	
	for user in users:
		for type in user_types:
			if user.type_id == type.id:
				user.type_id = type.type_name
				
	try:
		did = int(del_id)
	except ValueError:
		contents = {'title':'Zarządzanie użytkownikami','messageType':'danger', 'message':'Taki użytkownikk nie instnieje!', 'users': users}
		return render(request, 'manage_usermanagement.html', contents)
		
	toDel = User.objects.filter(user_id=did)
	iterator = -1
	if(toDel.count() == 1):
		toDel[0].delete()					
		users = User.objects.all()	
		for user in users:
			for type in user_types:
				if user.type_id == type.id:
					user.type_id = type.type_name					
		contents = {'title':'Zarządzanie użytkownikami','messageType':'success', 'message': 'Użytkownik usunięty poprawnie!', 'users': users}
		return render(request, 'manage_usermanagement.html', contents)
	elif(toDel.count() > 1):
		contents = {'title':'Zarządzanie użytkownikami','messageType':'danger', 'message':'Nieznany błąd', 'users': users}
	else:
		contents = {'title':'Zarządzanie użytkownikami','messageType':'danger', 'message':'Taki użytkownik nie instnieje!', 'users': users}
	
	return render(request, 'manage_usermanagement.html', contents)
	
def management_panel(request):
	check = user_check(request)
	if ('messageType' in check and check['messageType'] == 'danger'):
		return render(request, 'user_login.html', check)
	elif not check['canManage'] == True:
		return render(request, 'index.html', check)	
		
	contents = {'title':'Panel zarządzania','messageType':'none', 'message':'none'}	
	
	ingredients = Ingredient.objects.all()
	
	for element in ingredients:
		if element.quantity > element.min_quantity:
			contents = {'title':'Panel zarządzania','messageType':'alert', 'message':'none'}	
			return render(request, 'manage_management_panel.html', contents)
	
	return render(request, 'manage_management_panel.html', contents)