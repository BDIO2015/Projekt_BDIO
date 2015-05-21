#-*- coding: utf-8 -*-
from django.shortcuts import render
import re, hashlib
# Create your views here.
from django.http import HttpResponse
from .models import *

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
		reg_postal_code = request.POST.get('postal_code')
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
		if not(re.match('[0-9][0-9]-[0-9][0-9][0-9]',str(reg_postal_code))):
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
			row = {'name':curRow.name, 'desc':curRow.description,'type':curRow.get_type_display() , 'add_price':curRow.additional_price, 'parent':parent_name, 'id':curRow.cat_id, 'parent_id': parent_id}
			toDisp.append(row)
			contents = {'title':'Kategorie Produktów','count':product_categories.count(), 'content':toDisp}
	else:
		contents = {'title':'Kategorie Produktów', 'content':'Brak zdefiniowanych kategorii', 'count':0}
	return contents	
	
def product_category(request):
	return render(request, 'manage_product_category.html', display_product_category())

def product_category_add(request):
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
		cname =  request.POST.get('name', False);
		cdesc = request.POST.get('description', False);
		cadd_price = request.POST.get('additional_price', False);
		cparent = request.POST.get('parent', False);
		if(int(cparent) == 0):
			cparent = None
		else:
			cparent = Product_Category.objects.get(cat_id=cparent)
		ctype = request.POST.get('type', False);
		newCategory = Product_Category(name = cname, description = cdesc, additional_price = cadd_price, parent = cparent, type = ctype)
		newCategory.save()
		contents = {'title':'Kategorie Produktów', 'type': 'add', 'contents':'', 'parents':toDisp, 'messageType': 'success','message':'Dodano nową kategorię', 'count':product_categories.count()}
	else:
		contents = {'title':'Kategorie Produktów', 'type': 'add', 'contents':'', 'parents':toDisp, 'messageType': '', 'count':product_categories.count()}
	return render(request, 'manage_product_category_addedit.html', contents)

def product_category_edit(request, edit_id):
	contents = display_product_category()
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
	contents['ctype']=editCat.type
	contents['desc']=editCat.description
	contents['add_price']=editCat.additional_price
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
		cname =  request.POST.get('name', False);
		cdesc = request.POST.get('description', False);
		cadd_price = request.POST.get('additional_price', False);
		cparent = request.POST.get('parent', False);
		if(int(cparent) == 0):
			cparent = None
		else:
			cparent = Product_Category.objects.get(cat_id=cparent)
		ctype = request.POST.get('type', False);

		try:
			check = Product_Category.objects.get(cat_id=cid)
		except Product_Category.DoesNotExist:
			contents['messageType'] = 'danger'
			contents['message'] = 'Wystąpił nieoczekiwany błąd'
			return render(request, 'manage_product_category.html', contents)
		editCat.name = cname
		editCat.description = cdesc
		editCat.additional_price = cadd_price
		editCat.parent = cparent
		editCat.type = ctype
		editCat.save()
		contents = display_product_category()
		contents['messageType'] = 'success'
		contents['message'] = 'Kategoria poprawnie zapisana'
		return render(request, 'manage_product_category.html', contents)
	return render(request, 'manage_product_category_addedit.html', contents)

def product_category_delete(request, del_id):
	contents = display_product_category()
	try:
		delete = int(del_id)
	except ValueError:
		contents['messageType'] = 'danger'
		contents['message'] = 'Podano niepoprawny numer kategorii'
		return render(request, 'manage_product_category.html', contents)
	try:
		delCat = Product_Category.objects.get(cat_id=delete)
	except User_Type.DoesNotExist:
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
	ingredients = Ingredient.objects.all()
	
	contents = {'ingredients': ingredients, 'title': "Magazyn", 'messageType':'None'}
	return render(request, 'manage_magazine.html', contents)
	
def magazine_add(request):
	ingredients = Ingredient.objects.all()

	if(request.POST.get('sent')):		
		ingredient_name = request.POST.get('ingredient_name', False);
		quantityx = request.POST.get('count', False);
		min_quantityx = request.POST.get('min_count', False)
		pricex = request.POST.get('price', False)
		unitsx = request.POST.get('units', False)
		
		ingredient_name = str(ingredient_name)
		if re.match('^[a-zA-Zćśźżńłóąę ]+$',ingredient_name) and ingredient_name != "Nazwa składnika": 	
			

			if(pricex.count(",") > 1 or pricex.count(".") > 1 or quantityx.count(",") > 1 or quantityx.count(".") > 1 or min_quantityx.count(",") > 1 or min_quantityx.count(".") > 1):
				contents = {'title': "Magazyn", 'result':'Błędna/e wartości cena, ilość, min. ilość!', 'type': 'add'}		
				return render(request, 'manage_magazine_addedit.html', contents)
			
			for ingredient in ingredients:
				if(ingredient.name == ingredient_name):		
					contents = {'title': "Magazyn", 'result':'Składnik o takiej nazwie już istnieje!'}		
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
			
			return magazine(request)
			
		else:	
			contents = {'title': "Magazyn", 'messageType':'none', 'result': 'Niepoprawna nazwa składnika!', 'type': 'add'}
	else:
		contents = {'title': "Magazyn", 'messageType':'none', 'type': 'add'}
		
	return render(request, 'manage_magazine_addedit.html', contents)	

