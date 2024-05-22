#from django.shortcuts import render, get_object_or_404, redirect

from account.models import Payment
from account.models import Partner
from account.models import DailyCashFlow
from account.models import Expence
from account.models import Deposit
from account.models import Cash_Book

from django.conf import settings
from django.db.models import Q

#for debug
#import pdb; pdb.set_trace()

#日次入金ファイルへ加算(出納帳)
def set_cash_book_to_deposit(cash_book, settlement_date, amount):
    
    if settlement_date is not None and \
       amount is not None and abs(amount) > 0:
        
        deposit = Deposit.objects.filter(table_id=cash_book.id, table_type_id=settings.TABLE_TYPE_CASH_BOOK).first()
        
        if deposit is None:
            deposit = Deposit()
        
        deposit.table_type_id = settings.TABLE_TYPE_CASH_BOOK
        deposit.table_id = cash_book.id
        deposit.deposit_due_date = cash_book.settlement_date
        deposit.deposit_amount = cash_book.incomes
        
        deposit.deposit_source_id = settings.ID_SOURCE_CASH
        deposit.name = str(cash_book.account_title)
        deposit.completed_flag = 1  #常に完了とする
        
        deposit.save()

#日次入金ファイルへ加算
def set_deposit(balance_sheet, accrual_date, amount):
  
    if accrual_date is not None and \
       amount is not None and abs(amount) > 0:
        
        deposit = Deposit.objects.filter(table_id=balance_sheet.id, table_type_id=settings.TABLE_TYPE_BALANCE_SHEET).first()
        
        if deposit is None:
            deposit = Deposit()
        
        deposit.table_type_id = settings.TABLE_TYPE_BALANCE_SHEET
        deposit.table_id = balance_sheet.id
        deposit.deposit_due_date = balance_sheet.accrual_date
        deposit.deposit_amount = balance_sheet.amount
                
        deposit.deposit_source_id = settings.ID_BANK_HOKUETSU   #デフォルトは第四にする
        
        if balance_sheet.bank_id == 1 or \
           balance_sheet.bank_id == 2:
           
           deposit.deposit_source_id = settings.ID_BANK_SANSHIN
        
        deposit.name = balance_sheet.description
        deposit.completed_flag = 1  #常に完了とする
        
        deposit.save()

#日次出金ファイルへ加算(出納帳データ)
def set_cash_book_to_expence(cash_book, settlement_date, amount):

    if settlement_date is not None and \
        amount is not None and abs(amount) > 0:
        
        expence = Expence.objects.filter(table_id=cash_book.id, table_type_id=settings.TABLE_TYPE_CASH_BOOK).first()
        
        if expence is None:
            expence = Expence()
        
        expence.table_type_id = settings.TABLE_TYPE_CASH_BOOK
        expence.table_id = cash_book.id
        expence.payment_on = settlement_date
        expence.payment_amount = amount
        
        expence.payment_source_id = settings.ID_SOURCE_CASH
        expence.name = str(cash_book.account_title)
        
        expence.is_completed = 1 #常に1とする
        
        expence.save()
            
#日次出金ファイルへ加算(貸借データ)
def set_balance_sheet_to_expence(balance_sheet, accrual_date, amount):
    
    if accrual_date is not None and \
       amount is not None and abs(amount) > 0:
        
        expence = Expence.objects.filter(table_id=balance_sheet.id, table_type_id=2).first()
        
        if expence is None:
            #新規の場合
            expence = Expence()
        
        expence.table_type_id = 2 #
        expence.table_id = balance_sheet.id
        #expence.payment_method_id = 
        expence.payment_on = accrual_date
        expence.payment_amount = amount
        
        expence.payment_source_id = settings.ID_BANK_HOKUETSU   #デフォルトは第四にする
        
        if balance_sheet.bank_id == 1 or \
           balance_sheet.bank_id == 2:
           
           expence.payment_source_id = settings.ID_BANK_SANSHIN
        
        expence.name = balance_sheet.description
        expence.is_completed = 1 #常に1とする
        
        expence.save()
        
