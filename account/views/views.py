from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from account.models import Partner
from account.models import Account_Title
from account.models import Bank
from account.models import Bank_Branch
from account.models import Payment
from account.models import Payment_Reserve
from account.models import Cash_Book
from account.models import Staff
from account.models import Cash_Book_Weekly
from account.models import Cash_Flow_Header
#from account.models import Cash_Flow_Detail
from account.models import Cash_Flow_Detail_Expected
from account.models import Cash_Flow_Detail_Actual
from account.models import Balance_Sheet
from account.models import Balance_Sheet_Tally
#
from account.forms import PartnerForm
from account.forms import Account_TitleForm
from account.forms import BankForm
from account.forms import Bank_BranchForm
from account.forms import PaymentForm
from account.forms import Payment_ReserveForm
from account.forms import Cash_BookForm
from account.forms import Cash_Book_WeeklyForm
from account.forms import Cash_Flow_HeaderForm
from account.forms import Balance_SheetForm

import json 
from itertools import chain
from django.core.cache import cache
from django.db.models import Sum

from django.http import Http404, HttpResponse, QueryDict
from django.template import RequestContext
#from django.core.urlresolvers import reverse

from account.views import aggregate_weekly as Aggregate
from account.views import aggregate_cash_flow as Aggregate_Cash_Flow  #add200115
from account.views import aggregate_balance_sheet as Aggregate_Balance_Sheet_Tally
from account.views import set_cash_flow_detail as Set_Cash_Flow_Detail  #add200121
from account.views import set_cash_book_to_balance_sheet as Set_Cash_Book_To_Balance_Sheet    #add200124

#ログイン用
#from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
from django.views.generic import View
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
#
from datetime import datetime, date, timedelta
import calendar    #月末日取得用  add180911
from django.db.models import Sum

#ログイン用
@python_2_unicode_compatible
class Index(View):
    @method_decorator(login_required)
    def get(self, request):
        return render(request, 'account/index.html')

def index(request):
    
    #not work.....
    #partners = Partner.objects.order_by('order')
    #context_dict = {'partners': partners}
    #return render(request,
    #              'base.html',     # 使用するテンプレート
    #              {context_dict})         # テンプレートに渡すデータ
                  
    #return HttpResponse("Hello World !")
    return render(request,
                  'base.html',     # 使用するテンプレート
                  {})         # テンプレートに渡すデータ
def cash_flow_header_list(request):
    """資金繰り表"""
    
    #
    #import pdb; pdb.set_trace()
    
    if request.method == 'GET': # If the form is submitted
        
        search_query_bp_month_from = request.GET.get('q_bp_month_from', None)
        
        if search_query_bp_month_from == None:
            search_query_bp_month_from = cache.get('search_query_bp_month_from')
        
        if search_query_bp_month_from != None:
            if len(search_query_bp_month_from) == 10:
            #すでに１日が入っている場合、下部で処理するので削っておく
                #search_query_bp_month_from = search_query_bp_month_from.rstrip("-01")
                search_query_bp_month_from = search_query_bp_month_from[:-3]
        if search_query_bp_month_from != None:
            cache.set('search_query_bp_month_from', search_query_bp_month_from, 86400)
        
        if 'button_2' in request.GET: 
        #集計の場合、別途集計データを作成する
            #import pdb; pdb.set_trace()
            Aggregate_Cash_Flow.set_cash_flow(request)
        
        #画面表示用の結果を抽出
        if search_query_bp_month_from:
        
            search_query_bp_month_only_from = search_query_bp_month_from  #月までの文字でも保存しておく
            
            search_query_bp_month_from += "-01"
        
            #月末日で検索する
            end_year = int(search_query_bp_month_from[0:4])
            end_month = int(search_query_bp_month_from[5:7])
            
            _, lastday = calendar.monthrange(end_year,end_month)
        
        results = None
        
        if search_query_bp_month_from is not None:
        
            #for i in range(lastday):
            #0~月末日-1日でループ
            #    tmpDay = str(i+1).zfill(2)
            
            
            #文字→日付へ変換
            #開始日
            string_date = search_query_bp_month_only_from + "-" + "01"
            cash_flow_date_from = datetime.strptime(string_date, '%Y-%m-%d')
            
            #終了日
            string_date = search_query_bp_month_only_from + "-" + str(lastday).zfill(2)
            cash_flow_date_to = datetime.strptime(string_date, '%Y-%m-%d')
            

            #日付範囲をセットし見出データを取得
            results = Cash_Flow_Header.objects.all().filter(cash_flow_date__gte=cash_flow_date_from, cash_flow_date__lte=cash_flow_date_to)
            
            #各合計
            #支出
            sum_expected_expense = results.aggregate(Sum('expected_expense'))
            sum_actual_expense = results.aggregate(Sum('actual_expense'))
            #収入
            sum_expected_income = results.aggregate(Sum('expected_income'))
            sum_actual_income = results.aggregate(Sum('actual_income'))
            #北越
            sum_expected_hokuetsu = results.aggregate(Sum('expected_hokuetsu'))
            sum_actual_hokuetsu = results.aggregate(Sum('actual_hokuetsu'))
            #三信(塚野目)
            sum_expected_sanshin_tsukanome = results.aggregate(Sum('expected_sanshin_tsukanome'))
            sum_actual_sanshin_tsukanome  = results.aggregate(Sum('actual_sanshin_tsukanome'))
            #三信(本店)
            sum_expected_sanshin_main = results.aggregate(Sum('expected_sanshin_main'))
            sum_actual_sanshin_main  = results.aggregate(Sum('actual_sanshin_main'))
            #現金(社長)
            sum_expected_cash_president = results.aggregate(Sum('expected_cash_president'))
            sum_actual_cash_president  = results.aggregate(Sum('actual_cash_president'))
            #現金(会社)
            sum_expected_cash_company = results.aggregate(Sum('expected_cash_company'))
            sum_actual_cash_company  = results.aggregate(Sum('actual_cash_company'))
            #
            if results:
                #日付順にする
                results = results.order_by('cash_flow_date')
                
        #
        #import pdb; pdb.set_trace()
        if results:
            return render(request,
                 'account/cash_flow_header_list.html',     # 使用するテンプレート
                  {'cash_flow_headers':results, 'sum_expected_expense': sum_expected_expense["expected_expense__sum"], 'sum_actual_expense': sum_actual_expense["actual_expense__sum"],
                                                'sum_expected_income': sum_expected_income["expected_income__sum"], 'sum_actual_income': sum_actual_income["actual_income__sum"],
                                                'sum_expected_hokuetsu': sum_expected_hokuetsu["expected_hokuetsu__sum"], 'sum_actual_hokuetsu': sum_actual_hokuetsu["actual_hokuetsu__sum"],
                                                'sum_expected_sanshin_tsukanome': sum_expected_sanshin_tsukanome["expected_sanshin_tsukanome__sum"], 'sum_actual_sanshin_tsukanome': sum_actual_sanshin_tsukanome["actual_sanshin_tsukanome__sum"],
                                                'sum_expected_sanshin_main': sum_expected_sanshin_main["expected_sanshin_main__sum"], 'sum_actual_sanshin_main': sum_actual_sanshin_main["actual_sanshin_main__sum"],
                                                'sum_expected_cash_president': sum_expected_cash_president["expected_cash_president__sum"], 'sum_actual_cash_president': sum_actual_cash_president["actual_cash_president__sum"],
                                                'sum_expected_cash_company': sum_expected_cash_company["expected_cash_company__sum"], 'sum_actual_cash_company': sum_actual_cash_company["actual_cash_company__sum"],
                                                'search_query_bp_month_from': search_query_bp_month_from})
        else:
            return render(request,
                 'account/cash_flow_header_list.html',     # 使用するテンプレート
                  {'cash_flow_headers':results, 
                                   'search_query_bp_month_from': search_query_bp_month_from})
            
