import csv
import io
from django.core.cache import cache
from datetime import datetime, date, timedelta

from django.http import HttpResponse
#from django.urls import reverse_lazy
from django.views import generic
#from .forms import CSVUploadForm
from account.models import Cash_Book
from account.models import PurchaseOrderData
from django.conf import settings
import locale
from datetime import datetime, date, timedelta

#import pdb; pdb.set_trace()

def cash_book_export(request):
    response = HttpResponse(content_type='text/csv; charset=Shift-JIS')
    response['Content-Disposition'] = 'attachment; filename="cash_books.csv"'
    # HttpResponseオブジェクトはファイルっぽいオブジェクトなので、csv.writerにそのまま渡せます。
    writer = csv.writer(response)
    
    
    temp_date_from = cache.get('search_settlement_date_from')
    temp_date_to = cache.get('search_settlement_date_to')
    
    if temp_date_from is not None:
        
        dtm_from = datetime.strptime(temp_date_from, '%Y-%m-%d')
        dtm_to = datetime.strptime(temp_date_to, '%Y-%m-%d')
        
        #指定範囲の差引残高を算出
        cash_books = Cash_Book.objects.filter(settlement_date__gte=dtm_from.date(),
                                settlement_date__lte=dtm_to.date())
        if cash_books is not None:
            
            #精算日で並び替える
            cash_books = cash_books.order_by('settlement_date', 'order')
            
            
            #週初の残高をまず出力
            pre_balance = cache.get('pre_balance')
            pre_balance_president = cache.get('pre_balance_president')
            pre_balance_staff = cache.get('pre_balance_staff')
            
            writer.writerow(["総残高", pre_balance, "", "残高(社長分)", pre_balance_president, "残高(社員分)", pre_balance_staff])
        
            #ヘッダーはない
            
            cnt = 0 
            
            for cash_book in cash_books:
                expences_staff = ""
                expences_president = ""
            
                cnt += 1
            
                #支払いは社長と社員で切り分ける
                if cash_book.staff_id == settings.ID_STAFF_PRESIDENT:
                    expences_president = cash_book.expences
                else:
                    expences_staff = cash_book.expences
            
                #日付をフォーマット
                locale.setlocale(locale.LC_TIME, 'ja_JP.UTF-8')
                dtm_settlement = cash_book.settlement_date.strftime('%Y/%m/%d(%a)')
                #dtm_receipt = cash_book.receipt_date.strftime('%m/%d')
                #cash_book.pk
                
                #仕入Noまたは収入金額をセット
                str_incomes = ""
                incomes = cash_book.incomes or 0
                if incomes == 0:
                    try:
                        purchase_order = PurchaseOrderData.objects.get(pk=cash_book.purchase_order_code_id)
                    except PurchaseOrderData.DoesNotExist:
                        purchase_order = None
                    if purchase_order is not None:
                        str_incomes = "仕入(" + purchase_order.purchase_order_code + ")"
                else:
                    str_incomes = str(incomes)
                #
                
                writer.writerow([cnt, dtm_settlement, cash_book.receipt_date, cash_book.account_title, 
                     cash_book.description_partner, cash_book.description_content, str_incomes, expences_staff, expences_president])
            
            #週終わりの残高を出力
            balance = cache.get('balance')
            balance_president = cache.get('balance_president')
            balance_staff = cache.get('balance_staff')
            
            writer.writerow(["差引総残高", balance, "", "差引残高(社長分)", balance_president, "差引残高(社員分)", balance_staff])
            
    return response


