"""adusu URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include   # ←, includeを追加
from django.contrib import admin
from account import views #←追加
#import account
from django.conf import settings

#画面認証用
from django.contrib.auth.views import login, logout_then_login
from account.views.views import Index
#from account.views.views import PasswordAuth1  #add220826

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^account/login/$', login, {'template_name': 'account/login.html'}, name='login'),
    url(r'^account/logout/$', logout_then_login, name='logout'),
    url(r'^account/index/$', Index.as_view(), name='account_index'),
    url(r'^adusu/index', views.views.index),  #←追加
    url(r'^account/', include('account.urls', namespace='account')),

    #url(r'^account/password_auth_1/$', PasswordAuth1.as_view(), name='password_auth_1'),
    #url(r'^account/password_auth_1', views.views.password_auth_1),
    
    #url(r'^select2/', include('django_select2.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += (
        url(r'^account/', include(debug_toolbar.urls)),
    )