##### 一覧ビュー #####
def partner_list(request):
    """取引先の一覧"""
    #return HttpResponse('取引先の一覧')
    partners = Partner.objects.all().order_by('id')
    if request.method == 'GET': # If the form is submitted
        search_query = request.GET.get('q', None)
        if search_query:
            results = Partner.objects.all().filter(trade_division_id__icontains=search_query)
            #import pdb; pdb.set_trace()
            return render(request,
                'account/partner_list.html',     # 使用するテンプレート
                {'partners': results})         # テンプレートに渡すデータ
        else:
            return render(request,
                'account/partner_list.html',     # 使用するテンプレート
                {'partners': partners})         # テンプレートに渡すデータ
    #return render(request,
    #              'account/partner_list.html',     # 使用するテンプレート
    #              {'partners': partners})         # テンプレートに渡すデータ
def account_title_list(request):
    """勘定科目の一覧"""
    #デバッグ
    #import pdb; pdb.set_trace()
    #return HttpResponse('勘定科目の一覧')
    account_titles = Account_Title.objects.all().order_by('id')
    
    # Your code
    if request.method == 'GET': # If the form is submitted
        search_query = request.GET.get('q', None)
        search_query_trade = request.GET.get('q_trade', None)
        
        if search_query:
            if search_query_trade:
              #勘定科目＆取引区分で検索
                results = Account_Title.objects.all().filter(name__icontains=search_query, trade_division_id__icontains=search_query_trade)
            else:
              #勘定科目のみで検索
                results = Account_Title.objects.all().filter(name__icontains=search_query)
            #import pdb; pdb.set_trace()
            return render(request,
                'account/account_title_list.html',     # 使用するテンプレート
                {'account_titles': results})         # テンプレートに渡すデータ
        elif search_query_trade:
        #取引区分のみで検索
            results = Account_Title.objects.all().filter(trade_division_id__icontains=search_query_trade)
            return render(request,
                'account/account_title_list.html',     # 使用するテンプレート
                {'account_titles': results})         # テンプレートに渡すデータ
        else:
            return render(request,
                'account/account_title_list.html',     # 使用するテンプレート
                {'account_titles': account_titles})         # テンプレートに渡すデータ
    #return render(request,
    #              'account/account_title_list.html',     # 使用するテンプレート
    #              {'account_titles': account_titles})         # テンプレートに渡すデータ
def bank_list(request):
    """銀行の一覧"""
    #デバッグ
    #import pdb; pdb.set_trace()
    
    #return HttpResponse('銀行目の一覧')
    banks = Bank.objects.all().order_by('id')
    
    # Your code
    return render(request,
                  'account/bank_list.html',     # 使用するテンプレート
                  {'banks': banks})         # テンプレートに渡すデータ

def bank_branch_list(request):
    """銀行支店の一覧"""
    #デバッグ
    #import pdb; pdb.set_trace()
    
    #return HttpResponse('銀行目の一覧')
    bank_branchs = Bank_Branch.objects.all().order_by('id')
    
    # Your code
    return render(request,
                  'account/bank_branch_list.html',     # 使用するテンプレート
                  {'bank_branchs': bank_branchs})         # テンプレートに渡すデータ

    