def cash_book_export_extract(request):
#絞り込み抽出用CSV
#出納帳としては使用しない。担当別などでリスト作りたい場合に使用する。

    response = HttpResponse(content_type='text/csv; charset=Shift-JIS')
    response['Content-Disposition'] = 'attachment; filename="cash_books_extract.csv"'
    # HttpResponseオブジェクトはファイルっぽいオブジェクトなので、csv.writerにそのまま渡せます。
    writer = csv.writer(response)
    
    
    temp_date_from = cache.get('search_receipt_date_from')
    temp_date_to = cache.get('search_receipt_date_to')
    
    #精算日が入力されていたら、そっちを優先する
    settlement_flag = False
    
    if cache.get('search_settlement_date_from') is not None:
        settlement_flag = True
        
        temp_date_from = cache.get('search_settlement_date_from')
        temp_date_to = cache.get('search_settlement_date_to')
    
    search_account_title = cache.get('search_account_title')
    search_staff = cache.get('search_staff')
    
    if temp_date_from is not None:
        
        dtm_from = datetime.strptime(temp_date_from, '%Y-%m-%d')
        dtm_to = datetime.strptime(temp_date_to, '%Y-%m-%d')
        
        #指定条件で絞る
        if settlement_flag == False:
            cash_books = Cash_Book.objects.filter(receipt_date__gte=dtm_from.date(),
                                receipt_date__lte=dtm_to.date())
        else:
        #精算日で抽出する場合
            cash_books = Cash_Book.objects.filter(settlement_date__gte=dtm_from.date(),
                                settlement_date__lte=dtm_to.date())
        
        if search_account_title:
        #科目で絞り込み
            cash_books = cash_books.filter(account_title=search_account_title)
        if search_staff:
        #担当（社員）で絞り込み
            cash_books = cash_books.filter(staff=search_staff)
        #
        
        
        if cash_books is not None:
            
            #精算日でも並び替えれるようにする？？
            cash_books = cash_books.order_by('receipt_date', 'order')
            
            #ヘッダーはない
            
            #初期化
            cnt = 0 
            subtotal_incomes = 0
            total_incomes = 0
            subtotal_expences = 0
            total_expences = 0
            next_month = False
            month = 0
            subtotal_flag = False
            #
            
            for cash_book in cash_books:
                expences_staff = ""
                expences_president = ""
                
                #import pdb; pdb.set_trace()
                #月代わりの判定
                if next_month == False:
                    if cnt > 0:
                        if (cash_book.receipt_date.day >= 21) or \
                           (month != cash_book.receipt_date.month):
                            next_month = True
                #
                
                subtotal_flag = False  #最後の合計で出力判定するためのもの
                
                #小計を出力
                if next_month == True:
                    if subtotal_incomes == 0:
                        subtotal_incomes = ""
                    if subtotal_expences == 0:
                        subtotal_expences = ""
                     
                    subtotal_string = str(month) + "月計"
                    
                    writer.writerow(["", "", subtotal_string, 
                     subtotal_incomes, subtotal_expences])
                    
                    subtotal_flag = True  #最後の合計で出力判定するためのもの
                    
                    subtotal_incomes = 0
                    subtotal_expences = 0
                    next_month = False
                
                cnt += 1  #No用カウンター
                month = cash_book.receipt_date.month  #小計の月判別用
                
                #日付をフォーマット
                locale.setlocale(locale.LC_TIME, 'ja_JP.UTF-8')
                dtm_receipt = cash_book.receipt_date.strftime('%Y/%m/%d(%a)')
                
                writer.writerow([cnt, dtm_receipt, cash_book.account_title, 
                     cash_book.incomes, cash_book.expences, cash_book.settlement_date, cash_book.staff])
                
                #合計用カウント
                subtotal_incomes += cash_book.incomes or 0
                total_incomes += cash_book.incomes or 0
                subtotal_expences += cash_book.expences or 0
                total_expences += cash_book.expences or 0
                #
            
            
            #小計・合計を出力
            #小計
            if subtotal_flag == False:
                if subtotal_incomes == 0:
                    subtotal_incomes = ""
                if subtotal_expences == 0:
                    subtotal_expences = ""
                
                subtotal_string = str(month) + "月計"
                
                writer.writerow(["", "", subtotal_string, 
                     subtotal_incomes, subtotal_expences])
            #合計
            if total_incomes == 0:
                total_incomes = ""
            if total_expences == 0:
                total_expences = ""
            writer.writerow(["", "", "合計", 
                     total_incomes, total_expences])
            
    return response
    
#class PostIndex(generic.ListView):
#    model = Post
 
 
#class PostImport(generic.FormView):
#    template_name = 'app/import.html'
#    success_url = reverse_lazy('app:index')
#    form_class = CSVUploadForm
 
#    def form_valid(self, form):
#        # csv.readerに渡すため、TextIOWrapperでテキストモードなファイルに変換
#        csvfile = io.TextIOWrapper(form.cleaned_data['file'])
#        reader = csv.reader(csvfile)
#        # 1行ずつ取り出し、作成していく
#        for row in reader:
#            post, created = Post.objects.get_or_create(pk=row[0])
#            post.title = row[1]
#            post.save()
#        return super().form_valid(form)
 
 