def magazine_edit(request, edit_id):
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
			if re.match('^[a-zA-Zćśźżńłóąę ]+$',ingredient_name) and ingredient_name != "Nazwa składnika": 	
				

				if(pricex.count(",") > 1 or pricex.count(".") > 1 or quantityx.count(",") > 1 or quantityx.count(".") > 1 or min_quantityx.count(",") > 1 or min_quantityx.count(".") > 1):
					contents = {'title': "Magazyn", 'result':'Błędna/e wartości cena, ilość, min. ilość!'}		
					return render(request, 'manage_magazine_addedit.html', contents)
				
				for ingredient in ingredients:
					if(ingredient.name == ingredient_name and ingredient.id != eid):		
						contents = {'title': "Magazyn", 'result':'Składnik o takiej nazwie już istnieje!'}		
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
				
				return magazine(request)
				
			else:	
				contents = {'title': "Magazyn", 'messageType':'none', 'result': 'Niepoprawna nazwa składnika!', 'type': 'edit', 'toEdit': toEdit }
	else:	
		contents = {'title': "Magazyn", 'messageType':'danger', 'message': 'Podany element nie istnieje!', 'type': 'edit', 'toEdit': toEdit}
		
	return render(request, 'manage_magazine_addedit.html', contents)
	
def magazine_delete(request, del_id):
	try:
		did = int(del_id)
	except ValueError:
		contents = {'title':'Magazyn','messageType':'danger', 'message':'Taki element nie instnieje!'}
		return render(request, 'manage_magazine.html', contents)
		
	toDel = Ingredient.objects.filter(id=did)
	if(toDel.count() == 1):
		toDel[0].delete()
		return magazine(request)
	elif(toDel.count() > 1):
		contents = {'title':'Magazyn','messageType':'danger', 'message':'Nieznany błąd'}
	else:
		contents = {'title':'Magazyn','messageType':'danger', 'message':'Taki element nie instnieje!'}

	return render(request, 'manage_magazine.html', contents)

def basket(request):
	contents = {'title':'Koszyk'}
	if('basket_products' in request.session):
		contents['messageType'] = 'success'
		contents['message'] = request.session['basket_products']
	else:
		contents['messageType'] = 'danger'
		contents['message'] = 'Koszyk jest pusty'
	return render(request, 'basket.html', contents)
	
def basket_add(request, product_id):
	contents = {'title':'Dodaj do koszyka'}
	product_id = int(product_id)
	'''try:
		check = Product.objects.get(product_code=product_id)
	except Product.DoesNotExist:
		contents['messageType'] = 'danger'
		contents['message'] = 'Wybranego produktu nie ma w bazie'
		return render(request, 'basket.html', contents)'''
	categories = Product_Category.objects.filter(parent=None) #dodac pobieranie po id z produktow
	subcategories = {}
	for cat in categories:
		if(cat.type == '2'):
			subcategory = Product_Category.objects.filter(parent=cat.cat_id)
			subcategories[cat.name] = []
			for subcat in subcategory:
				if(subcat.type == '2'):
					subsubcat = Product_Category.objects.filter(parent=subcat.cat_id)
					subcategories[subcat.name] = []
					for curcat in subsubcat:
						subcategories[subcat.name].append(curcat.name) 
				else:
					subcategories[cat.name].append(subcat.name)
	for key, each in subcategories.iteritems():
		if(len(each) == 0):
			del subcategories[key]
			break
	if(request.POST.get('sent', False)):
		pingreds = request.POST.getlist('basket_products_ingredients', [])
		pingreds.sort()
		premarks = request.POST.get('basket_products_remarks', '')
		premarks = premarks.replace(':', ' ').replace(';', ' ')
		selections = request.POST.getlist('selections', [])
		selections.sort()
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
					prod_in = unpack[3+len(subcategories):]
					prod_in.sort()
					cat_in = unpack[3:3+len(subcategories)]
					cat_in.sort()
					if(prod_in == pingreds and premarks == unpack[2] and cat_in == selections):
						amount += 1
						products.remove(curProd)
						unpack[1] = str(amount)
						packed = ':'.join(unpack)
						products.append(packed)
						request.session['basket_products'] = ';'.join(products)
						contents['messageType'] = 'success'
						contents['message'] = 'Dodano wybrany produkt do koszyka'
						return render(request, 'basket.html', contents)
			forStr = ';' + str(product_id) + ':1' + ':' + premarks
			if(len(selections) > 0):
				forStr += ':' + ':'.join(selections)
			if(len(pingreds) > 0):
				forStr += ':' + ':'.join(pingreds)
			request.session['basket_products'] += forStr
		else:
			forStr = str(product_id) + ':1' + ':' + premarks
			if(len(selections) > 0):
				forStr += ':' + ':'.join(selections)
			if(len(pingreds) > 0):
				forStr += ':' + ':'.join(pingreds)
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
	#wczytac nazwe produktu z id
	#dodac wybieranie podkategorii produktu
	contents['name'] = 'Nazwa produktutt' # check.product_name
	contents['categories'] = subcategories
	contents['id'] = product_id
	return render(request, 'basket_step2.html', contents)
def basket_remove(request, product_id):
	contents = {'title':'Usuń z koszyka'}
	product_id = int(product_id)
	if('basket_products' in request.session):
		products = request.session['basket_products'].split(';')
		for curProd in products:
			unpack = curProd.split(':')
			try:
				id = int(unpack[0])
			except ValueError:
				contents['messageType'] = 'danger'
				contents['message'] = 'Nieznany błąd'
				return render(request, 'basket.html', contents)
			if(id == product_id):
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