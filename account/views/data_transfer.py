#データ一括移行用
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
#from django.http import HttpResponse
#
from account.models import Partner
from account.models import Account_Title
from account.models import Bank
from account.models import Bank_Branch
from account.models import Payment
from account.models import Payment_Reserve
#

from account.views import set_cash_flow_detail as Set_Cash_Flow_Detail  #add200121

from django.http import Http404, HttpResponse, QueryDict
#from django.template import RequestContext
from django.conf import settings

from django.core.cache import cache
from datetime import datetime, date, timedelta
from account.views import jholiday
from dateutil.relativedelta import relativedelta

from copy import deepcopy

#for debug
#import pdb; pdb.set_trace()

#取引先マスターより支払データを一括コピー
def automake_payment(request):
    
    #定数-固定フラグ
    CONTENT_ASSIGNED_MONTH = 2              #固定フラグ（指定月）のID
    CONTENT_ASSIGNED_MONTH_WITH_AMOUNT = 4  #固定フラグ（指定月-固定費）のID
    CONTENT_WITH_AMOUNT = 3                 #固定フラグ（項目・固定費）のID
    #定数-支払月フラグ
    PAY_DIVISION_THIS_MONTH = 0
    PAY_DIVISION_NEXT_MONTH = 1
    PAY_DIVISION_MONTH_AFTER_NEXT = 2
    PAY_DIVISION_THIS_MONTH_END_ADVANCE = 3
    PAY_DIVISION_THIS_MONTH_END_POSTPONE = 4
    
    #add180903
    PAY_DIVISION_NEXT_MONTH_END_ADVANCE = 5
    PAY_DIVISION_NEXT_MONTH_END_POSTPONE = 6
    #
    
    #temp_date = cache.get('search_query_month')
    #upd180418
    temp_date = cache.get('search_query_month_from')
    
    #import pdb; pdb.set_trace()
    
    
    if temp_date is not None:
        temp_date += "-01"
    
        dtm = datetime.strptime(temp_date, '%Y-%m-%d')
        assigned_date = dtm.date() 
    
        #まず指定月のものを一括で削除する
        Payment.objects.filter(billing_year_month=assigned_date).delete()
        
        ###取引先から支払データを一括作成する。
        partners = Partner.objects.all().order_by('order')
        
        for partner in partners:
            
            payment = Payment()
            
            fixed_content = False
            if partner.fixed_content_id is not None:    #固定フラグがある場合のみ作成
                if (partner.fixed_content_id is CONTENT_ASSIGNED_MONTH) or (partner.fixed_content_id is CONTENT_ASSIGNED_MONTH_WITH_AMOUNT):
                #if partner.fixed_content_id is CONTENT_ASSIGNED_MONTH:
                #月指定有り?
                    fixed_content = False
                    #指定年月から月のみ取得
                    assigned_month = assigned_date.month
                    
                    #import pdb; pdb.set_trace()
                    
                    ###指定月の判定
                    if partner.pay_month_flag_1 is True:  #1月の場合
                        if assigned_month is 1:
                            fixed_content = True
                    if partner.pay_month_flag_2 is True:  #2月の場合
                        if assigned_month is 2:
                            fixed_content = True
                    if partner.pay_month_flag_3 is True:  #3月の場合
                        if assigned_month is 3:
                            fixed_content = True
                    if partner.pay_month_flag_4 is True:  #4月の場合
                        if assigned_month is 4:
                            fixed_content = True
                    if partner.pay_month_flag_5 is True:  #5月の場合
                        if assigned_month is 5:
                            fixed_content = True
                    if partner.pay_month_flag_6 is True:  #6月の場合
                        if assigned_month is 6:
                            fixed_content = True
                    if partner.pay_month_flag_7 is True:  #7月の場合
                        if assigned_month is 7:
                            fixed_content = True
                    if partner.pay_month_flag_8 is True:  #8月の場合
                        if assigned_month is 8:
                            fixed_content = True
                    if partner.pay_month_flag_9 is True:  #9月の場合
                        if assigned_month is 9:
                            fixed_content = True
                    if partner.pay_month_flag_10 is True: #10月の場合
                        if assigned_month is 10:
                            fixed_content = True
                    if partner.pay_month_flag_11 is True: #11月の場合
                        if assigned_month is 11:
                            fixed_content = True
                    if partner.pay_month_flag_12 is True: #12月の場合
                        if assigned_month is 12:
                            fixed_content = True
                    ###
                
                else:
                #上記以外（月指定なし）
                    fixed_content = True
    
            if fixed_content is True:    #固定フラグがある場合のみ作成
                payment.order = partner.order
                payment.billing_year_month = assigned_date
                payment.partner_id = partner.id
                payment.trade_division_id = partner.trade_division_id
                payment.payment_method_id = partner.payment_method_id
                payment.account_title_id = partner.account_title_id
                #add180418
                #振込・振替口座をセット（振込か引落の場合のみ）
                if payment.payment_method_id == settings.ID_PAYMENT_METHOD_TRANSFER or \
                      payment.payment_method_id == settings.ID_PAYMENT_METHOD_WITHDRAWAL:
                    payment.source_bank = partner.source_bank
                    
                    #add200120
                    #支店もセット
                    if partner.source_bank_branch:
                        payment.source_bank_branch = partner.source_bank_branch
                #固定費
                if partner.fixed_content_id is CONTENT_ASSIGNED_MONTH_WITH_AMOUNT:  
                    #固定フラグ（指定月-固定費）
                    payment.billing_amount = partner.fixed_cost
                elif partner.fixed_content_id is CONTENT_ASSIGNED_MONTH:            
                    #固定フラグ（指定月）
                    payment.billing_amount = None
                elif partner.fixed_content_id is CONTENT_WITH_AMOUNT:               
                    #固定フラグ（項目・固定費）
                    payment.billing_amount = partner.fixed_cost
                else:
                    #以外
                    payment.billing_amount = None
                #
                payment.rough_estimate = partner.rough_estimate     #概算
               
                #支払日の計算
                tmp_year = assigned_date.year
                tmp_month = assigned_date.month
                tmp_day = partner.pay_day
                
                #if partner.pay_day_division is PAY_DIVISION_THIS_MONTH_END_ADVANCE:
                if partner.pay_day_division is PAY_DIVISION_THIS_MONTH_END_ADVANCE or \
                    partner.pay_day_division is PAY_DIVISION_THIS_MONTH_END_POSTPONE or \
                    partner.pay_day_division is PAY_DIVISION_NEXT_MONTH_END_ADVANCE or \
                    partner.pay_day_division is PAY_DIVISION_NEXT_MONTH_END_POSTPONE:
                #月末の場合は、とりあえず１日としておく（後で算出）
                    tmp_day = 1
                
                #各日付の加減算を行う
                if tmp_day > 0:
                    
                    pay_date = date(int(tmp_year), int(tmp_month), int(tmp_day))
                    
                    if partner.pay_day_division is PAY_DIVISION_THIS_MONTH: 
                    #当月?
                        #土日祝を考慮して加算する
                        pay_date = date_eliminate_holiday(pay_date, 1)
                    elif partner.pay_day_division is PAY_DIVISION_NEXT_MONTH: 
                    #翌月?
                        pay_date += relativedelta(months=1) #月を１つ加算
                        
                        #土日祝を考慮して加算する
                        pay_date = date_eliminate_holiday(pay_date, 1)
                    elif partner.pay_day_division is PAY_DIVISION_MONTH_AFTER_NEXT: 
                    #翌々月?
                        pay_date += relativedelta(months=2) #月を2つ加算
                         #土日祝を考慮して加算する
                        pay_date = date_eliminate_holiday(pay_date, 1)
                    elif partner.pay_day_division is PAY_DIVISION_THIS_MONTH_END_ADVANCE:
                    #月末(前倒)
                        pay_date += relativedelta(months=1, days=-1) #1ヶ月加算して1日減算
                        
                        #土日祝を考慮して加算する（月末の場合は、土日祝があれば日付は”前倒し”になる）
                        pay_date = date_eliminate_holiday(pay_date, 2)
                    elif partner.pay_day_division is PAY_DIVISION_THIS_MONTH_END_POSTPONE:
                    #月末(先送)
                        pay_date += relativedelta(months=1, days=-1) #1ヶ月加算して1日減算
                        
                        #土日祝を考慮して加算する（月末の場合は、土日祝があれば日付は”先送り”になる）
                        pay_date = date_eliminate_holiday(pay_date, 1)
                    elif partner.pay_day_division is PAY_DIVISION_NEXT_MONTH_END_ADVANCE:
                    #翌月末(前倒)
                        pay_date += relativedelta(months=2, days=-1) #2ヶ月加算して1日減算
                        
                        #土日祝を考慮して加算する（月末の場合は、土日祝があれば日付は”前倒し”になる）
                        pay_date = date_eliminate_holiday(pay_date, 2)
                    elif partner.pay_day_division is PAY_DIVISION_NEXT_MONTH_END_POSTPONE:
                    #翌月末(先送)
                        pay_date += relativedelta(months=2, days=-1) #2ヶ月加算して1日減算
                        
                        #土日祝を考慮して加算する（月末の場合は、土日祝があれば日付は”先送り”になる）
                        pay_date = date_eliminate_holiday(pay_date, 1)
                    #ex.翌々月も追加する場合は、ここの条件分岐に加える他、１つ前の条件分岐にも
                    #追記すること。
                    
                    #支払日区分入力有り？
                    #if partner.pay_day_division > 0:  
                        
                    
                    #支払予定日へセット
                    payment.payment_due_date = pay_date
                #
                
                payment.save()
                
                #add200121
                #資金繰明細データも保存する
                Set_Cash_Flow_Detail.set_cash_flow_detail(payment.id)
        
        #add191220
        #支払予約データがあれば上書or追加する
        payment_reserves = Payment_Reserve.objects.all().filter(billing_year_month=assigned_date)
        
        for payment_reserve in payment_reserves:
          
          try:
            payment = Payment.objects.get(billing_year_month=assigned_date, 
                                       partner_id=payment_reserve.partner_id)
            
            #一括コピーできる方法があればよいが..
            #payment.billing_year_month = payment_reserve.billing_year_month
            payment.trade_division_id = payment_reserve.trade_division_id
            #payment.partner_id = payment_reserve.partner_id
            payment.account_title_id = payment_reserve.account_title_id
            payment.billing_amount = payment_reserve.billing_amount
            payment.rough_estimate = payment_reserve.rough_estimate
            payment.payment_method_id = payment_reserve.payment_method_id
            payment.source_bank_id = payment_reserve.source_bank_id
            payment.payment_due_date = payment_reserve.payment_due_date
            #
            payment.save()
            
            #add200121
            #資金繰明細データも保存する
            Set_Cash_Flow_Detail.set_cash_flow_detail(payment.id)
            
          except Payment.DoesNotExist:
            #一括コピーできる方法があればよいが..
            payment.billing_year_month = payment_reserve.billing_year_month
            payment.trade_division_id = payment_reserve.trade_division_id
            payment.partner_id = payment_reserve.partner_id
            payment.account_title_id = payment_reserve.account_title_id
            payment.billing_amount = payment_reserve.billing_amount
            payment.rough_estimate = payment_reserve.rough_estimate
            payment.payment_method_id = payment_reserve.payment_method_id
            payment.source_bank_id = payment_reserve.source_bank_id
            payment.payment_due_date = payment_reserve.payment_due_date
            #
            payment.save()
             
            #add200121
            #資金繰明細データも保存する
            Set_Cash_Flow_Detail.set_cash_flow_detail(payment.id)
    
    return redirect('account:payment_list')