def payment_list(request, number=None):
    """支払の一覧"""
    
    #return HttpResponse('◯◯◯の一覧')
    #payments = Payment.objects.all().order_by('id')
    payments = Payment.objects.all().order_by('order')
    
    #検索フォーム用に取引先も取得 
    #add180403
    partners = Partner.objects.order_by('order')
    
    if request.method == 'GET': # If the form is submitted
        
        search_query_trade_division_id = request.GET.get('q_trade_division_id', None)
        #
        search_query_pay_month_from = request.GET.get('q_pay_month_from', None)
        search_query_pay_month_to = request.GET.get('q_pay_month_to', None)
        #
        search_query_month_from = request.GET.get('q_month_from', None)
        search_query_month_to = request.GET.get('q_month_to', None)
        search_query_payment = request.GET.get('q_payment', None)
        search_query_partner = request.GET.get('q_partner', None)
        search_query_paid = request.GET.get('q_paid', None)
        
        #キャッシュに保存された検索結果をセット
        if search_query_trade_division_id == None:
            search_query_trade_division_id = cache.get('search_query_trade_division_id')
        
        #add180911
        #支払開始年月
        if search_query_pay_month_from == None:
            search_query_pay_month_from = cache.get('search_query_pay_month_from')
        if search_query_pay_month_to == None:
            search_query_pay_month_to = cache.get('search_query_pay_month_to')
        #
        
        if search_query_month_from == None:
            search_query_month_from = cache.get('search_query_month_from')
            
        if search_query_month_to == None:
            search_query_month_to = cache.get('search_query_month_to')
        #add180524
        if search_query_trade_division_id == None:
            search_query_trade_division_id = cache.get('search_query_trade_division_id')
        if search_query_payment == None:
            search_query_payment = cache.get('search_query_payment')
        if search_query_partner == None:
            search_query_partner = cache.get('search_query_partner')
        if search_query_paid == None:
            search_query_paid = cache.get('search_query_paid')
        #
        #キャッシュへ検索結果をセット（最後の引数は、保存したい秒数）
        cache.set('search_query_trade_division_id', search_query_trade_division_id, 86400)
        #add180911
        cache.set('search_query_pay_month_from', search_query_pay_month_from, 86400)
        cache.set('search_query_pay_month_to', search_query_pay_month_to, 86400)
        #add end
        cache.set('search_query_month_from', search_query_month_from, 86400)
        cache.set('search_query_month_to', search_query_month_to, 86400)
        cache.set('search_query_trade_division_id', search_query_trade_division_id, 10800)
        cache.set('search_query_payment', search_query_payment, 10800)
        cache.set('search_query_partner', search_query_partner, 10800)
        cache.set('search_query_paid', search_query_paid, 10800)
        #
        
        ###フィルタリング
        results = None
        search_flag = False
        search_flag_pay_day = False
        multi_month = False
        search_query_pay_month_from_saved = ""
        
        
        #del190411
        #支払開始日の絞り込みはなしにする（あくまでも指定月以下で未払のものを検索）
        if search_query_pay_month_from:
        #年月で絞り込み(支払開始年月日)
        
            search_flag = True
            search_flag_pay_day = True
            #◯月１日で検索するようにする
            search_query_pay_month_from_saved = search_query_pay_month_from
            search_query_pay_month_from += "-01"
            
            if search_query_paid and search_query_paid == "1":
            #upd190514
            #支払済のものだけ検索した場合に、検索開始月のフィルターを有効にする
                results = Payment.objects.all().filter(payment_due_date__gte=search_query_pay_month_from)
        
        if search_query_pay_month_to:
        #年月で絞り込み(支払終了年月日)
            search_flag = True
            search_flag_pay_day = True
            #複数月で検索しているか判定
            if search_query_pay_month_from_saved < search_query_pay_month_to:
                multi_month = True
            #月末日を求める
            end_year = int(search_query_pay_month_to[0:4])
            end_month = int(search_query_pay_month_to[5:7])
            
            _, lastday = calendar.monthrange(end_year,end_month)
            
            #◯月１日で検索するようにする
            #search_query_pay_month_to += "-01"
            #指定月末日で検索するようにする
            search_query_pay_month_to += "-" + str(lastday)
            
            #import pdb; pdb.set_trace()
            
            if results is None:
                results = Payment.objects.all().filter(payment_due_date__lte=search_query_pay_month_to)
            else:
                results = results.filter(payment_due_date__lte=search_query_pay_month_to)
                
        if search_query_month_from:
        #年月で絞り込み(請求開始年月日)
            search_flag = True
            #◯月１日で検索するようにする
            search_query_month_from += "-01"
            #results = Payment.objects.all().filter(billing_year_month__gte=search_query_month_from).order_by('order')
            if results is None:
                results = Payment.objects.all().filter(billing_year_month__gte=search_query_month_from)
            else:
                results = results.filter(billing_year_month__gte=search_query_month_from)
                
        if search_query_month_to:
        #年月で絞り込み(請求終了年月日)
            search_flag = True
            #◯月１日で検索するようにする
            search_query_month_to += "-01"
            if results is None:
                #results = Payment.objects.all().filter(billing_year_month__lte=search_query_month_to).order_by('order')
                results = Payment.objects.all().filter(billing_year_month__lte=search_query_month_to)
            else:
                #results = results.filter(billing_year_month__lte=search_query_month_to).order_by('order')
                results = results.filter(billing_year_month__lte=search_query_month_to)
            
        if search_query_trade_division_id:
        #取引区分で絞り込み
            search_flag = True
            if results is None:
                #results = Payment.objects.all().filter(trade_division_id__icontains=search_query_trade_division_id).order_by('order')
                results = Payment.objects.all().filter(trade_division_id__icontains=search_query_trade_division_id)
            else:
                #results = results.filter(trade_division_id__icontains=search_query_trade_division_id).order_by('order')
                results = results.filter(trade_division_id__icontains=search_query_trade_division_id)
        
        if search_query_payment:
        #支払方法で絞り込み
            search_flag = True
            if results is None:
                #results = Payment.objects.all().filter(payment_method_id__icontains=search_query_payment).order_by('order')
                results = Payment.objects.all().filter(payment_method_id__icontains=search_query_payment)
            else:
                #results = results.filter(payment_method_id__icontains=search_query_payment).order_by('order')
                results = results.filter(payment_method_id__icontains=search_query_payment)
        
        if search_query_partner:
        #支払先で絞り込み
            search_flag = True
            if results is None:
                #results = Payment.objects.all().filter(partner_id=search_query_partner).order_by('order')
                results = Payment.objects.all().filter(partner_id=search_query_partner)
            else:
                #results = results.filter(partner_id=search_query_partner).order_by('order')
                results = results.filter(partner_id=search_query_partner)
        
        if search_query_paid:
        #支払状況で絞り込み
            if search_query_paid == "0":
                search_flag = True
                if results is None:
                    results = Payment.objects.all().filter(payment_date__isnull=True).order_by('order')
                else:
                    results = results.filter(payment_date__isnull=True)
                #results = results.order_by('partner_id', 'billing_year_month', 'order')
            elif search_query_paid == "1":
            #支払済
                search_flag = True
                if results is None:
                    results = Payment.objects.all().filter(payment_date__isnull=False)
                else:
                    results = results.filter(payment_date__isnull=False)
                #results = results.order_by('partner_id', 'billing_year_month', 'order')
        
        else:
            #支払済未選択の場合でも、支払日検索の場合は”未”の扱いとする
            #(社長仕様)
            if search_query_pay_month_from:
                search_flag = True
                if results is None:
                    results = Payment.objects.all().filter(payment_date__isnull=True).order_by('order')
                else:
                    results = results.filter(payment_date__isnull=True)
        ###
        
        
        #sort_by = request.GET.get('sort_by')
        #if sort_by is not None:
        #    results = results.order_by(sort_by)
        
        #if (search_query_trade_division_id or search_query_month):
        if search_flag == True:
        #検索クエリーが入力されている場合のみ
            
            #upd180719
            #並び順を最後に変更
            #results = results.order_by('partner_id', 'billing_year_month', 'order')
            if search_flag_pay_day == False:
                results = results.order_by('trade_division_id', 'partner_id', 'billing_year_month', 'order')
            else:
            #支払日検索の場合
            #add 180911
                if multi_month == True:
                #単月の場合、取引区分+支払先マスター順
                    results = results.order_by('trade_division_id', 'partner_id', 'payment_due_date', 'order')
                else:
                #複数月の場合、支払日順
                    results = results.order_by('payment_due_date', 'order', 'partner_id')
            #合計金額
            total_price = results.aggregate(Sum('billing_amount'))
            
            #日付は再び年月のみにする
            #search_query_month_from = search_query_month_from.rstrip("-01")
            #search_query_month_to = search_query_month_to.rstrip("-01")
            #upd180615 上記は１月も消えてしまう
            if search_query_month_from:
                search_query_month_from = search_query_month_from[:-3]
            if search_query_month_to:
                search_query_month_to = search_query_month_to[:-3]
            #
            if search_query_pay_month_from:
                search_query_pay_month_from = search_query_pay_month_from[:-3]
            if search_query_pay_month_to:
                search_query_pay_month_to = search_query_pay_month_to[:-3]
                       
            return render(request,
                'account/payment_list.html',     # 使用するテンプレート
                {'payments': results, 'partners': partners, 'total_price': total_price, 
                  'search_query_pay_month_from': search_query_pay_month_from,
                  'search_query_pay_month_to': search_query_pay_month_to,
                  'search_query_month_from': search_query_month_from,
                  'search_query_month_to': search_query_month_to, 
                  'search_query_trade_division_id': search_query_trade_division_id, 
                  'search_query_payment': search_query_payment, 'search_query_partner': search_query_partner, 
                  'search_query_paid': search_query_paid})         # テンプレートに渡すデータ
        else:
            
                return render(request,
                'account/payment_list.html',     # 使用するテンプレート
                {'payments': payments, 'partners': partners })         # テンプレートに渡すデータ

