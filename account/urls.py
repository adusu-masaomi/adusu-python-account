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
    url(r'^payment/report_1/$', views.pdf_payment_list.payment_list_1, name='payment_list_1'),    #支払集計表1
    url(r'^payment/report_2/$', views.pdf_payment_list.payment_list_2, name='payment_list_2'),    #支払集計表2(提示用)
    url(r'^payment/data_transfer_1/$', views.data_transfer.automake_payment, name='payment_data_transfer'),    #データ移行
    url(r'^payment/data_transfer_2/$', views.data_transfer.delete_all_payment, name='payment_data_delete'),    #データ一括削除
    #出納帳
    url(r'^cash_book/$', views.views.cash_book_list, name='cash_book_list'),   # 一覧
    url(r'^cash_book/add/$', views.views.cash_book_edit, name='cash_book_add'),  # 登録
    url(r'^cash_book/mod/(?P<cash_book_id>\d+)/$', views.views.cash_book_edit, name='cash_book_mod'),  # 修正
    url(r'^cash_book/del/(?P<cash_book_id>\d+)/$', views.views.cash_book_del, name='cash_book_del'),   # 削除
    url(r'^cash_book/set_weekly_1/$', views.aggregate_weekly.set_weekly, name='set_weekly'),    #週末データ手動作成
    url('cash_book_sort/', views.ajaxs.ajax_cash_book_sort, name='cash_book_sort'),                        #ajax
    url(r'^cash_book/report_1/$', views.pdf_cash_book.list_1, name='cash_book_list_1'),    #出納帳
    url(r'^cash_book/report_2/$', views.pdf_cash_book.list_2, name='cash_book_list_2'),    #集計表(抽出用)
    url(r'^cash_book/cash_book_export_1/$', views.export_csv.cash_book_export, name='cash_book_export'),     #csv
    url(r'^cash_book/cash_book_export_extract_1/$', views.export_csv.cash_book_export_extract, name='cash_book_export_extract'),     #csv
    url(r'^cash_book/cash_book_training_account_title_1/$', views.machine_learning.training_account_title, name='training_account_title'),     #機械学習
    url('predict_account_tile/', views.ajaxs.ajax_cash_book_predict_account_tile, name='predict_account_tile'),   #ajax
    #週末データ
    url(r'^cash_book_weekly/$', views.views.cash_book_weekly_list, name='cash_book_weekly_list'),   # 一覧
    url(r'^cash_book_weekly/add/$', views.views.cash_book_weekly_edit, name='cash_book_weekly_add'),  # 登録
    url(r'^cash_book_weekly/mod/(?P<cash_book_weekly_id>\d+)/$', views.views.cash_book_weekly_edit, name='cash_book_weekly_mod'),  # 修正
    url(r'^cash_book_weekly/del/(?P<cash_book_weekly_id>\d+)/$', views.views.cash_book_weekly_del, name='cash_book_weekly_del'),   # 削除
    
]