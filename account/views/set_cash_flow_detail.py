from account.models import Cash_Flow_Detail_Expected
from account.models import Cash_Flow_Detail_Actual
from account.models import Cash_Book
from account.models import Payment
from django.conf import settings
#for debug
#import pdb; pdb.set_trace()

#資金繰明細データへの書き込み処理(現金出納帳より)
def set_cash_flow_detail_from_cash_book(cash_book_id):
    
    STAFF_PRESIDENT = 1
    
    cash_book = Cash_Book.objects.get(pk=cash_book_id)
    
    #実績データを一旦削除
    #Cash_Flow_Detail_Actual.objects.filter(cash_book_id=cash_book_id).delete()
    
    cash_flow_detail_actual = Cash_Flow_Detail_Actual.objects.filter(cash_book_id=cash_book_id).first()
    
    
    #社長以外の分&領収日入力有&金額入力有の場合のみセット
    if cash_book and cash_book.staff_id != STAFF_PRESIDENT and cash_book.receipt_date is not None \
                    and (cash_book.expences or cash_book.incomes):
                    
          
        #if cash_flow_detail_actual is None:  #新規の場合
        if not cash_flow_detail_actual:  #新規の場合
            cash_flow_detail_actual = Cash_Flow_Detail_Actual()
            cash_flow_detail_actual.cash_book_id = cash_book_id  #キー用
        
        #科目
        cash_flow_detail_actual.account_title_id = cash_book.account_title_id
        
        #cash_flow_detail_actual.actual_date = cash_book.receipt_date
        cash_flow_detail_actual.actual_date = cash_book.settlement_date  #精算日とする
        cash_flow_detail_actual.cash_id = 1 
        
        if cash_book.expences:
            cash_flow_detail_actual.actual_expense = cash_book.expences
        if cash_book.incomes:
            #cash_flow_detail_actual.actual_income = cash_book.incomes
            #upd200213
            cash_flow_detail_actual.actual_income = -cash_book.incomes
        
        cash_flow_detail_actual.save()  #
    else:
        if cash_flow_detail_actual:  #該当しなければ実績データを削除
            cash_flow_detail_actual.delete()
        