def payment_reserve_list(request, number=None):
    """支払予約の一覧"""
    
    payment_reserves = Payment_Reserve.objects.all().order_by('order')
    
    #検索フォーム用に取引先も取得 
    #add180403
    partners = Partner.objects.order_by('order')
    
    if request.method == 'GET': # If the form is submitted
        
        search_query_trade_division_id = request.GET.get('q_trade_division_id', None)
        #
        #search_query_pay_month_from = request.GET.get('q_pay_month_from', None)
        #search_query_pay_month_to = request.GET.get('q_pay_month_to', None)
        #
        search_query_month_from = request.GET.get('q_month_from', None)
        search_query_month_to = request.GET.get('q_month_to', None)
        search_query_payment = request.GET.get('q_payment', None)
        search_query_partner = request.GET.get('q_partner', None)
        #search_query_partner = None
        search_query_paid = request.GET.get('q_paid', None)
        
        #キャッシュに保存された検索結果をセット
        #if search_query_trade_division_id == None:
        #    search_query_trade_division_id = cache.get('search_query_trade_division_id')
        
        #add180911
        #支払開始年月
        #if search_query_pay_month_from == None:
        #    search_query_pay_month_from = cache.get('search_query_pay_month_from')
        #if search_query_pay_month_to == None:
        #    search_query_pay_month_to = cache.get('search_query_pay_month_to')
        #
        
        if search_query_month_from == None:
            search_query_month_from = cache.get('search_query_month_from')
            
        if search_query_month_to == None:
            search_query_month_to = cache.get('search_query_month_to')
        #if search_query_trade_division_id == None:
        #    search_query_trade_division_id = cache.get('search_query_trade_division_id')
        #if search_query_payment == None:
        #    search_query_payment = cache.get('search_query_payment')
        if search_query_partner == None:
            search_query_partner = cache.get('search_query_partner')
        #if search_query_paid == None:
        #    search_query_paid = cache.get('search_query_paid')
        
        #
        #キャッシュへ検索結果をセット（最後の引数は、保存したい秒数）
        cache.set('search_query_trade_division_id', search_query_trade_division_id, 86400)
        #cache.set('search_query_pay_month_from', search_query_pay_month_from, 86400)
        #cache.set('search_query_pay_month_to', search_query_pay_month_to, 86400)
        cache.set('search_query_month_from', search_query_month_from, 86400)
        cache.set('search_query_month_to', search_query_month_to, 86400)
        cache.set('search_query_trade_division_id', search_query_trade_division_id, 10800)
        cache.set('search_query_payment', search_query_payment, 10800)
        cache.set('search_query_partner', search_query_partner, 10800)
        #cache.set('search_query_paid', search_query_paid, 10800)
        #
        
        #フィルタリング
        results = None
        search_flag = False
        search_flag_pay_day = False
        multi_month = False
        search_query_pay_month_from_saved = ""
        
            
        if search_query_month_from:
        #年月で絞り込み(請求開始年月日)
            search_flag = True
            #◯月１日で検索するようにする
            search_query_month_from += "-01"
            if results is None:
                results = Payment_Reserve.objects.all().filter(billing_year_month__gte=search_query_month_from)
            else:
                results = results.filter(billing_year_month__gte=search_query_month_from)
                
        if search_query_month_to:
        #年月で絞り込み(請求終了年月日)
            search_flag = True
            #◯月１日で検索するようにする
            search_query_month_to += "-01"
            if results is None:
                results = Payment_Reserve.objects.all().filter(billing_year_month__lte=search_query_month_to)
            else:
                results = results.filter(billing_year_month__lte=search_query_month_to)
        
        if search_query_partner:
        #支払先で絞り込み
            search_flag = True
            if results is None:
                results = Payment_Reserve.objects.all().filter(partner_id=search_query_partner)
            else:
                results = results.filter(partner_id=search_query_partner)
        
        if search_query_payment:
        #支払方法で絞り込み
            search_flag = True
            if results is None:
                results = Payment_Reserve.objects.all().filter(payment_method_id__icontains=search_query_payment)
            else:
                results = results.filter(payment_method_id__icontains=search_query_payment)
        
        if search_query_trade_division_id:
        #取引区分で絞り込み
            search_flag = True
            if results is None:
                results = Payment_Reserve.objects.all().filter(trade_division_id__icontains=search_query_trade_division_id)
            else:
                results = results.filter(trade_division_id__icontains=search_query_trade_division_id)
       
        
        if search_flag == True:
        #検索クエリーが入力されている場合のみ
            
            #並び順を最後に変更
            if search_flag_pay_day == False:
                results = results.order_by('trade_division_id', 'partner_id', 'billing_year_month', 'order')
            else:
            #支払日検索の場合
                if multi_month == True:
                #単月の場合、取引区分+支払先マスター順
                    results = results.order_by('trade_division_id', 'partner_id', 'payment_due_date', 'order')
                else:
                #複数月の場合、支払日順
                    results = results.order_by('payment_due_date', 'order', 'partner_id')
            #合計金額
            total_price = results.aggregate(Sum('billing_amount'))
            
            if search_query_month_from:
                search_query_month_from = search_query_month_from[:-3]
            if search_query_month_to:
                search_query_month_to = search_query_month_to[:-3]
            #
            #if search_query_pay_month_from:
            #    search_query_pay_month_from = search_query_pay_month_from[:-3]
            #if search_query_pay_month_to:
            #    search_query_pay_month_to = search_query_pay_month_to[:-3]
            
            
            #test
            #return render(request,
            #    'account/payment_reserve_list.html',     # 使用するテンプレート
            #    {'payment_reserves': payment_reserves, 'partners': partners })         # テンプレートに渡すデータ
                
            return render(request,
                'account/payment_reserve_list.html',     # 使用するテンプレート
                {'payment_reserves': results, 'partners': partners, 'total_price': total_price, 
                  'search_query_month_from': search_query_month_from,
                  'search_query_month_to': search_query_month_to, 
                  'search_query_trade_division_id': search_query_trade_division_id, 
                  'search_query_partner': search_query_partner 
                  })         # テンプレートに渡すデータ
        else:
            
                return render(request,
                'account/payment_reserve_list.html',     # 使用するテンプレート
                {'payment_reserves': payment_reserves, 'partners': partners })         # テンプレートに渡すデータ
        