#日次出金ファイルへ加算(支払データ)
#def set_expence(payment, pay_date, billing_amount, is_estimate):
def set_payment_to_expence(payment, pay_date, billing_amount, is_estimate):
    
    if pay_date is not None and \
        billing_amount is not None and abs(billing_amount) > 0:
        
        #要修正....
        #expence = Expence.objects.filter(payment_on=pay_date).first()
        expence = Expence.objects.filter(table_id=payment.id, table_type_id=1).first()
        
        if expence is None:
            #新規の場合
            expence = Expence()
        
        #各カラムへセット
        #expence.table_id = 1  #テーブルIDは常に1とする
        expence.table_type_id = 1  #テーブル種類IDは常に1とする
        #expence.payment_id = payment.id
        expence.table_id = payment.id
        expence.payment_method_id = payment.payment_method_id
        expence.payment_on = pay_date
        expence.unpaid_on = payment.unpaid_date  
        expence.payment_amount = billing_amount
        #add230315
        expence.unpaid_amount = payment.unpaid_amount
        expence.billing_year_month = payment.billing_year_month
        
        #支払元IDを設定
        expence.payment_source_id = set_payment_source_id(payment)
        
        #未払支払予定日
        if payment.unpaid_due_date is not None and \
           payment.unpaid_date is None:
            expence.unpaid_on = payment.unpaid_due_date
        
        #未払いフラグ
        #is_unpaid = 0
        #if payment.unpaid_due_date is not None or payment.unpaid_date is not None:
        #    is_unpaid = 1
        #expence.is_unpaid = is_unpaid
        #
        
        expence.is_completed = payment.completed_flag
        expence.is_estimate = is_estimate
        
        #取引先名をセットする
        partner = Partner.objects.filter(pk=payment.partner_id).first()
        if partner is not None:
            expence.name = partner.name
        #
        
        expence.save()

#支払元IDを設定
def set_payment_source_id(payment):
    
    #source_id = 0
    source_id = settings.ID_BANK_HOKUETSU  #デフォルトは第四北越にする
    
    if payment.source_bank_id == settings.ID_BANK_HOKUETSU or \
       payment.source_bank_id == settings.ID_BANK_SANSHIN:
        
        if payment.payment_method_id == settings.ID_PAYMENT_METHOD_CASH:
            source_id = 9  #現金の場合のID
        else:
            source_id = payment.source_bank_id  #銀行IDをセット
    elif payment.source_bank_id == None:
        if payment.payment_method_id == settings.ID_PAYMENT_METHOD_CASH:
            source_id = 9  #現金の場合のID
    
    return source_id
    
#日次入出金ファイルへ加算
def set_daily_cash_flow(pay_date, billing_amount, income_expence_flag):
    
    if pay_date is not None:
    
        daily_cash_flow = DailyCashFlow.objects.filter(cash_flow_date=pay_date).first()
        
        #if billing_amount is not None:
        if billing_amount is not None and abs(billing_amount) > 0:
            
            if daily_cash_flow is None:
                #新規の場合
            
                daily_cash_flow = DailyCashFlow()
        
                daily_cash_flow.cash_flow_date = pay_date
                
                #収入・支出により切分
                if income_expence_flag == 1:    #支出
                    daily_cash_flow.expence = billing_amount
                elif income_expence_flag == 0:  #収入
                    daily_cash_flow.income = billing_amount
                
                daily_cash_flow.save()
            else:
                #追加の場合、出金予定額をプラスして保存
                #収入・支出により切分
                if income_expence_flag == 1:    #支出
                    if daily_cash_flow.expence is None:
                        daily_cash_flow.expence = billing_amount
                    else:
                        daily_cash_flow.expence += billing_amount
                elif income_expence_flag == 0:  #収入
                    if daily_cash_flow.income is None:
                        daily_cash_flow.income = billing_amount
                    else:
                        daily_cash_flow.income += billing_amount
                                
                daily_cash_flow.save()

