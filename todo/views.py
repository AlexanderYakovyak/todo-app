from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.forms import ModelForm
from django import forms

from .models import *

def login_view(request):
    if request.method=='POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request,user)
            return HttpResponseRedirect(reverse('main'))
        else:
            return render(request,'todo/login.html', {
                    'message':'Invalid password or username'
                })
    return render(request,'todo/login.html')


def signup(request):
    if request.method=='POST':
        username = request.POST['username']
        email = request.POST['email']
        
        password = request.POST['password']
        confirmation_password = request.POST['conf_password']

        if password!=confirmation_password:
            return render(request,'todo/signup.html',{
                    'message':'Passwords do not match. Try again.'
                })

        try:
            user = User.objects.create_user(username,email,password)
        except IntegrityError:
            return render(request,'todo/singup.html',{
                    'message':'User with such username already exists.'
                })
        return HttpResponseRedirect(reverse('main'))
    else:
        return render(request,'todo/singup.html')

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('login_view'))

def main(request):
    if request.user.is_authenticated:
        return render(request,'todo/main.html')
    else:
        return HttpResponseRedirect(reverse('login'))