def cash_book_list(request):
    """出納帳の一覧"""
    #return HttpResponse('取引先の一覧')
    #cash_books = Cash_Book.objects.all().order_by('id')
    cash_books = Cash_Book.objects.all().order_by('settlement_date', 'order')
    
    #検索フォーム用に勘定科目も取得 
    account_titles = Account_Title.objects.all().order_by('order')
    #検索フォーム用に社員も取得 
    staffs = Staff.objects.all()
    
    #デバッグ
    #import pdb; pdb.set_trace()
    
    
    if request.method == 'GET': # If the form is submitted
        
        #form = Cash_BookForm(request.GET or None)
        
        
        #import pdb; pdb.set_trace()
        
        
        search_settlement_date_from = request.GET.get('q_settlement_date_from', None)
        search_settlement_date_to = request.GET.get('q_settlement_date_to', None)
        
        search_receipt_date_from = request.GET.get('q_receipt_date_from', None)
        search_receipt_date_to = request.GET.get('q_receipt_date_to', None)
        
        search_account_title = request.GET.get('q_account_title', None)
        search_staff = request.GET.get('q_staff', None)
        search_not_staff = request.GET.get('q_not_staff', None)
        
        
        #キャッシュに保存された検索結果をセット
        if search_settlement_date_from == None:
            search_settlement_date_from = cache.get('search_settlement_date_from')
        if search_settlement_date_to == None:
            search_settlement_date_to = cache.get('search_settlement_date_to')
        if search_receipt_date_from == None:
            search_receipt_date_from = cache.get('search_receipt_date_from')
        if search_receipt_date_to == None:
            search_receipt_date_to = cache.get('search_receipt_date_to')
        if search_account_title == None:
            search_account_title = cache.get('search_account_title')
        if search_staff == None:
            search_staff = cache.get('search_staff')
        if search_not_staff == None:
            search_not_staff = cache.get('search_not_staff')
        #
        
        #add180524
        #search_context = {"search_account_title":search_account_title, "search_staff":search_staff}
        
        #キャッシュへ検索結果をセット（最後の引数は、保存したい秒数）
        cache.set('search_settlement_date_from', search_settlement_date_from, 10800)
        cache.set('search_settlement_date_to', search_settlement_date_to, 10800)
        cache.set('search_receipt_date_from', search_receipt_date_from, 10800)
        cache.set('search_receipt_date_to', search_receipt_date_to, 10800)
        cache.set('search_account_title', search_account_title, 10800)
        cache.set('search_staff', search_staff, 10800)
        cache.set('search_not_staff', search_not_staff, 10800)
        #
        ###フィルタリング
        results = None
        search_flag = False
        
        #請求日で検索していたら請求日を並び順にする
        if search_settlement_date_from:
            order_date = "settlement_date"
        else:
            order_date = "receipt_date"
        #
        
        
        if search_settlement_date_from:
        #請求日で絞り込み(開始)
            
            search_flag = True
            results = Cash_Book.objects.all().filter(settlement_date__gte=search_settlement_date_from).order_by('settlement_date', 'order')
        
        if search_settlement_date_to:
        #請求日で絞り込み(終了)
            search_flag = True
            if results is None:
                results = Cash_Book.objects.all().filter(settlement_date__lte=search_settlement_date_to).order_by('settlement_date', 'order')
            else:
                results = results.filter(settlement_date__lte=search_settlement_date_to).order_by('settlement_date', 'order')
        
        if search_receipt_date_from:
        #領収日で絞り込み(開始)
            search_flag = True
            if results is None:
                results = Cash_Book.objects.all().filter(receipt_date__gte=search_receipt_date_from).order_by('receipt_date', 'order')
            else:
                results = results.filter(receipt_date__gte=search_receipt_date_from).order_by('receipt_date', 'order')
        if search_receipt_date_to:
        #領収日で絞り込み(終了)
            search_flag = True
            if results is None:
                results = Cash_Book.objects.all().filter(receipt_date__lte=search_receipt_date_to).order_by('receipt_date', 'order')
            else:
                results = results.filter(receipt_date__lte=search_receipt_date_to).order_by('receipt_date', 'order')
        if search_account_title:
        #科目で絞り込み
            search_flag = True
            
            if results is None:
                results = Cash_Book.objects.all().filter(account_title=search_account_title).order_by(order_date, 'order')
            else:
                results = results.filter(account_title=search_account_title).order_by(order_date, 'order')
        if search_staff:
        #担当（社員）で絞り込み
            search_flag = True
            
            if results is None:
                results = Cash_Book.objects.all().filter(staff=search_staff).order_by(order_date, 'order')
            else:
                results = results.filter(staff=search_staff).order_by(order_date, 'order')
        if search_not_staff:
        #担当（社員-除外）で絞り込み
            search_flag = True
            
            if results is None:
                results = Cash_Book.objects.all().exclude(staff=search_not_staff).order_by(order_date, 'order')
            else:
                    results = results.exclude(staff=search_not_staff).order_by(order_date, 'order')
        #残高を算出しておく
        if search_flag == True:
            if search_settlement_date_from or search_settlement_date_to:
                cache.set('aggregate_save_flag', "false", 300)
                Aggregate.set_weekly(request)
        
        balance = cache.get('balance')
        balance_president = cache.get('balance_president')
        balance_staff = cache.get('balance_staff')
        #
        
        
        
        if search_flag == True:
        #検索クエリーが入力されている場合のみ
            
            #画面用の合計を算出
            Aggregate.caluculate_total(request, results)
            total_incomes = cache.get('total_incomes')
            total_expences = cache.get('total_expences')
            total_balance = cache.get('total_balance')
            
            
            return render(request,
                'account/cash_book_list.html',     # 使用するテンプレート
                {'cash_books': results, 'account_titles': account_titles, 'staffs': staffs,
                 'balance': balance, 'balance_president': balance_president, 'balance_staff': balance_staff, 
                 'total_incomes': total_incomes, 'total_expences': total_expences, 'total_balance': total_balance, 
                 'search_settlement_date_from': search_settlement_date_from, 'search_settlement_date_to': search_settlement_date_to, 
                 'search_receipt_date_from': search_receipt_date_from, 'search_receipt_date_to': search_receipt_date_to, 
                 'search_account_title':search_account_title, 'search_staff':search_staff, 'search_not_staff':search_not_staff })         # テンプレートに返すデータ
        else:
            return render(request,
                'account/cash_book_list.html',     # 使用するテンプレート
                {'cash_books': cash_books, 'account_titles': account_titles, 'staffs': staffs,
                 'balance': balance, 'balance_president': balance_president, 'balance_staff': balance_staff})     # テンプレートに渡すデータ

        
    
def cash_book_weekly_list(request):
    """出納帳の一覧"""
    #return HttpResponse('取引先の一覧')
    cash_book_weeklies = Cash_Book_Weekly.objects.all().order_by('id')

    return render(request,
                'account/cash_book_weekly_list.html',     # 使用するテンプレート
                {'cash_book_weeklies': cash_book_weeklies})         # テンプレートに渡すデータ
                
