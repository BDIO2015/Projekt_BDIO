#-*- coding: utf-8 -*-
from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from .models import Discount

def index(request):
	contents = {'title':'Testujemy', 'question':'test'}
	return render(request, 'index.html', contents)
	
def manage(request):
	contents = {'title':'Testujemy2', 'question':'test2'}
	return render(request, 'manage.html', contents)
	
def discount(request):
	discounts = Discount.objects.all()
	if(discounts.count() > 0):
		mainContent = 'test'
	else:
		mainContent = 'Brak zdefiniowanych zniżek'
	contents = {'title':'Zniżki', 'content':mainContent}
	return render(request, 'manage.html', contents)
	
def discount_add(request):
	#TODO dodac sprawdzenie czy zalogowany i ma uprawnienia
	isSent = request.POST.get('sent', False);
	mainContent = '';
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
			try:
				sHour = int(sHour)
			except ValueError:
				sHour = 8
			sMinutes = request.POST.get('sminutes', False);
			try:
				sMinutes = int(sMinutes)
			except ValueError:
				sMinutes = 0
			eHour = request.POST.get('ehour', False);
			try:
				eHour = int(eHour)
			except ValueError:
				eHour = 12
			eMinutes = request.POST.get('eminutes', False);
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
			newDisc = Discount(type=typeFormat, value=disc)
			newDisc.save()
			mainContent = 'Inserted'
		else:
			mainContent = 'Nie wybrano żadnego dnia'
	contents = {'title':'Zniżki', 'type':'add', 'content':mainContent}
	return render(request, 'manage_addedit.html', contents)
