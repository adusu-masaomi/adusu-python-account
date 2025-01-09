from account.models import Daily_Representative_Loan
#from account.models import Cash_Flow_Detail_Actual
#from account.models import Cash_Book
#from account.models import Payment
from django.conf import settings
#for debug
#import pdb; pdb.set_trace()


#出納帳データを貸付金データへ移行
def set_cash_book_to_representative(cash_book):
    
    is_data = False
    
    #"代表者貸付"がチェック状態で勘定科目が"入金"の時にのみ更新する
    if cash_book.is_representative and cash_book.account_title_id == \
       settings.ID_ACCOUNT_INCOMES:
        is_data = True
        
    id = cash_book.id
    
    representative_loan = Daily_Representative_Loan.objects.filter(table_type_id=2, table_id=id).first()
    
    if not representative_loan:
        #新規登録
        if is_data:  #add240425
            representative_loan = Daily_Representative_Loan()
            save_cash_book_to_representative(representative_loan, cash_book)
    else:
        #更新or削除
        if not is_data:
            #削除 --- 勘定科目が"入金"からそれ以外になった場合等は削除する
            representative_loan.delete()
            #Expence.objects.filter(table_id=cash_book_id, table_type_id=settings.TABLE_TYPE_CASH_BOOK).delete()
        else:
            #更新
            save_cash_book_to_representative(representative_loan, cash_book)
            
#貸借表データを貸付金データへ移行
def set_balance_sheet_to_representative(table_id, occurred_on, description, income_expence_flag, amount, bank_id, \
                                        is_representative):
    
    representative_loan = Daily_Representative_Loan.objects.filter(table_type_id=1, table_id=table_id).first()
    
    #debit = None:
    #credit = None:
    
    if not representative_loan:
        #新規登録
        
        if is_representative == 1:  #代表者貸付チェックの場合のみ登録
        
            representative_loan = Daily_Representative_Loan()
            save_balance_sheet_to_representative(representative_loan, table_id, occurred_on, description, \
                                income_expence_flag, amount, bank_id)
        
    else:
    #    #更新
        if is_representative == 1:  #代表者貸付チェックの場合のみ更新
            save_balance_sheet_to_representative(representative_loan, table_id, occurred_on, description, \
                                income_expence_flag, amount, bank_id)
        else:
            #代表者チェックのない状態で、すでに貸付金データがあった場合は削除する
            representative_loan.delete()

#出納帳データ→貸付金データへ
def save_cash_book_to_representative(representative_loan, cash_book):

    representative_loan.table_type_id = 2
    representative_loan.table_id = cash_book.id
    
    #発生日
    representative_loan.occurred_on = cash_book.settlement_date
    
    #科目(=2)
    representative_loan.account_id = 2  #現金
    
    #補助科目-->無
    
    #貸方勘定へ
    representative_loan.credit = cash_book.incomes
    
    #摘要
    #representative_loan.description = "個人より"
    representative_loan.description = "社長より"  #upd250109
    representative_loan.save()
    
#貸借表データ→貸付金データへ
def save_balance_sheet_to_representative(representative_loan, table_id, occurred_on, description, \
                        income_expence_flag, amount, bank_id):
    representative_loan.table_type_id = 1
    representative_loan.table_id = table_id
            
    #発生日
    representative_loan.occurred_on = occurred_on
        
    #科目(=1)
    representative_loan.account_id = 1  #普通　預金
            
    #補助科目
    tmp_id = convert_bank(bank_id)
            
    representative_loan.sub_account_id = tmp_id
        
    if income_expence_flag == settings.FLAG_BP_INCOME:
        #借→貸方勘定へ
        representative_loan.credit = amount
        representative_loan.debit = None
        
        #del250109
        #add250108
        #摘要未入力の場合のデフォルト設定
        #if description == "":
        #    description = "社長より"
    else:
        #貸→借方勘定へ
        representative_loan.debit = amount
        representative_loan.credit = None
        
        #del250109
        #add250108
        #摘要未入力の場合のデフォルト設定
        #if description == "":
        #    description = "社長へ"
    #摘要
    representative_loan.description = description
    representative_loan.save()

#貸借データの銀行IDを変換
def convert_bank(bank_id):
    tmp_id = None
    
    if bank_id is not None:
        if bank_id == 0:
        #第四北越
            tmp_id = 1
        else:  
        #三信
            tmp_id = 2
    
    return tmp_id

##資金繰明細データへの書き込み処理(現金出納帳より)
#def set_cash_flow_detail_from_cash_book(cash_book_id):    
#    STAFF_PRESIDENT = 1
#    cash_book = Cash_Book.objects.get(pk=cash_book_id)
#    #実績データを一旦削除
#    #Cash_Flow_Detail_Actual.objects.filter(cash_book_id=cash_book_id).delete()
#    cash_flow_detail_actual = Cash_Flow_Detail_Actual.objects.filter(cash_book_id=cash_book_id).first()
#    #社長以外の分&領収日入力有&金額入力有の場合のみセット
#    if cash_book and cash_book.staff_id != STAFF_PRESIDENT and cash_book.receipt_date is not None \
#                    and (cash_book.expences or cash_book.incomes):
#        #if cash_flow_detail_actual is None:  #新規の場合
#        if not cash_flow_detail_actual:  #新規の場合
#            cash_flow_detail_actual = Cash_Flow_Detail_Actual()
#            cash_flow_detail_actual.cash_book_id = cash_book_id  #キー用
#        #科目
#        cash_flow_detail_actual.account_title_id = cash_book.account_title_id
#        #cash_flow_detail_actual.actual_date = cash_book.receipt_date
#        cash_flow_detail_actual.actual_date = cash_book.settlement_date  #精算日とする
#        cash_flow_detail_actual.cash_id = 1 
#        if cash_book.expences:
#            cash_flow_detail_actual.actual_expense = cash_book.expences
#        if cash_book.incomes:
#            #cash_flow_detail_actual.actual_income = cash_book.incomes
#            #upd200213
#            cash_flow_detail_actual.actual_income = -cash_book.incomes
#        cash_flow_detail_actual.save()  #
#    else:
#        if cash_flow_detail_actual:  #該当しなければ実績データを削除
#            cash_flow_detail_actual.delete()