def date_eliminate_holiday(tmp_date, add_flag):
    #土日祝の場合、日付を加算する
    #引数add_flagが１の場合、翌日以降（加算）とし、２の場合は−１日（減算）とする
    
    #if partner.pay_day_division is PAY_DIVISION_THIS_MONTH_END_ADVANCE:
    #    import pdb; pdb.set_trace()
    
    
    for num in range(10):   #１０日最大とする
        
        holiday_flag = False
        
        #土日？
        if (tmp_date.weekday() >= 5):
            holiday_flag = True
        else:
        #それ以外で祝日？
            holiday_name = jholiday.holiday_name(date=tmp_date)
            if holiday_name is not None:
                holiday_flag = True
        #日付の加減算を行う
        if holiday_flag is True:
            if add_flag is 1:
                tmp_date += timedelta(days=1)
            elif add_flag is 2:
                tmp_date += timedelta(days=-1)
            
    return tmp_date

#支払データを指定年月で一括消去
def delete_all_payment(request):
    
    #temp_date = cache.get('search_query_month')
    #月は１月のみ指定とする（複数月は考慮していない）
    temp_date = cache.get('search_query_month_from')
    if temp_date is not None:
        temp_date += "-01"
        dtm = datetime.strptime(temp_date, '%Y-%m-%d')
        assigned_date = dtm.date() 
    
        Payment.objects.filter(billing_year_month=assigned_date).delete()

    return redirect('account:payment_list')
