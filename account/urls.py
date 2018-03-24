from django.conf.urls import url, include, patterns
from account import views
#import account

app_name = 'account'

urlpatterns = [
    #メニュー
	url(r'^index/$', views.views.index, name='index'),   # メニュー
	# 取引先
    url(r'^partner/$', views.views.partner_list, name='partner_list'),   # 一覧
    url(r'^partner/add/$', views.views.partner_edit, name='partner_add'),  # 登録
    url(r'^partner/mod/(?P<partner_id>\d+)/$', views.views.partner_edit, name='partner_mod'),  # 修正
    url(r'^partner/del/(?P<partner_id>\d+)/$', views.views.partner_del, name='partner_del'),   # 削除
    url('bank_select/', views.ajaxs.ajax_bank_branch_extract, name='bank_branch_extract'),   #ajax
    url('partner_sort/', views.ajaxs.ajax_partner_sort, name='partner_sort'),                #ajax
    # 勘定科目
    url(r'^account_title/$', views.views.account_title_list, name='account_title_list'),   # 一覧
    url(r'^account_title/add/$', views.views.account_title_edit, name='account_title_add'),  # 登録
    url(r'^account_title/mod/(?P<account_title_id>\d+)/$', views.views.account_title_edit, name='account_title_mod'),  # 修正
    url(r'^account_title/del/(?P<account_title_id>\d+)/$', views.views.account_title_del, name='account_title_del'),   # 削除
    url('account_title_sort/', views.ajaxs.ajax_account_title_sort, name='account_title_sort'),                #ajax
    #銀行
    url(r'^bank/$', views.views.bank_list, name='bank_list'),   # 一覧
    url(r'^bank/add/$', views.views.bank_edit, name='bank_add'),  # 登録
    url(r'^bank/mod/(?P<bank_id>\d+)/$', views.views.bank_edit, name='bank_mod'),  # 修正
    url(r'^bank/del/(?P<bank_id>\d+)/$', views.views.bank_del, name='bank_del'),   # 削除
    url('bank_sort/', views.ajaxs.ajax_bank_sort, name='bank_sort'),                #ajax
    #銀行支店
    url(r'^bank_branch/$', views.views.bank_branch_list, name='bank_branch_list'),   # 一覧
    url(r'^bank_branch/add/$', views.views.bank_branch_edit, name='bank_branch_add'),  # 登録
    url(r'^bank_branch/mod/(?P<bank_branch_id>\d+)/$', views.views.bank_branch_edit, name='bank_branch_mod'),  # 修正
    url(r'^bank_branch/del/(?P<bank_branch_id>\d+)/$', views.views.bank_branch_del, name='bank_branch_del'),   # 削除
    url('bank_branch_sort/', views.ajaxs.ajax_bank_branch_sort, name='bank_branch_sort'),                #ajax
    #支払
    url(r'^payment/$', views.views.payment_list, name='payment_list'),   # 一覧
    url(r'^payment/add/$', views.views.payment_edit, name='payment_add'),  # 登録
    url(r'^payment/mod/(?P<payment_id>\d+)/$', views.views.payment_edit, name='payment_mod'),  # 修正
    url(r'^payment/del/(?P<payment_id>\d+)/$', views.views.payment_del, name='payment_del'),   # 削除
    url('partner_select/', views.ajaxs.ajax_partner_extract, name='partner_extract'),   #ajax
    url('payment_sort/', views.ajaxs.ajax_payment_sort, name='payment_sort'),                #ajax
    url(r'^payment/report_1/$', views.pdf_payment_list.payment_list_1, name='payment_list_1'),    #支払集計表
    url(r'^payment/data_transfer_1/$', views.data_transfer.automake_payment, name='payment_data_transfer'),    #データ移行
    url(r'^payment/data_transfer_2/$', views.data_transfer.delete_all_payment, name='payment_data_delete'),    #データ一括削除
]