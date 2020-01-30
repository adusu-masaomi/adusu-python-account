#from account.models import Cash_Flow_Detail_Expected  #未整理
from account.models import Balance_Sheet  
from account.models import Cash_Book    
from django.conf import settings

#貸借表データへの書き込み処理
def set_balance_sheet(cash_book_id):

    STAFF_PRESIDENT = 1

    cash_book = Cash_Book.objects.get(pk=cash_book_id)
    
    #一旦削除(予定・実施)
    #Balance_Sheet.objects.filter(cash_book_id=cash_book_id).delete()
    balance_sheet = Balance_Sheet.objects.filter(cash_book_id=cash_book_id).first()
    
    #社長分&領収日入力有&金額入力有の場合、又は
    #会社への入金分(社長以外)の場合にセット
    #if cash_book and cash_book.staff_id == STAFF_PRESIDENT and cash_book.receipt_date is not None \
    #                and cash_book.expences:
    if (cash_book and cash_book.staff_id == STAFF_PRESIDENT and cash_book.receipt_date is not None \
                    and cash_book.expences) or \
       (cash_book and cash_book.staff_id != STAFF_PRESIDENT and cash_book.receipt_date is not None \
                    and cash_book.incomes):
    
        #
        #if balance_sheet is None:  #新規の場合
        if not balance_sheet:  #新規の場合
            balance_sheet = Balance_Sheet()
            balance_sheet.cash_book_id = cash_book.id  #キー用
    
        #balance_sheet.accrual_date = cash_book.receipt_date
        balance_sheet.accrual_date = cash_book.settlement_date   #日付は請求日とする     
        
        #貸(入金)については、通帳からの引落時点で入力しているので、ここでは登録しない
        #if cash_book.incomes:
        #    balance_sheet.borrow_lend_id = 0  #貸とする
        #    balance_sheet.amount = cash_book.incomes
        
        #会社への入金については、借とする
        if cash_book.incomes:
            balance_sheet.borrow_lend_id = 1  #借とする
            balance_sheet.amount = cash_book.incomes
        
        if cash_book.expences:
            balance_sheet.borrow_lend_id = 1  #借とする
            balance_sheet.amount = cash_book.expences
        
        #摘要
        balance_sheet.description = cash_book.description_content
        
        #☓→勘定科目については、束ねる可能性があるので、保存せずにそのままとしておく。
        #account_id
        
        #勘定科目をセット
        balance_sheet.account_title_id = cash_book.account_title_id
        
        #銀行IDも明確ではないのでセットしない。
        #bank_id
        
        balance_sheet.save()
    else:
        if balance_sheet:
            balance_sheet.delete()  #該当しなければ貸借データを削除


  
                