def balance_sheet_list(request):
    """貸借表の一覧"""
    #デバッグ
    #import pdb; pdb.set_trace()
    #return HttpResponse('◯◯◯の一覧')
    
    balance_sheets = Balance_Sheet.objects.all().order_by('id')

    if request.method == 'GET': # If the form is submitted
    
        #import pdb; pdb.set_trace()
    
        search_accrual_date_from = request.GET.get('q_accrual_date_from', None)
        search_accrual_date_to = request.GET.get('q_accrual_date_to', None)
        
        #貸借ID
        search_query_borrow_lend_id = request.GET.get('q_borrow_lend_id', None)
        
        #キャッシュに保存された検索結果をセット
        if search_accrual_date_from == None:
            search_accrual_date_from = cache.get('search_accrual_date_from')
        if search_accrual_date_to == None:
            search_accrual_date_to = cache.get('search_accrual_date_to')
        if search_query_borrow_lend_id == None:
            search_query_borrow_lend_id = cache.get('search_query_borrow_lend_id')
        #キャッシュへ検索結果をセット（最後の引数は、保存したい秒数）
        cache.set('search_accrual_date_from', search_accrual_date_from, 10800)
        cache.set('search_accrual_date_to', search_accrual_date_to, 10800)
        cache.set('search_query_borrow_lend_id', search_query_borrow_lend_id, 10800)
        
        ###フィルタリング
        results = None
        search_flag = False
        
        if search_accrual_date_from:
        #発生日で絞り込み(開始)
            
            search_flag = True
            results = Balance_Sheet.objects.all().filter(accrual_date__gte=search_accrual_date_from)
        
        if search_accrual_date_to:
        #発生日で絞り込み(終了)
            search_flag = True
            if results is None:
                results = Balance_Sheet.objects.all().filter(accrual_date__lte=search_accrual_date_to)
            else:
                results = results.filter(accrual_date__lte=search_accrual_date_to)
        
        if search_query_borrow_lend_id:
        #貸借で絞り込み(終了)
            search_flag = True
            if results is None:
                results = Balance_Sheet.objects.all().filter(borrow_lend_id__icontains=search_query_borrow_lend_id)
            else:
                results = results.filter(borrow_lend_id__icontains=search_query_borrow_lend_id)
        
        if search_flag == True:
        #検索クエリーが入力されている場合のみ
            
            return render(request,
                'account/balance_sheet_list.html',     # 使用するテンプレート
                {'balance_sheets': results, 'search_accrual_date_from': search_accrual_date_from, 'search_accrual_date_to': search_accrual_date_to, 'search_query_borrow_lend_id': search_query_borrow_lend_id})         # テンプレートに返すデータ
        else:
            return render(request,
                'account/balance_sheet_list.html',     # 使用するテンプレート
                {'balance_sheets': balance_sheets})         # テンプレートに渡すデータ
    else:
        return render(request,
                'account/balance_sheet_list.html',     # 使用するテンプレート
                {'balance_sheets': balance_sheets})         # テンプレートに渡すデータ

def balance_sheet_tally_list(request):
    """貸借表(集計)の一覧"""
    #デバッグ
    #import pdb; pdb.set_trace()
    #return HttpResponse('◯◯◯の一覧')
    
    balance_sheet_tallies = Balance_Sheet_Tally.objects.all().order_by('id')

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
        
        if search_accrual_date_from_tally and search_accrual_date_to_tally:
            
            search_flag = True
        
            #ここで集計データを用意する
            Aggregate_Balance_Sheet_Tally.aggregate_balance_sheet(request)
        
        if search_flag == True:
        #検索クエリーが入力されている場合のみ
            
            #日付範囲をセットし見出データを取得
            results = Balance_Sheet_Tally.objects.all().filter(accrual_date__gte=search_accrual_date_from_tally, accrual_date__lte=search_accrual_date_to_tally)

            sum_borrow_amount = results.aggregate(Sum('borrow_amount'))
            sum_lend_amount = results.aggregate(Sum('lend_amount'))
            
            return render(request,
                'account/balance_sheet_tally_list.html',     # 使用するテンプレート
                {'balance_sheet_tallies': results, 'search_accrual_date_from': search_accrual_date_from_tally, 
                'search_accrual_date_to': search_accrual_date_to_tally ,
                'sum_borrow_amount': sum_borrow_amount["borrow_amount__sum"],
                'sum_lend_amount': sum_lend_amount["lend_amount__sum"],
                                            })         # テンプレートに返すデータ
        else:
            return render(request,
                'account/balance_sheet_tally_list.html',     # 使用するテンプレート
                {'balance_sheet_tallies': balance_sheet_tallies})         # テンプレートに渡すデータ
    #else:
    #    return render(request,
    #            'account/balance_sheet_list.html',     # 使用するテンプレート
    #            {'balance_sheets': balance_sheets})         # テンプレートに渡すデータ

#def daterange(start_date, end_date):
#    start_date = datetime.date.today()
#    end_date = start_date + datetime.timedelta(days=5)
#    for n in range(int((end_date - start_date).days)):
#        yield start_date + timedelta(n)

#ノーマルな雛形(事前Import必要)
#def xxx_list(request):
#    """xxxの一覧"""
#    #デバッグ
#    #import pdb; pdb.set_trace()
#    #return HttpResponse('◯◯◯の一覧')
#    xxxs = Xxx.objects.all().order_by('id')
#    
#    # Your code
#    return render(request,
#                  'account/xxx_list.html',     # 使用するテンプレート
#                  {'xxxs': xxxs})         # テンプレートに渡すデータ

        
##### 編集ビュー #####
def partner_edit(request, partner_id=None):
    """取引先の編集"""
#    return HttpResponse('取引先の編集')
    if partner_id:   # partner_id が指定されている (修正時)
        partner = get_object_or_404(Partner, pk=partner_id)
    else:         # partner_id が指定されていない (追加時)
        partner = Partner()

    if request.method == 'POST':
        form = PartnerForm(request.POST, instance=partner)  # POST された request データからフォームを作成
        if form.is_valid():    # フォームのバリデーション
            partner = form.save(commit=False)
            partner.save()
            return redirect('account:partner_list')
    else:    # GET の時
        form = PartnerForm(instance=partner)  # partner インスタンスからフォームを作成

    return render(request, 'account/partner_edit.html', dict(form=form, partner_id=partner_id))

def account_title_edit(request, account_title_id=None):
    """勘定科目の編集"""
#    return HttpResponse('勘定科目の編集')
    if account_title_id:   # account_title_id が指定されている (修正時)
        account_title = get_object_or_404(Account_Title, pk=account_title_id)
    else:         # account_title_id が指定されていない (追加時)
        account_title = Account_Title()

    if request.method == 'POST':
        form = Account_TitleForm(request.POST, instance=account_title)  # POST された request データからフォームを作成
        if form.is_valid():    # フォームのバリデーション
            account_title = form.save(commit=False)
            account_title.save()
            return redirect('account:account_title_list')
    else:    # GET の時
        form = Account_TitleForm(instance=account_title)  # account_title インスタンスからフォームを作成

    return render(request, 'account/account_title_edit.html', dict(form=form, account_title_id=account_title_id))