#資金繰明細データへの書き込み処理(支払より)
def set_cash_flow_detail(payment_id):
    payment = Payment.objects.get(pk=payment_id)
    
    #if payment and payment.payment_due_date is not None and payment.billing_amount is not None:
    
    #一旦削除(予定・実施)
    #Cash_Flow_Detail_Expected.objects.filter(billing_year_month=payment.billing_year_month, 
    #                partner_id=payment.partner_id).delete()
    #Cash_Flow_Detail_Actual.objects.filter(billing_year_month=payment.billing_year_month, 
    #                partner_id=payment.partner_id).delete()
    
    cash_flow_detail_expected = Cash_Flow_Detail_Expected.objects.filter(billing_year_month=payment.billing_year_month, 
                    partner_id=payment.partner_id).first()
    cash_flow_detail_actual = Cash_Flow_Detail_Actual.objects.filter(billing_year_month=payment.billing_year_month, 
                    partner_id=payment.partner_id).first()
    
    #import pdb; pdb.set_trace()
    
    
    #支払予定日有、請求金額入力有の場合にセット
    
    #☓☓☓支払予定日有、請求金額入力有、かつ支払日未入力の場合だけセット
    #if payment and payment.payment_due_date is not None and payment.billing_amount is not None and payment.payment_date is None:
    #支払日が入力された時点で削除するべきか否か？？
    
    set_flag = False
    
    if payment and payment.payment_due_date is not None and payment.billing_amount is not None:
        
        set_flag = True
        
        if not cash_flow_detail_expected:  #新規の場合
        #if cash_flow_detail_expected is None:  #新規の場合
            cash_flow_detail_expected = Cash_Flow_Detail_Expected()
        
        cash_flow_detail_expected.expected_date = payment.payment_due_date
        
        cash_flow_detail_expected.billing_year_month = payment.billing_year_month
        cash_flow_detail_expected.partner_id = payment.partner_id
        cash_flow_detail_expected.account_title_id = payment.account_title_id
        
        #一旦値をリセットしておく
        cash_flow_detail_expected.payment_bank_id = None
        cash_flow_detail_expected.payment_bank_branch_id = None
        cash_flow_detail_expected.cash_id = None
        #
                
        if payment.billing_amount:
            cash_flow_detail_expected.expected_expense = payment.billing_amount
    
        #if payment.payment_method_id == 1:
        if payment.payment_method_id == settings.ID_PAYMENT_METHOD_TRANSFER or \
                      payment.payment_method_id == settings.ID_PAYMENT_METHOD_WITHDRAWAL:
        #振込・振替口座をセット（振込か引落の場合）
    
            cash_flow_detail_expected.payment_bank_id = payment.source_bank_id
            cash_flow_detail_expected.payment_bank_branch_id = payment.source_bank_branch_id
        elif payment.payment_method_id == settings.ID_PAYMENT_METHOD_CASH:
        #現金の場合
        
            cash_flow_detail_expected.cash_id = 1   #ひとまず１をセット
            
            #if payment.source_bank_id == settings.ID_BANK_HOKUETSU || not payment.source_bank_id:
            ##北越orNullの場合、そのままセット
            #    cash_flow_detail_expected.payment_bank_id = payment.source_bank_id
            #elseif payment.source_bank_id == settings.ID_BANK_SANSHIN
            ##さんしんの場合、塚野目が本店で要判定
            #    #注:ID=3になっているので２にする
            #    cash_flow_detail_expected.payment_bank_id = payment.source_bank_id
            #    #ここで支店も保管させる
        
        #支払方法
        cash_flow_detail_expected.payment_method_id = payment.payment_method_id
        
        cash_flow_detail_expected.save()
    
    #if payment and payment.billing_amount is not None and payment.payment_date is not None:
    if payment and payment.billing_amount is not None and payment.payment_date is not None \
       and payment.payment_method_id != settings.ID_PAYMENT_METHOD_CASH:
    #実施のデータへ保存する処理
       #現金は、出納帳から保存するのでここでは除外する
        
        set_flag = True
        
        #if cash_flow_detail_actual is None:  #新規の場合
        if not cash_flow_detail_actual:  #新規の場合
            cash_flow_detail_actual = Cash_Flow_Detail_Actual()
            
        cash_flow_detail_actual.actual_date = payment.payment_date
        
        cash_flow_detail_actual.billing_year_month = payment.billing_year_month
        cash_flow_detail_actual.partner_id = payment.partner_id
        cash_flow_detail_actual.account_title_id = payment.account_title_id
        
        #一旦値をリセットしておく
        cash_flow_detail_actual.payment_bank_id = None
        cash_flow_detail_actual.payment_bank_branch_id = None
        cash_flow_detail_actual.cash_id = None
        #
        
        if payment.billing_amount:
            cash_flow_detail_actual.actual_expense = payment.billing_amount
    
        if payment.payment_method_id == settings.ID_PAYMENT_METHOD_TRANSFER or \
                      payment.payment_method_id == settings.ID_PAYMENT_METHOD_WITHDRAWAL:
        #振込・振替口座をセット（振込か引落の場合）
    
            cash_flow_detail_actual.payment_bank_id = payment.source_bank_id
            cash_flow_detail_actual.payment_bank_branch_id = payment.source_bank_branch_id
        
        #elif payment.payment_method_id == settings.ID_PAYMENT_METHOD_CASH:
        #現金の場合
        #    cash_flow_detail_actual.cash_id = 1   #ひとまず１をセット
        
        #支払方法
        cash_flow_detail_actual.payment_method_id = payment.payment_method_id
        
        #import pdb; pdb.set_trace()
        
        cash_flow_detail_actual.save()
    #else:
    
    if not set_flag:
        
        #どれも該当しない場合、登録済のデータなら削除する
        if cash_flow_detail_expected:
            cash_flow_detail_expected.delete()
        
        if cash_flow_detail_actual:
            cash_flow_detail_actual.delete()
    #
                
                