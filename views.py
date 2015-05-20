#-*- coding: utf-8 -*-
from django.shortcuts import render
import re
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
	contents = {'title':'Rejestracja', 'name':'', 'second_name':'', 'address':'', 'city':'', 'postal_code':'', 'phone_number':'', 'username':''}
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
		if not((len(str(reg_password)) > 5) or (len(str(reg_password))) < 64):
				contents = {'title':'Błąd!!!', 'messageType':'danger', 'message':'Hasło musi mieć min 6 znaków i max 64 znaków!', 'name':str(reg_name), 'second_name':str(reg_second_name), 'address':str(reg_address), 'city':str(reg_city), 'postal_code':str(reg_postal_code), 'phone_number':str(reg_phone_number), 'username':str(reg_username)}
				return render(request,'user_register.html',contents)
		users = User.objects.all()
		for user in users:
			if(user.username == str(reg_username)):
				contents = {'title':'Błąd!!!', 'messageType':'danger', 'message':'Nazwa użytkownika zajęta!', 'name':str(reg_name), 'second_name':str(reg_second_name), 'address':str(reg_address), 'city':str(reg_city), 'postal_code':str(reg_postal_code), 'phone_number':str(reg_phone_number), 'username':''}	
				return render(request,'user_register.html',contents)	
		good=1
		if good:
			##DOPOKI NIE MA TYPE I SCHEDULE, TRZEBA ZEZWOLIC CHWILOWO NA NULL!, PRZYJMUJEMY ZE UZYTKOWNICY ZE ZWYKLEGO REGISTER DOSTAJA SCHEDULE 0 CZYLI BRAK BO TO KLIENCI, TYP 0, ZMIANA TYPU MOZLIWA PRZEZ PANEL ADMINA KTORY KTOS ZROBI##
			newUser = User(name=reg_name, second_name=reg_second_name, username=reg_username, password=reg_password, postal_code=reg_postal_code, phone_number=reg_phone_number, city=reg_city, address=reg_address)
			newUser.save()
			contents = {'messageType':'success', 'message':'Użytkownik zarejestrowany','name':'', 'second_name':'', 'address':'', 'city':'', 'postal_code':'', 'phone_number':'', 'username':''}
	return render(request, 'user_register.html', contents)

def product_category(request):
	product_categories = Product_Category.objects.all()
	contents = {'title':'Kategorie Produktów', 'content':''}
	if(product_categories.count() > 0):
		toDisp = []
		for curRow in product_categories:
			if(curRow.parent != None):
				parent_name = curRow.parent.name
			else:
				parent_name = "-"
			row = {'name':curRow.name, 'desc':curRow.description,'type':curRow.get_type_display() , 'add_price':curRow.additional_price, 'parent':parent_name, 'id':curRow.cat_id}
			toDisp.append(row)
			contents = {'title':'Kategorie Produktów','count':product_categories.count(), 'content':toDisp}
	else:
		contents = {'title':'Kategorie Produktów', 'content':'Brak zdefiniowanych kategorii', 'count':0}
	return render(request, 'manage_product_category.html', contents)

def product_category_add(request):
	product_categories = Product_Category.objects.all()
	toDisp = []
	if(product_categories.count() > 0):
		for curRow in product_categories:
			row = {'name':curRow.name, 'id':curRow.cat_id}
			toDisp.append(row)
			contents = {'title':'Kategorie Produktów','count':product_categories.count(), 'content':toDisp}
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
		contents = {'title':'Kategorie Produktów', 'type': 'add', 'contents':toDisp, 'messageType': 'success','message':'Dodano nową kategorię', 'count':product_categories.count()}
	else:
		contents = {'title':'Kategorie Produktów', 'type': 'add', 'contents':toDisp, 'messageType': '', 'count':product_categories.count()}
	return render(request, 'manage_product_category_addedit.html', contents)
	
	
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
			manage = "Nie"
			if(curRow.canManage == 1):
				manage = "Tak"
			row = {'name':curRow.type_name, 'add':add,'edit':edit , 'delete':delete, 'manage':manage, 'id':curRow.id}
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
		manage = request.POST.get('manage', False)
		if(len(name) < 3):
			contents['messageType'] = 'danger'
			contents['message'] = 'Nazwa nie może być krótsza niż 3 znaki'
			return render(request, 'manage_user_type_addedit.html', contents)
		try:
			check = User_Type.objects.get(type_name=name)
		except User_Type.DoesNotExist:
			toSave = User_Type(type_name=name, canCreate=create, canEdit=edit, canDelete=delete, canManage=manage)
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
	contents['manage']=user.canManage
	if(request.POST.get('sent', False)):
		name = request.POST.get('name', False)
		create = request.POST.get('create', False)
		edit = request.POST.get('edit', False)
		delete = request.POST.get('delete', False)
		manage = request.POST.get('manage', False)
		if(len(name) < 3):
			contents['messageType'] = 'danger'
			contents['message'] = 'Nazwa nie może być krótsza niż 3 znaki'
			return render(request, 'manage_user_type_addedit.html', contents)
		try:
			check = User_Type.objects.get(type_name=name)
		except User_Type.DoesNotExist:
			user.type_name = name
			user.canCreate = create
			user.canEdit = edit
			user.canDelete = delete
			user.canManage = manage
			user.save()
			contents = display_user_type()
			contents['messageType'] = 'success'
			contents['message'] = 'Typ został zmieniony'
			return render(request, 'manage_user_type.html', contents)
		contents['messageType'] = 'danger'
		contents['message'] = 'Nazwa jest już używana'
	return render(request, 'manage_user_type_addedit.html', contents)