def bank_edit(request, bank_id=None):
    """銀行の編集"""
#    return HttpResponse('勘定科目の編集')
    if bank_id:   # bank_id が指定されている (修正時)
        bank = get_object_or_404(Bank, pk=bank_id)
    else:         # bank_id が指定されていない (追加時)
        bank = Bank()

    if request.method == 'POST':
        form = BankForm(request.POST, instance=bank)  # POST された request データからフォームを作成
        if form.is_valid():    # フォームのバリデーション
            bank = form.save(commit=False)
            bank.save()
            return redirect('account:bank_list')
    else:    # GET の時
        form = BankForm(instance=bank)  # bank インスタンスからフォームを作成

    return render(request, 'account/bank_edit.html', dict(form=form, bank_id=bank_id))

def bank_branch_edit(request, bank_branch_id=None):
    """銀行支店の編集"""
#    return HttpResponse('勘定科目の編集')
    if bank_branch_id:   # bank_branch_id が指定されている (修正時)
        bank_branch = get_object_or_404(Bank_Branch, pk=bank_branch_id)
    else:         # bank_branch_id が指定されていない (追加時)
        bank_branch = Bank_Branch()

    if request.method == 'POST':
        form = Bank_BranchForm(request.POST, instance=bank_branch)  # POST された request データからフォームを作成
        if form.is_valid():    # フォームのバリデーション
            bank_branch = form.save(commit=False)
            bank_branch.save()
            return redirect('account:bank_branch_list')
    else:    # GET の時
        form = Bank_BranchForm(instance=bank_branch)  # bank_branch インスタンスからフォームを作成

    return render(request, 'account/bank_branch_edit.html', dict(form=form, bank_branch_id=bank_branch_id))

def payment_edit(request, payment_id=None):
    """支払の編集"""
         
#    return HttpResponse('勘定科目の編集')
    if payment_id:   # payment_id が指定されている (修正時)
        payment = get_object_or_404(Payment, pk=payment_id)
    else:         # payment_id が指定されていない (追加時)
        payment = Payment()

    if request.method == 'POST':
        form = PaymentForm(request.POST, instance=payment)  # POST された request データからフォームを作成
        if form.is_valid():    # フォームのバリデーション
            payment = form.save(commit=False)
            payment.save()
            
            #add200121
            #資金繰明細データも保存する
            Set_Cash_Flow_Detail.set_cash_flow_detail(payment.id)
            #add200118
            #import pdb; pdb.set_trace()
            
            #資金繰明細データへも保存する
            #billing_year_month, partnerでサーチ
            #payment.partner_id
            
            #別ビューで処理
            
            #各カラムへセット(予定日が入っていた場合のみ)
            #if payment.payment_due_date:
            #    #一旦削除
            #    Cash_Flow_Detail.objects.filter(billing_year_month=payment.billing_year_month, 
            #                                 partner_id=payment.partner_id).delete()
            #    cash_flow_detail = Cash_Flow_Detail()
                
            #    cash_flow_detail.billing_year_month = payment.billing_year_month
            #    cash_flow_detail.partner_id = payment.partner_id
            #    cash_flow_detail.account_title_id = payment.account_title_id
            #    cash_flow_detail.expected_expense = payment.billing_amount
                
            #    if payment.payment_method_id == 1:
                
                #
                
            #author = Author.objects.get(name="author name")
            #
            #
            
            return redirect('account:payment_list')
    else:    # GET の時
        
    
        form = PaymentForm(instance=payment)  # payment インスタンスからフォームを作成

    return render(request, 'account/payment_edit.html', dict(form=form, payment_id=payment_id))

def payment_reserve_edit(request, payment_reserve_id=None):
    """支払予約の編集"""
         
#    return HttpResponse('勘定科目の編集')
    if payment_reserve_id:   # payment_id が指定されている (修正時)
        payment_reserve = get_object_or_404(Payment_Reserve, pk=payment_reserve_id)
    else:         # payment_id が指定されていない (追加時)
        payment_reserve = Payment_Reserve()

    if request.method == 'POST':
        form = Payment_ReserveForm(request.POST, instance=payment_reserve)  # POST された request データからフォームを作成
        if form.is_valid():    # フォームのバリデーション
            payment_reserve = form.save(commit=False)
            payment_reserve.save()
            return redirect('account:payment_reserve_list')
    else:    # GET の時
        
    
        form = Payment_ReserveForm(instance=payment_reserve)  # payment インスタンスからフォームを作成

    return render(request, 'account/payment_reserve_edit.html', dict(form=form, payment_reserve_id=payment_reserve_id))


def cash_book_edit(request, cash_book_id=None):
    """出納帳の編集"""
         
#    return HttpResponse('勘定科目の編集')
    if cash_book_id:   # cash_book_id が指定されている (修正時)
        cash_book = get_object_or_404(Cash_Book, pk=cash_book_id)
    else:         # cash_book_id が指定されていない (追加時)
        cash_book = Cash_Book()

    if request.method == 'POST':
        form = Cash_BookForm(request.POST, instance=cash_book)  # POST された request データからフォームを作成
        if form.is_valid():    # フォームのバリデーション
            cash_book = form.save(commit=False)
            cash_book.save()
            
            #add200124
            #社長のデータの場合は、試算表・貸借表のデータにも保存する
            Set_Cash_Flow_Detail.set_cash_flow_detail_from_cash_book(cash_book.id)
            Set_Cash_Book_To_Balance_Sheet.set_balance_sheet(cash_book.id)
            #
            
            return redirect('account:cash_book_list')
    else:    # GET の時
        
    
        form = Cash_BookForm(instance=cash_book)  # cash_book インスタンスからフォームを作成

    return render(request, 'account/cash_book_edit.html', dict(form=form, cash_book_id=cash_book_id))


def cash_book_weekly_edit(request, cash_book_weekly_id=None):
    """週末データの編集"""
         
#    return HttpResponse('勘定科目の編集')
    if cash_book_weekly_id:   # cash_book_weekly_id が指定されている (修正時)
        cash_book_weekly = get_object_or_404(Cash_Book_Weekly, pk=cash_book_weekly_id)
    else:         # cash_book_weekly_id が指定されていない (追加時)
        cash_book_weekly = Cash_Book_Weekly()

    if request.method == 'POST':
        form = Cash_Book_WeeklyForm(request.POST, instance=cash_book_weekly)  # POST された request データからフォームを作成
        if form.is_valid():    # フォームのバリデーション
            cash_book_weekly = form.save(commit=False)
            cash_book_weekly.save()
            return redirect('account:cash_book_weekly_list')
    else:    # GET の時
        
    
        form = Cash_Book_WeeklyForm(instance=cash_book_weekly)  # cash_book_weekly インスタンスからフォームを作成

    return render(request, 'account/cash_book_weekly_edit.html', dict(form=form, cash_book_weekly_id=cash_book_weekly_id))

