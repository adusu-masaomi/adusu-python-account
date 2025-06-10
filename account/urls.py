from django.conf.urls import url, include, patterns
from account import views
#import account

app_name = 'account'

urlpatterns = [
    #メニュー
	url(r'^index/$', views.views.index, name='index'),   # メニュー
    #
    # マスター管理
    # 取引先
    url(r'^partner/$', views.views.partner_list, name='partner_list'),   # 一覧
    url(r'^password_auth_2/$', views.views.password_auth_2, name='password_auth_2'),   # 一覧(パスワード画面)
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
    # 勘定科目(貸借用)
    url(r'^account/$', views.views.account_list, name='account_list'),     # 一覧
    url(r'^account/add/$', views.views.account_edit, name='account_add'),  # 登録
    url(r'^account/mod/(?P<account_id>\d+)/$', views.views.account_edit, name='account_mod'),    # 修正
    url(r'^account/del/(?P<account_id>\d+)/$', views.views.account_del, name='account_del'),     # 削除
    url('account_sort/', views.ajaxs.ajax_account_sort, name='account_sort'),                    #ajax
    # 勘定補助科目(貸借用)
    url(r'^account_sub/$', views.views.account_sub_list, name='account_sub_list'),                         # 一覧
    url(r'^account_sub/add/$', views.views.account_sub_edit, name='account_sub_add'),                      # 登録
    url(r'^account_sub/mod/(?P<account_sub_id>\d+)/$', views.views.account_sub_edit, name='account_sub_mod'),  # 修正
    url(r'^account_sub/del/(?P<account_sub_id>\d+)/$', views.views.account_sub_del, name='account_sub_del'),   # 削除
    url('account_sub_sort/', views.ajaxs.ajax_account_sub_sort, name='account_sub_sort'),                      #ajax
    #
    # 支払管理
    #支払
    url(r'^payment/$', views.views.payment_list, name='payment_list'),   # 一覧
    url(r'^password_auth_1/$', views.views.password_auth_1, name='password_auth_1'),   # 一覧(パスワード画面)
    
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
    #支払
    url(r'^payment_reserve/$', views.views.payment_reserve_list, name='payment_reserve_list'),   # 一覧
    url(r'^payment_reserve/add/$', views.views.payment_reserve_edit, name='payment_reserve_add'),  # 登録
    url(r'^payment_reserve/mod/(?P<payment_reserve_id>\d+)/$', views.views.payment_reserve_edit, name='payment_reserve_mod'),  # 修正
    url(r'^payment_reserve/del/(?P<payment_reserve_id>\d+)/$', views.views.payment_reserve_del, name='payment_reserve_del'),   # 削除
    #資金繰り表(集計)
    url(r'^cash_flow_header/$', views.views.cash_flow_header_list, name='cash_flow_header_list'),   # 一覧
    url(r'^password_auth_5_1/$', views.views.password_auth_5_1, name = 'password_auth_5_1'),  #一覧(パスワード画面)
    url(r'^cash_flow_header/mod/(?P<cash_flow_header_id>\d+)/$', views.views.cash_flow_header_edit, name='cash_flow_header_mod'),  # 修正
    url(r'^cash_flow_header/report_1/$', views.pdf_cash_flow_list.cash_flow_list_1, name='cash_flow_list_1'),    #資金繰り表1
    url(r'^cash_flow_header/set_cash_flow_1/$', views.aggregate_cash_flow.set_cash_flow, name='set_cash_flow'),  #資金繰り見出データ作成
    #資金繰(予定)
    url(r'^cash_flow_detail_expected/$', views.views.cash_flow_detail_expected_list, name='cash_flow_detail_expected_list'),   # 一覧
    url(r'^cash_flow_detail_expected/del/(?P<cash_flow_detail_expected_id>\d+)/$', views.views.cash_flow_detail_expected_del, name='cash_flow_detail_expected_del'),   # 削除
    #資金繰(実際)
    url(r'^cash_flow_detail_actual/$', views.views.cash_flow_detail_actual_list, name='cash_flow_detail_actual_list'),   # 一覧
    url(r'^cash_flow_detail_actual/del/(?P<cash_flow_detail_actual_id>\d+)/$', views.views.cash_flow_detail_actual_del, name='cash_flow_detail_actual_del'),   # 削除
    #貸借データ
    url(r'^balance_sheet/$', views.views.balance_sheet_list, name='balance_sheet_list'),   # 一覧
    url(r'^balance_sheet/add/$', views.views.balance_sheet_edit, name='balance_sheet_add'),  # 登録
    url(r'^balance_sheet/mod/(?P<balance_sheet_id>\d+)/$', views.views.balance_sheet_edit, name='balance_sheet_mod'),  # 修正
    url(r'^balance_sheet/del/(?P<balance_sheet_id>\d+)/$', views.views.balance_sheet_del, name='balance_sheet_del'),   # 削除
    #貸借表
    url(r'^balance_sheet_tally/$', views.views.balance_sheet_tally_list, name='balance_sheet_tally_list'),   # 一覧
    #add240425
    #代表者貸付
    url(r'^daily_representative_loan/$', views.views.daily_representative_loan_list, name='daily_representative_loan_list'),   # 一覧
    url(r'^daily_representative_loan/add/$', views.views.daily_representative_loan_edit, name='daily_representative_loan_add'),  # 登録
    url(r'^daily_representative_loan/mod/(?P<daily_representative_loan_id>\d+)/$', views.views.daily_representative_loan_edit, name='daily_representative_loan_mod'),  # 修正
    url(r'^daily_representative_loan/del/(?P<daily_representative_loan_id>\d+)/$', views.views.daily_representative_loan_del, name='daily_representative_loan_del'),   # 削除
    #代表者貸付(月次)
    url(r'^monthly_representative_loan/$', views.views.monthly_representative_loan_list, name='monthly_representative_loan_list'),   # 一覧
    url(r'^monthly_representative_loan/add/$', views.views.monthly_representative_loan_edit, name='monthly_representative_loan_add'),  # 登録
    url(r'^monthly_representative_loan/mod/(?P<monthly_representative_loan_id>\d+)/$', views.views.monthly_representative_loan_edit, name='monthly_representative_loan_mod'),  # 修正
    url(r'^monthly_representative_loan/del/(?P<monthly_representative_loan_id>\d+)/$', views.views.monthly_representative_loan_del, name='monthly_representative_loan_del'),   # 削除
    #未払費用
    url(r'^accrued_expence/$', views.views.accrued_expence_list, name='accrued_expence_list'),   # 一覧
    url(r'^password_auth_3/$', views.views.password_auth_3, name='password_auth_3'),   # 一覧(パスワード画面)
    url(r'^accrued_expence/add/$', views.views.accrued_expence_edit, name='accrued_expence_add'),  # 登録
    url(r'^accrued_expence/mod/(?P<accrued_expence_id>\d+)/$', views.views.accrued_expence_edit, name='accrued_expence_mod'),  # 修正
    url(r'^accrued_expence/del/(?P<accrued_expence_id>\d+)/$', views.views.accrued_expence_del, name='accrued_expence_del'),   # 削除
    #役員報酬
    url(r'^compensation/$', views.views.compensation_list, name='compensation_list'),    #一覧
    url(r'^password_auth_6_4/$', views.views.password_auth_6_4, name='password_auth_6_4'),     # 一覧(パスワード画面)
    url('set_carryover', views.ajaxs.ajax_set_carryover, name = "set_carryover"),    #ajax
    url(r'^compensation/add/$', views.views.compensation_edit, name='compensation_add'),  #登録
    url(r'^compensation/mod/(?P<compensation_id>\d+)$', views.views.compensation_edit, name='compensation_mod'),  #修正
    url(r'^compensation/del/(?P<compensation_id>\d+)$', views.views.compensation_del, name='compensation_del') ,  #削除
    #日次役員報酬
    url(r'^daily_compensation/$', views.views.daily_compensation_list, name='daily_compensation_list'),   #一覧
    url(r'^password_auth_6_5/$', views.views.password_auth_6_5, name='password_auth_6_5'),      # 一覧(パスワード画面)
    url('set_compensation/', views.ajaxs.ajax_set_compensation, name = "set_compensation"),  #ajax
    url(r'^daily_compensation/add/$', views.views.daily_compensation_edit, name='daily_compensation_add'),
    url(r'^daily_compensation/mod/(?P<daily_compensation_id>\d+)$', views.views.daily_compensation_edit, name='daily_compensation_mod'), #修正
    url(r'^daily_compensation/del/(?P<daily_compensation_id>\d+)$', views.views.daily_compensation_del, name='daily_compensation_del'),   #削除
    #代表者貸付(年次)
    url(r'^yearly_representative_loan/$', views.views.yearly_representative_loan_list, name='yearly_representative_loan_list'),      # 一覧
    url(r'^yearly_representative_loan/add/$', views.views.yearly_representative_loan_edit, name='yearly_representative_loan_add'),   # 登録
    url(r'^yearly_representative_loan/mod/(?P<yearly_representative_loan_id>\d+)$', views.views.yearly_representative_loan_edit, name='yearly_representative_loan_mod'),
    url(r'^yearly_representative_loan/del/(?P<yearly_representative_loan_id>\d+)$', views.views.yearly_representative_loan_del, name='yearly_representative_loan_del')
]