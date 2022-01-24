from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.forms import ModelForm,ModelMultipleChoiceField
from django import forms

from .models import *

class DateInput(forms.DateInput):
    input_type = 'date'

class TaskForm(ModelForm):
    def __init__(self,request_user,*args,**kwargs):
        super (TaskForm,self).__init__(*args,**kwargs)
        self.fields['category'].queryset = Category.objects.filter(doer=request_user)

    class Meta:
        model = Task
        fields = ['description','category','deadline','edit_mode']
        widgets = {
            'deadline': DateInput(),
            'description': forms.TextInput(attrs={'autocomplete':'off'}),
            'edit_mode':forms.HiddenInput(),
        }

class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'autocomplete':'off'}),
        }

class TaskListForm(forms.Form):
    tasks = ModelMultipleChoiceField(queryset=Task.objects.filter(category__isnull=True,complete=False))

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
        if request.method=='POST':
            form = forms.Form(request.POST)
            if form.is_valid():
                if request.POST.get("task"):
                    task_id = request.POST.get("task")
                    task_to_complete = Task.objects.get(id=int(task_id))
                    task_to_complete.complete=True
                    task_to_complete.save()
                elif request.POST.get("delete"):
                    task_id = request.POST.get("delete")
                    Task.objects.get(id=int(task_id)).delete()
                
                return HttpResponseRedirect(reverse('main'))
            else:
                return render(request,'todo/main.html', {
                        'categories': Category.objects.filter(doer=request.user)[:3],
                        'active_tasks': Task.objects.filter(doer=request.user,complete=False),
                        'message':'Sorry, something went wrong!'
                    })

        return render(request,'todo/main.html', {
                'categories': Category.objects.filter(doer=request.user)[:3],
                'active_tasks': Task.objects.filter(doer=request.user,complete=False),
            })
    else:
        return HttpResponseRedirect(reverse('login_view'))

def category_view(request,category_id):
    category = Category.objects.get(id=category_id) 
    return render(request,'todo/category.html',{
            "category_name":category.name,
            "active_tasks":Task.objects.filter(category=category,complete=False),
            "categories":Category.objects.filter(doer=request.user)[:3],
        })

def new_task(request):
    if request.method=='POST':
        form = TaskForm(request.user,request.POST)
        if form.is_valid():

            task_description = form.cleaned_data['description']
            category = form.cleaned_data['category']
            deadline = form.cleaned_data['deadline']

            if form.cleaned_data['edit_mode']:
                task_id = int(request.POST.get('edit'))
                edited_task = Task.objects.get(id=task_id)

                edited_task.description = task_description
                edited_task.category = category
                edited_task.deadline = deadline

                edited_task.save()
            else:
                doer = request.user

                new_user_task = Task(description=task_description,doer=doer,deadline=deadline)

                if category:
                    new_user_task = Task(description=task_description,category=category,doer=doer,deadline=deadline)
                else:
                    new_user_task = Task(description=task_description,doer=doer,deadline=deadline)

                new_user_task.save()
                
            return HttpResponseRedirect(reverse('main'))

        else:
            return render(request,'todo/new_task.html',{
                    'task_form':form,
                })         

    return render(request,'todo/new_task.html',{
            'task_form':TaskForm(request.user),
            'categories':Category.objects.filter(doer=request.user)[:3],
        })

def edit_task(request):
    task_id = int(request.POST.get('edit'))
    task = Task.objects.get(id=task_id)
    edit_form = TaskForm(request.user,initial = {'description':task.description,
                                    'category':task.category,'deadline':task.deadline,
                                    'edit_mode':True})

    return render(request,'todo/new_task.html', {
            'task_form':edit_form,
            'edit_mode':True,
            'task_id':task_id,
            'categories':Category.objects.filter(doer=request.user)[:3],
        })
    

def new_category(request):
    if request.method=='POST':
        tasks_form = TaskListForm(request.POST)
        category_form = CategoryForm(request.POST)
        if category_form.is_valid():
            category_name = category_form.cleaned_data['name']

            if Category.objects.filter(name__icontains = category_name):
                return render(request,'todo/new_category.html',{
                        'message':'Such category already exists',
                        'category_form':category_form,
                        'tasks_form':tasks_form
                    })

            category_new = Category(name=category_name,
                                        doer = request.user)
            category_new.save()

            if tasks_form.is_valid():
                for task in tasks_form.cleaned_data['tasks']:
                    task.category = category_new
                    task.save()

            return HttpResponseRedirect(reverse('main'))
 
        else:
            return render(request,'todo/new_category.html',{
                    'message':'Error',
                    'category_form':category_form,
                    'tasks_form':tasks_form
                })

    return render(request,'todo/new_category.html',{
            'category_form':CategoryForm(),
            'tasks_form':TaskListForm(),
            'tasks_available':Task.objects.filter(complete=False,category__isnull=True).count(),
            'categories':Category.objects.filter(doer=request.user)[:3],
        })

def all_categories(request):
    if request.method == 'POST':
        if request.POST.get("delete"):
            category_id = int(request.POST.get("delete"))
            Category.objects.get(id=category_id).delete()

            return HttpResponseRedirect(reverse('all_categories'))
        else:
            return render(request,'todo/all_categories.html', {
                     'categories':Category.objects.filter(doer=request.user),
                })

    return render(request,'todo/all_categories.html',{
            'categories':Category.objects.filter(doer=request.user),
        })

def complete(request):
    if request.method == 'POST':
        if request.POST.get("delete"):
            task_id = int(request.POST.get("delete"))
            Task.objects.get(id=task_id).delete()

            return HttpResponseRedirect(reverse('complete'))
        else:
            return render(request,'todo/complete.html', {
                    'complete_tasks':Task.objects.filter(doer=request.user,complete=True),
                    'categories':Category.objects.filter(doer=request.user)[:3],
                })

    return render(request,'todo/complete.html',{
            'complete_tasks':Task.objects.filter(doer=request.user,complete=True),
            'categories':Category.objects.filter(doer=request.user)[:3],
        })

