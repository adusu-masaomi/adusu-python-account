#週末（次）データ作成用
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
#from django.http import HttpResponse
#
from account.models import Partner
from account.models import Account_Title
from account.models import Bank
from account.models import Bank_Branch
from account.models import Payment
from account.models import Cash_Book
from account.models import Cash_Book_Weekly
#
from django.http import Http404, HttpResponse, HttpResponseRedirect, QueryDict
from django.core.urlresolvers import reverse
#from django.template import RequestContext
from django.conf import settings

from django.core.cache import cache
from datetime import datetime, date, timedelta
from account.views import jholiday
from dateutil.relativedelta import relativedelta

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from django.contrib import messages

#for debug
#import pdb; pdb.set_trace()

#週末データ作成（手動）
def set_weekly(request):
    
    save_flag = cache.get('aggregate_save_flag')  #集計のみかデータ保存するかのフラグ
     
    
    temp_date_from = cache.get('search_settlement_date_from')
    temp_date_to = cache.get('search_settlement_date_to')
    
    #import pdb; pdb.set_trace()
    
    #upd 230113
    if (temp_date_from is not None and temp_date_to is not None
       and temp_date_from != "" and temp_date_to != ""):
    #if temp_date_from is not None and temp_date_from == True:
        #temp_date_from += "-01"
        
        dtm_from = datetime.strptime(temp_date_from, '%Y-%m-%d')
        dtm_to = datetime.strptime(temp_date_to, '%Y-%m-%d')
        
        #今週の日曜の日付を取得
        #dtm_pre_week = dtm_from - timedelta(days=1)  #1日マイナス(日曜日と仮定) 
        
        #最大−７にちまで、日曜日を探す
        dtm_pre_week = dtm_from
        for num in range(7):
            if dtm_pre_week.weekday() != 6:
               dtm_pre_week -= timedelta(days=1)  #1日マイナス(日曜日と仮定)
        
        #開始日は、あくまでも直前の月曜とする
        dtm_from = dtm_pre_week + timedelta(days=1)
        
        #assigned_date = dtm_pre_week.date() 
        
        #次週の日曜の日付を取得
        #最大＋７にちまで、日曜日を探す
        dtm_next_week = dtm_to
        for num in range(7):
            if dtm_next_week.weekday() != 6:
                dtm_next_week += timedelta(days=1)   #1日プラス(日曜日と仮定)
        
        balance = 0
        balance_president = 0
        balance_staff = 0
        
        #cash_book_pre_weekly = Cash_Book_Weekly.objects.get(computation_date=assigned_date)
        
        try:
           
            #cash_book_pre_weekly = Cash_Book_Weekly.objects.get(computation_date=dtm_pre_week.date()).first()
            #upd180615
            cash_book_pre_weekly = Cash_Book_Weekly.objects.filter(computation_date=dtm_pre_week.date()).first()
        except ObjectDoesNotExist:
            cash_book_pre_weekly = None
        
        
        if cash_book_pre_weekly is not None:
            #balance += cash_book_pre_weekly.balance
            #週初の残高をまず算出
            balance_president += cash_book_pre_weekly.balance_president
            balance_staff += cash_book_pre_weekly.balance_staff
            balance = balance_president + balance_staff
            
            #週初の残高をキャッシュへ保存
            cache.set('pre_balance', balance, 86400)
            cache.set('pre_balance_president', balance_president, 86400)
            cache.set('pre_balance_staff', balance_staff, 86400)
            
            #指定範囲の差引残高を算出
            cash_books = Cash_Book.objects.filter(settlement_date__gte=dtm_from.date(),
                                settlement_date__lte=dtm_to.date())
            if cash_books is not None:
                for cash_book in cash_books:
                    #upd240427
                    #社長・社員で分けない
                    balance_staff += int(cash_book.incomes or 0)
                    balance_staff -= int(cash_book.expences or 0)
                    
                    #if cash_book.staff_id == settings.ID_STAFF_PRESIDENT:
                    ##社長の場合
                    #    balance_president += int(cash_book.incomes or 0)
                    #    balance_president -= int(cash_book.expences or 0)
                    #else:
                    ##社員の場合
                    #    balance_staff += int(cash_book.incomes or 0)
                    #    balance_staff -= int(cash_book.expences or 0)
                    
                #総残高を算出
                balance = balance_president + balance_staff
            
                #デバッグ
                #import pdb; pdb.set_trace()
                
                if save_flag != "false":
                
                    #翌日曜日へ書き込む
                    #既存データがあれば消去する
                    Cash_Book_Weekly.objects.filter(computation_date=dtm_next_week.date()).delete()
                    #
                    cash_book_weekly = Cash_Book_Weekly()
                
                    cash_book_weekly.computation_date = dtm_next_week
                    cash_book_weekly.balance_president = balance_president
                    cash_book_weekly.balance_staff = balance_staff
                    cash_book_weekly.balance = balance
                
                    cash_book_weekly.save()
                
                    messages.success(request, '週末データ作成が完了しました！')
                    
                    return redirect('account:cash_book_list')
                else:
                    #フラグを消す
                    cache.set('aggregate_save_flag', "", 300)
                   
                    #return HttpResponseRedirect(reverse('account:cash_book_weekly_list'))
                    #import pdb; pdb.set_trace()
        
        #残高をキャッシュに保存する（最後の引数は、保存したい秒数）→２４時間とする
        cache.set('balance', balance, 86400)
        cache.set('balance_president', balance_president, 86400)
        cache.set('balance_staff', balance_staff, 86400)

def caluculate_total(request, results):
#指定期間の収入・支払いの合計を求める
    
    total_incomes = 0
    total_expences = 0
    total_balance = 0
    
    if results is not None:
        for cash_book in results:
            total_incomes += int(cash_book.incomes or 0)
            total_expences += int(cash_book.expences or 0)
        #差引合計
        total_balance = total_incomes - total_expences

        cache.set('total_incomes', total_incomes, 86400)
        cache.set('total_expences', total_expences, 86400)
        cache.set('total_balance', total_balance, 86400)
        
        #import pdb; pdb.set_trace()
        
def date_eliminate_holiday(tmp_date, add_flag):
    
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