#日次入出金の完了フラグをセット
def set_complete_flag(table_id, table_type_id, pay_date, completed_flag, income_expence_flag):
    
    if completed_flag == 1:
        all_complete = True
        
        if table_type_id == settings.TABLE_TYPE_PAYMENT:  #payment(支払データ)の場合
        
            payments = Payment.objects.filter(payment_due_date=pay_date)
    
            for payment in payments:
                if payment.billing_amount is not None and payment.billing_amount != 0 \
                    and payment.id != table_id:
                
                    if payment.completed_flag is None or payment.completed_flag == 0:
                        all_complete = False
        
        elif table_type_id == settings.TABLE_TYPE_BALANCE_SHEET or \
                              settings.TABLE_TYPE_CASH_BOOK:   #balance_sheet or cash_bookの場合
            #作成中(未検証)
            
            #table_type_id = 1のデータが存在したら、完了フラグは書き換えないようにする
            
            if income_expence_flag == 0: 
                deposit_count = Deposit.objects.filter(deposit_due_date=pay_date, table_type_id=1).count()
                if deposit_count > 0:
                    all_complete = False
            elif income_expence_flag == 1:
                #expence_count = Expence.objects.filter(payment_on=pay_date, table_type_id=1).count
                expence_count = Expence.objects.filter(Q(payment_on=pay_date, table_type_id=1) | \
                                                       Q(unpaid_on=pay_date, table_type_id=1)).count()
                
                if expence_count > 0:
                    all_complete = False
                
        #if all_complete == True:
        daily_cash_flow = DailyCashFlow.objects.all().filter(cash_flow_date=pay_date).first()
            
        if daily_cash_flow is not None:
            if table_type_id == settings.TABLE_TYPE_PAYMENT:  #支払データの場合
                #完了フラグはいずれかをセット
                if all_complete == True:   
                    daily_cash_flow.expence_completed_flag = 1
                else:
                    daily_cash_flow.expence_completed_flag = 0
                daily_cash_flow.save()
            elif table_type_id == settings.TABLE_TYPE_BALANCE_SHEET or \
                                  settings.TABLE_TYPE_CASH_BOOK: #貸借、出納帳データの場合
                if all_complete == True:  #１件の場合のみ更新
                    if income_expence_flag == 1: 
                        daily_cash_flow.expence_completed_flag = 1
                    elif income_expence_flag == 0: #収入の場合
                        daily_cash_flow.income_completed_flag = 1
                    daily_cash_flow.save()
    else:
        #未完了の場合、先に完了フラグがセットされていたら外す。
        #(支払データのみの処理)
        daily_cash_flow = DailyCashFlow.objects.all().filter(cash_flow_date=pay_date).first()
        if daily_cash_flow is not None:
            if daily_cash_flow.expence_completed_flag == 1:
                daily_cash_flow.expence_completed_flag = 0
                daily_cash_flow.save()
        
#日次入出金ファイルから減算
def delete_daily_cash_flow(table_type_id, pay_date, billing_amount, income_expence_flag):
    
    #import pdb; pdb.set_trace()
    
    if pay_date is not None and billing_amount is not None:
        daily_cash_flow = DailyCashFlow.objects.filter(cash_flow_date=pay_date).first()
        
        #import pdb; pdb.set_trace()
        
        rec_count = 0
        if table_type_id == settings.TABLE_TYPE_PAYMENT:    #支払データの場合
            rec_count = Expence.objects.filter(Q(payment_on=pay_date) | Q(unpaid_on=pay_date)).count()
        elif table_type_id == settings.TABLE_TYPE_BALANCE_SHEET or \
             table_type_id == settings.TABLE_TYPE_CASH_BOOK:  #貸借データo出納帳データの場合
            if income_expence_flag == settings.FLAG_BP_EXPENCE:  #支出の場合
                rec_count = Expence.objects.filter(payment_on=pay_date).count()
            elif income_expence_flag == settings.FLAG_BP_INCOME:  #収入の場合
                rec_count = Deposit.objects.filter(deposit_due_date=pay_date).count()
        
        #import pdb; pdb.set_trace()
        
        if daily_cash_flow is not None:
            #table_type_idで切り分け？
            
            if income_expence_flag == settings.FLAG_BP_EXPENCE:    #支出の場合
                if daily_cash_flow.expence is not None:
                    daily_cash_flow.expence -= billing_amount
            elif income_expence_flag == settings.FLAG_BP_INCOME:  #収入の場合
                if daily_cash_flow.income is not None:
                    daily_cash_flow.income -= billing_amount
            #if no_complete_flag == False:
            if rec_count == 1:   #１件のみの場合のみ、完了フラグをリセット
                if income_expence_flag == settings.FLAG_BP_EXPENCE:    #支出の場合
                    daily_cash_flow.expence_completed_flag = 0
                elif income_expence_flag == settings.FLAG_BP_INCOME:  #収入の場合
                    daily_cash_flow.income_completed_flag = 0
            daily_cash_flow.save()
            
#def delete_expence(payment_id):
#    #payment = get_object_or_404(Payment, pk=payment_id)
#    #expence = get_object_or_404(Expence, pk=payment_id)
#    #expence = Expence.objects.get(pk=payment_id)
#    expence = Expence.objects.filter(id=payment_id).first
#    if expence is not None:
#        expence.delete
