#資金表見出データ作成用
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
#from django.http import HttpResponse
#
#from account.models import Partner
#from account.models import Account_Title
#from account.models import Bank
#from account.models import Bank_Branch
#from account.models import Payment
#from account.models import Cash_Book
#from account.models import Cash_Book_Weekly

from account.models import Cash_Flow_Header
#from account.models import Cash_Flow_Detail
from account.models import Cash_Flow_Detail_Expected
from account.models import Cash_Flow_Detail_Actual

#
from django.http import Http404, HttpResponse, HttpResponseRedirect, QueryDict
from django.core.urlresolvers import reverse

from django.conf import settings

from django.core.cache import cache
from datetime import datetime, date, timedelta
from account.views import jholiday
from dateutil.relativedelta import relativedelta

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from django.contrib import messages

import calendar    #月末日取得用
from datetime import datetime, date, timedelta
from django.db.models import Avg, Max, Min, Sum

#for debug
#import pdb; pdb.set_trace()

#資金表見出データ作成（手動）
def set_cash_flow(request):
    
    #save_flag = cache.get('aggregate_save_flag')  #集計のみかデータ保存するかのフラグ
    
    search_query_cash_flow_date_from = None
    search_query_cash_flow_date_to = None
    
    #
    
    if request.method == 'GET': # If the form is submitted
        search_query_cash_flow_date_from = request.GET.get('q_cash_flow_date_from', None)
        if search_query_cash_flow_date_from == None:
            search_query_cash_flow_date_from = cache.get('search_query_cash_flow_date_from')
        
        if search_query_cash_flow_date_from != None:
            if len(search_query_cash_flow_date_from) == 10:
            #すでに１日が入っている場合、下部で処理するので削っておく
                search_query_cash_flow_date_from = search_query_cash_flow_date_from[:-3]
         
        #キャッシュからは取らない
        #if search_query_cash_flow_date_from != None:    
        #    cache.set('search_query_cash_flow_date_from', search_query_cash_flow_date_from, 86400)
        
        
    #今日の日付から、今年の1月1日を求める
    first_date = date.today()
    
    if search_query_cash_flow_date_from is None:
        today = date.today()
        tmp_first_date = date(today.year, 1, 1)
        
        tstr = tmp_first_date.strftime('%Y-%m-%d')
        search_query_cash_flow_date_from = tstr[:-3]   #下の計算用に、１日は消しておく
        
        first_date = tmp_first_date  #add200205
    #
    
    date_count = 0
    last_date = date.today()
    search_query_cash_flow_date_only_from = ""
    
    if search_query_cash_flow_date_from:
        
        search_query_cash_flow_date_only_from = search_query_cash_flow_date_from  #月までの文字でも保存しておく
        
        search_query_cash_flow_date_from += "-01"
        
        ###
        #支払予定のデータより、最終の集計日(指定の年間のみで)を求める
        tmp_year = int(search_query_cash_flow_date_from[:-6])  #年だけ抜き取る
        cash_flow_detail_expected_last = Cash_Flow_Detail_Expected.objects.filter(expected_date__year=tmp_year).\
                                                              aggregate(Max('expected_date'))
        
        #cash_flow_detail_expected_last = Cash_Flow_Detail_Expected.objects.all().aggregate(Max('expected_date'))
        
        tmp_last_date = cash_flow_detail_expected_last["expected_date__max"]
        
        if tmp_last_date:   #add200212
        
            #import pdb; pdb.set_trace()
        
            #最終日は、最終の予定日のデータの入ってる月のものとする
            end_year = tmp_last_date.year
            end_month = tmp_last_date.month
        
            #月末日で検索する
            #end_year = int(search_query_cash_flow_date_from[0:4])
            #end_month = int(search_query_cash_flow_date_from[5:7])
        
            _, lastday = calendar.monthrange(end_year,end_month)
       
            #最終日付を求める
            last_date = date(end_year, end_month, lastday)
        
            tmp_days = last_date-first_date
        
            #import pdb; pdb.set_trace()
            date_count = (last_date-first_date).days
        
            #開始日を再セット
            first_date = datetime.strptime(search_query_cash_flow_date_from, '%Y-%m-%d')

        
    #if search_query_cash_flow_date_from is not None:
    if search_query_cash_flow_date_from is not None and date_count > 0:
        
        #import pdb; pdb.set_trace()
        
        #for i in range(lastday):
        for i in range(date_count):
        #0~月末日-1日でループ
            
            #集計用変数をリセット
            expected_expense = 0
            actual_expense = 0
            expected_income = 0
            actual_income=0
            expected_hokuetsu=0
            actual_hokuetsu=0
            expected_sanshin_tsukanome=0
            actual_sanshin_tsukanome=0
            expected_sanshin_main=0
            actual_sanshin_main=0
            expected_cash_president=0
            actual_cash_president=0
            expected_cash_company=0
            actual_cash_company=0
            #
            
            #tmpDay = str(i+1).zfill(2)
            
            cash_flow_date = first_date + timedelta(days=i)
            
            #if cash_flow_date == datetime(2020, 3, 10, 0, 0):
            #    import pdb; pdb.set_trace()
            
            
            #文字→日付へ変換
            #string_date = search_query_cash_flow_date_only_from + "-" + tmpDay
            #cash_flow_date = datetime.strptime(string_date, '%Y-%m-%d')
            
            #日付をセットし明細データを取得、ループ開始
            results = Cash_Flow_Detail_Expected.objects.all().filter(expected_date=cash_flow_date)
            
            #実績データ
            results_actual = Cash_Flow_Detail_Actual.objects.all().filter(actual_date=cash_flow_date)
            
            #既存データがあれば一旦消去する(見出データ)
            #Cash_Flow_Header.objects.filter(cash_flow_date=cash_flow_date).delete()
            cash_flow_header = Cash_Flow_Header.objects.filter(cash_flow_date=cash_flow_date).first()
            
            #if not results:  
            if not results and not results_actual:
                #集計結果がなくても(予定・実際)空の日付データも作る(データない場合)
                if not cash_flow_header:
                    cash_flow_header = Cash_Flow_Header()
                    cash_flow_header.cash_flow_date = cash_flow_date
                cash_flow_header.save()
                
                #messages.success(request, '週末データ作成が完了しました！')
            else:
                #データ存在(予定)している場合、明細データを集計して見出しへセット
                if results:
                    for cash_flow_detail_expected in results:
                        #収支一時集計用変数
                        tmp_expected_bp = 0
                        #tmp_actual_bp = 0
                   
                        #支出へプラス
                        expected_expense += cash_flow_detail_expected.expected_expense
                        #actual_expense += cash_flow_detail_expected.actual_expense
                   
                        tmp_expected_bp -= cash_flow_detail_expected.expected_expense
                        #tmp_actual_bp -= cash_flow_detail_expected.actual_expense
                   
                        #if expected_expense > 0:
                        #    import pdb; pdb.set_trace()
                   
                        #収入へプラス
                        expected_income += cash_flow_detail_expected.expected_income
                        #actual_income += cash_flow_detail_expected.actual_income
                   
                        tmp_expected_bp += cash_flow_detail_expected.expected_income
                        #tmp_actual_bp += cash_flow_detail_expected.actual_income
                   
                        #銀行ごとに振り分ける
                        if cash_flow_detail_expected.payment_bank_id == 1:
                            #北越
                            expected_hokuetsu += tmp_expected_bp
                            #actual_hokuetsu += tmp_actual_bp
                        elif cash_flow_detail_expected.payment_bank_id == 3:  #upd200120
                        
                            if cash_flow_detail_expected.payment_bank_branch_id != settings.ID_BANK_BRANCH_SANSHIN_MAIN:  #本店以外--要定数化:
                                #三信(塚野目)
                                expected_sanshin_tsukanome += tmp_expected_bp
                                #actual_sanshin_tsukanome += tmp_actual_bp
                            else:
                                #三信(本店)
                                expected_sanshin_main += tmp_expected_bp
                                #actual_sanshin_main += tmp_actual_bp
                        elif cash_flow_detail_expected.cash_id == 1:
                            #現金の場合→ひとまず会社現金のみとする
                            expected_cash_company += tmp_expected_bp
                            #actual_cash_company += tmp_actual_bp
                     
                        #工事データはほくぎん以外は、三信塚野目しか入らないものとする
                        #elif cash_flow_detail_expected.payment_bank_id == 4:  #upd200120
                        #    #三信(本店)
                        #    expected_sanshin_main += tmp_expected_bp
                        #    actual_sanshin_main += tmp_actual_bp
                
                #データ(実際)存在している場合、明細データを集計して見出しへセット
                if results_actual:
                    for cash_flow_detail_actual in results_actual:
                    #収支一時集計用変数
                        tmp_actual_bp = 0
                   
                        #支出へプラス
                        actual_expense += cash_flow_detail_actual.actual_expense
                        tmp_actual_bp -= cash_flow_detail_actual.actual_expense
                   
                        #収入へプラス
                        actual_income += cash_flow_detail_actual.actual_income
                        tmp_actual_bp += cash_flow_detail_actual.actual_income
                   
                        #銀行ごとに振り分ける
                        if cash_flow_detail_actual.payment_bank_id == 1:
                            #北越
                            actual_hokuetsu += tmp_actual_bp
                        elif cash_flow_detail_actual.payment_bank_id == 3:  
                        
                            if cash_flow_detail_actual.payment_bank_branch_id != settings.ID_BANK_BRANCH_SANSHIN_MAIN:  #本店以外--要定数化:
                                #三信(塚野目)
                                actual_sanshin_tsukanome += tmp_actual_bp
                            else:
                                #三信(本店)
                                actual_sanshin_main += tmp_actual_bp
                        elif cash_flow_detail_actual.cash_id == 1:
                            #現金の場合→ひとまず会社現金のみとする
                            actual_cash_company += tmp_actual_bp
                
                #ループ後にカラムへセット
                if not cash_flow_header:
                    cash_flow_header = Cash_Flow_Header()
                    cash_flow_header.cash_flow_date = cash_flow_date
                
                #支出
                cash_flow_header.expected_expense = expected_expense
                cash_flow_header.actual_expense = actual_expense
                #収入
                cash_flow_header.expected_income = expected_income
                cash_flow_header.actual_income = actual_income
                #北越
                cash_flow_header.expected_hokuetsu = expected_hokuetsu
                cash_flow_header.actual_hokuetsu = actual_hokuetsu
                #三信(塚野目)
                cash_flow_header.expected_sanshin_tsukanome = expected_sanshin_tsukanome
                cash_flow_header.actual_sanshin_tsukanome = actual_sanshin_tsukanome
                #三信(本店)
                cash_flow_header.expected_sanshin_main = expected_sanshin_main
                cash_flow_header.actual_sanshin_main = actual_sanshin_main
                
                #現金(会社)
                cash_flow_header.expected_cash_company = expected_cash_company
                cash_flow_header.actual_cash_company = actual_cash_company
                
                #保存
                cash_flow_header.save()          
            
         
    return HttpResponseRedirect(reverse('account:cash_flow_header_list'))
   

