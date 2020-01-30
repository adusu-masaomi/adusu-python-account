"""
Django settings for adusu project.

Generated by 'django-admin startproject' using Django 1.9.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os
#CentOsなら以下は不要
from pymysql import install_as_MySQLdb
install_as_MySQLdb()
#

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#ログイン用
LOGIN_ERROR_URL = '/account/login'
LOGIN_URL = '/account/login/'
LOGIN_REDIRECT_URL = '/account/index/'
AUTH_USER_MODEL = 'account.AuthUser'
#

#CentOS用
#LOGIN_ERROR_URL = '/django/account/login'
#LOGIN_URL = '/django/account/login/'
#LOGIN_REDIRECT_URL = '/django/account/index/'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'o^-a@)9ortg9mi8b5w@0sl3+sl0uqvqr!t^%ew)f3)l(p-x9%9'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

INTERNAL_IPS = ('127.0.0.1',)

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'bootstrapform',  # django-bootstrap-form
    'account', #←追加
    'debug_toolbar',
    'crispy_forms',
    'datetimewidget',
    'sorting_bootstrap',
    'webstack_django_sorting',
    'template_debug',
]



#INSTALLED_APPS += ('crispy_forms', )
CRISPY_TEMPLATE_PACK = 'bootstrap3'

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

#centOsはこれがないとエラーになる
MIDDLEWARE = [
    # ...
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    # ...
]

#各ページのキャッシュ時間を秒単位で指定
#CACHE_MIDDLEWARE_SECONDS = 60 * 1440   #24時間
#CACHE_MIDDLEWARE_KEY_PREFIX = 'bbs'    #複数のサイト間でキャッシュを共有する場合

ROOT_URLCONF = 'adusu.urls'

#グローバル変数用

#ヌルの場合の記号（デフォルトはNone）
EMPTY_MARK = '-'
#支払方法のID
ID_PAYMENT_METHOD_TRANSFER = 1    #振込
ID_PAYMENT_METHOD_WITHDRAWAL = 2  #引落
ID_PAYMENT_METHOD_CASH = 4  #現金
#社員ID
ID_STAFF_PRESIDENT = 1 #社長

#銀行マスターのID(ADUSUの取扱銀行・資金繰りで使用)
ID_BANK_HOKUETSU = 1
ID_BANK_SANSHIN = 2
#銀行支店
ID_BANK_BRANCH_SANSHIN_MAIN = 19  #三信本店の支店ID

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')], # ←← ここの中身を追加
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'account.context_processors.empty_mark_info',
                'account.context_processors.payment_method_transfer_info',
                'account.context_processors.payment_method_withdrawal_info',
            ],
        },
    },
]

#↑CentOsの場合は↓これも加えておく(STATIC_DIRが有効になる)
#'django.template.context_processors.static', 

WSGI_APPLICATION = 'adusu.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'adusu_db',
        'USER': 'adusu',
        'PASSWORD': 'Adusu2016%',
        'HOST': '',
        'PORT': '',
    }
}
def mysqldb_escape(value, conv_dict):
    from pymysql.converters import encoders
    vtype = type(value)
    # note: you could provide a default:
    # PY2: encoder = encoders.get(vtype, escape_str)
    # PY3: encoder = encoders.get(vtype, escape_unicode)
    encoder = encoders.get(vtype)
    return encoder(value)

#CentOsの場合は以下は不要
import pymysql
setattr(pymysql, 'escape', mysqldb_escape)
del pymysql

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

#LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = 'ja'

#TIME_ZONE = 'UTC'
TIME_ZONE = 'Asia/Tokyo'


USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

#プロジェクトのルートをSITE_ROOTとする
#SITE_ROOT = abspath(os.path.join(dirname(__file__),".."))

STATIC_URL = '/static/'

#CentOS用
#STATIC_URL = '/django/static/'

# 静的ファイルを共通で置く
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)

#学習ファイルのパス（macとcentosで異なる)
#for mac
DIR_VECT_CASH_BOOK = 'static/data/vect.pkl'
DIR_CLF_CASH_BOOK = 'static/data/clf.pkl'
#for centOS
#DIR_VECT_CASH_BOOK = '/var/www/work_py/adusu/static/data/vect.pkl'
#DIR_CLF_CASH_BOOK = '/var/www/work_py/adusu/static/data/clf.pkl'
#

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TEMPLATE_CONTEXT': True,
}