def cash_flow_header_edit(request, cash_flow_header_id=None):
    """資金繰り表見出の編集"""
#    return HttpResponse('資金繰り表見出の編集')
    if cash_flow_header_id:   # account_title_id が指定されている (修正時)
        cash_flow_header = get_object_or_404(Cash_Flow_Header, pk=cash_flow_header_id)
    else:         # cash_flow_header_id が指定されていない (追加時)
        cash_flow_header = Cash_Flow_Header()

    if request.method == 'POST':
        form = Cash_Flow_HeaderForm(request.POST, instance=cash_flow_header)  # POST された request データからフォームを作成
        if form.is_valid():    # フォームのバリデーション
            cash_flow_header = form.save(commit=False)
            cash_flow_header.save()
            return redirect('account:cash_flow_header_list')
    else:    # GET の時
        form = Cash_Flow_HeaderForm(instance=cash_flow_header)  # cash_flow_header インスタンスからフォームを作成

    return render(request, 'account/cash_flow_header_edit.html', dict(form=form, cash_flow_header_id=cash_flow_header_id))


def balance_sheet_edit(request, balance_sheet_id=None):
    """貸借表の編集"""
#    return HttpResponse('貸借表の編集')
    if balance_sheet_id:   # account_title_id が指定されている (修正時)
        balance_sheet = get_object_or_404(Balance_Sheet, pk=balance_sheet_id)
    else:         # cash_flow_header_id が指定されていない (追加時)
        balance_sheet = Balance_Sheet()
    
    #貸借表集計からの画面遷移の場合のパラメータをセット
    if request.method == 'GET':
        search_accrual_date_from = request.GET.get('q_accrual_date_from', None)
        search_accrual_date_to = request.GET.get('q_accrual_date_to', None)
        search_query_borrow_lend_id = request.GET.get('q_borrow_lend_id', None)
        
        #キャッシュに保存された検索結果をセット
        if search_accrual_date_from == None:
            search_accrual_date_from = cache.get('search_accrual_date_from')
        if search_accrual_date_to == None:
            search_accrual_date_to = cache.get('search_accrual_date_to')
        if search_query_borrow_lend_id == None:
            search_query_borrow_lend_id = cache.get('search_query_borrow_lend_id')
            
        #キャッシュへ検索結果をセット（最後の引数は、保存したい秒数）
        if search_accrual_date_from:
            cache.set('search_accrual_date_from', search_accrual_date_from, 10800)
        if search_accrual_date_to:
            cache.set('search_accrual_date_to', search_accrual_date_to, 10800)
        if search_query_borrow_lend_id:
            cache.set('search_query_borrow_lend_id', search_query_borrow_lend_id, 10800)
        
        #発生日をセット(開始日より)
        if search_accrual_date_from:
            balance_sheet.accrual_date = search_accrual_date_from
        #貸借IDをセット
        if search_query_borrow_lend_id:
            balance_sheet.borrow_lend_id = search_query_borrow_lend_id
            
        #import pdb; pdb.set_trace()
    #
    
    if request.method == 'POST':
        form = Balance_SheetForm(request.POST, instance=balance_sheet)  # POST された request データからフォームを作成
        
        #import pdb; pdb.set_trace()
        
        if form.is_valid():    # フォームのバリデーション
            balance_sheet = form.save(commit=False)
            balance_sheet.save()
            
            #直接遷移フラグ
            direct_from_tally_flag = request.GET.get('direct_from_tally_flag', None)
            
            #import pdb; pdb.set_trace()
            
            if direct_from_tally_flag is None:
                return redirect('account:balance_sheet_list')
            else:
                return redirect('account:balance_sheet_tally_list')
    else:    # GET の時
        form = Balance_SheetForm(instance=balance_sheet)  # cash_flow_header インスタンスからフォームを作成

    return render(request, 'account/balance_sheet_edit.html', dict(form=form, balance_sheet_id=balance_sheet_id))

##### 削除ビュー #####
def partner_del(request, partner_id):
    """取引先の削除"""
    #return HttpResponse('取引先の削除')
    partner = get_object_or_404(Partner, pk=partner_id)
    partner.delete()
    return redirect('account:partner_list')

def account_title_del(request, account_title_id):
    """勘定科目の削除"""
    #return HttpResponse('勘定科目の削除')
    account_title = get_object_or_404(Account_Title, pk=account_title_id)
    account_title.delete()
    return redirect('account:account_title_list')
    
def bank_del(request, bank_id):
    """銀行の削除"""
    #return HttpResponse('銀行の削除')
    bank = get_object_or_404(Bank, pk=bank_id)
    bank.delete()
    return redirect('account:bank_list')
    
def bank_branch_del(request, bank_branch_id):
    """銀行支店の削除"""
    #return HttpResponse('銀行支店の削除')
    bank_branch = get_object_or_404(Bank_Branch, pk=bank_branch_id)
    bank_branch.delete()
    return redirect('account:bank_branch_list')
    
def payment_del(request, payment_id):
    """支払の削除"""
    
    payment = get_object_or_404(Payment, pk=payment_id)
    payment.delete()
    return redirect('account:payment_list')

def payment_reserve_del(request, payment_reserve_id):
    """支払の削除"""
    
    payment_reserve = get_object_or_404(Payment_Reserve, pk=payment_reserve_id)
    payment_reserve.delete()
    return redirect('account:payment_reserve_list')
    
def cash_book_del(request, cash_book_id):
    """支払の削除"""
    
    #貸借表データがあれば削除
    Balance_Sheet.objects.filter(cash_book_id=cash_book_id).delete()
    #資金繰表実績データがあれば削除
    Cash_Flow_Detail_Actual.objects.filter(cash_book_id=cash_book_id).delete()
    #
    
    cash_book = get_object_or_404(Cash_Book, pk=cash_book_id)
    cash_book.delete()
    
    return redirect('account:cash_book_list')


def cash_book_weekly_del(request, cash_book_weekly_id):
    """支払の削除"""
    cash_book_weekly = get_object_or_404(Cash_Book, pk=cash_book_weekly_id)
    cash_book_weekly.delete()
    return redirect('account:cash_book_weekly_list')
    
def balance_sheet_del(request, balance_sheet_id):
    """貸借表の削除"""
    balance_sheet = get_object_or_404(Balance_Sheet, pk=balance_sheet_id)
    balance_sheet.delete()
    return redirect('account:balance_sheet_list')
    

#検索フォーム用・・・
#def get_queryset(self):
#    #デバッグ？
#    import pdb; pdb.set_trace()

#    query = self.request.GET.get('q') 
#    if query:
#        return Account_Title.objects.filter(name__icontains=query)
#    else:
#        return Account_Title.objects.all()

