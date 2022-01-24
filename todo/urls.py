from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from . import views

urlpatterns = [
    path('', views.login_view, name='login_view'),
    path('signup', views.signup, name='signup'),
    path('logout',views.logout_view, name='logout_view'),
    path('main', views.main, name='main'),
    path('new_task',views.new_task,name='new_task'),
    path('edit_task',views.edit_task,name='edit_task'),
    path('new_category',views.new_category,name='new_category'),
    path('all_categories',views.all_categories,name='all_categories'),
    path('complete',views.complete,name='complete'),
    path('<int:category_id>',views.category_view,name='category_view'),
]

urlpatterns += staticfiles_urlpatterns()