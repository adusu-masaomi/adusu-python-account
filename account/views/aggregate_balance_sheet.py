#貸借表集計データ作成用
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.

from account.models import Balance_Sheet
from account.models import Balance_Sheet_Tally


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

from django.db.models import Sum
from datetime import datetime, date, timedelta

import calendar    #月末日取得用
#for debug
#import pdb; pdb.set_trace()

#資金表見出データ作成
def aggregate_balance_sheet(request):
    
    
    if request.method == 'GET': # If the form is submitted
        search_accrual_date_from_tally = request.GET.get('q_accrual_date_from_tally', None)
        search_accrual_date_to_tally = request.GET.get('q_accrual_date_to_tally', None)
        #キャッシュに保存された検索結果をセット
        if search_accrual_date_from_tally == None:
            search_accrual_date_from_tally = cache.get('search_accrual_date_from_tally')
        if search_accrual_date_to_tally == None:
            search_accrual_date_to_tally = cache.get('search_accrual_date_to_tally')
        #キャッシュへ検索結果をセット（最後の引数は、保存したい秒数）
        cache.set('search_accrual_date_from_tally', search_accrual_date_from_tally, 10800)
        cache.set('search_accrual_date_to_tally', search_accrual_date_to_tally, 10800)
        
        ###フィルタリング
        results = None
        search_flag = False
        
     #search_query_bp_month_from = None
     #search_query_bp_month_to = None
     #if request.method == 'GET': # If the form is submitted
        #search_query_bp_month_from = request.GET.get('q_bp_month_from', None)
        #if search_query_bp_month_from == None:
        #    search_query_bp_month_from = cache.get('search_query_bp_month_from')
        #if search_query_bp_month_from != None:
        #    if len(search_query_bp_month_from) == 10:
        #    #すでに１日が入っている場合、下部で処理するので削っておく
        #        search_query_bp_month_from = search_query_bp_month_from[:-3]
        #if search_query_bp_month_from != None:    
        #    cache.set('search_query_bp_month_from', search_query_bp_month_from, 86400)
        #
        
        accrual_date_from = datetime.strptime(search_accrual_date_from_tally, '%Y-%m-%d')
        accrual_date_to = datetime.strptime(search_accrual_date_to_tally, '%Y-%m-%d')
        
        tmp_date = accrual_date_to - accrual_date_from
        day_count = tmp_date.days
        
        #for i in range(day_count):
        for i in range(day_count + 1):
          
          #日にちを求める
          current_date = accrual_date_from + timedelta(days=i)
          
          #既存データがあれば一旦消去する
          #Balance_Sheet_Tally.objects.filter(accrual_date=current_date).delete()
          
          balance_sheet_tally = Balance_Sheet_Tally.objects.filter(accrual_date=current_date).first()
          
          #if balance_sheet_tally is None:
          if not balance_sheet_tally:
          #新規の場合
            balance_sheet_tally = Balance_Sheet_Tally()
            
            #日付をセット
            balance_sheet_tally.accrual_date = current_date
          #
          
          #集計(貸)
          borrow_amount = Balance_Sheet.objects.filter(accrual_date=current_date, borrow_lend_id=0).\
                                    aggregate(Sum('amount'))
          if borrow_amount:
            
            balance_sheet_tally.borrow_amount = borrow_amount["amount__sum"]
          
          #集計(借)
          lend_amount = Balance_Sheet.objects.filter(accrual_date=current_date, borrow_lend_id=1).\
                                    aggregate(Sum('amount'))
          if lend_amount:
            balance_sheet_tally.lend_amount = lend_amount["amount__sum"]
          
          balance_sheet_tally.save()
    #return HttpResponseRedirect(reverse('account:cash_flow_header_list'))
   

