from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from . import views

urlpatterns = [
    path('', views.login_view, name='login_view'),
    path('signup', views.signup, name='signup'),
    path('logout',views.logout_view, name='logout_view'),
    path('main', views.main, name='main'),
]

urlpatterns += staticfiles_urlpatterns()