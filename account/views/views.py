from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from account.models import Partner
from account.models import Account
from account.models import Account_Sub
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
from account.models import Expence
from account.models import Deposit
from account.models import Daily_Representative_Loan
from account.models import Monthly_Representative_Loan  #add240502
from account.models import Accrued_Expence  #add240727

#
from account.forms import PartnerForm
from account.forms import AccountForm
from account.forms import Account_SubForm
from account.forms import Account_TitleForm
from account.forms import BankForm
from account.forms import Bank_BranchForm
from account.forms import PaymentForm
from account.forms import Payment_ReserveForm
from account.forms import Cash_BookForm
from account.forms import Cash_Book_WeeklyForm
from account.forms import Cash_Flow_HeaderForm
from account.forms import Balance_SheetForm
from account.forms import Daily_Representative_LoanForm
from account.forms import Monthly_Representative_LoanForm
from account.forms import Accrued_ExpenceForm  #add240729

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
from account.views import set_daily_cash_flow as Set_Daily_Cash_flow    #add230130

from account.views import set_representative_loan as Set_Representative_Loan  #add231121

from django.conf import settings
from django.db.models import Q  
from django.contrib import messages

#ログイン用
#from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
from django.views.generic import View
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
#
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

import calendar    #月末日取得用  add180911
from django.db.models import Avg, Max, Min, Sum

#from django.db import IntegrityError
from django.http import HttpResponseRedirect

#グローバル変数
table_type_id = 0  
income_expence_flag = 0 # 0：収入  1:支出
#no_complete_flag = False
#

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

##### 一覧ビュー #####
def partner_list(request):
    """取引先の一覧"""
    #return HttpResponse('取引先の一覧')
    partners = Partner.objects.all().order_by('id')
    if request.method == 'GET': # If the form is submitted
        search_query = request.GET.get('q', None)
        search_query_partner = request.GET.get('q_partner', None)
        
        if search_query_partner == None:
            search_query_partner = cache.get('search_query_partner')
        cache.set('search_query_partner', search_query_partner, 10800)
        
        search_flag = False
        results = None
        
        if search_query:
            search_flag = True
            results = Partner.objects.all().filter(trade_division_id__icontains=search_query)
            #return render(request,
            #    'account/partner_list.html',     # 使用するテンプレート
            #    {'partners': results})         # テンプレートに渡すデータ
        #else:
        #    return render(request,
         #       'account/partner_list.html',     # 使用するテンプレート
        #        {'partners': partners})         # テンプレートに渡すデータ
                
        if search_query_partner:
        #支払先で絞り込み
            search_flag = True
            if results is None:
                results = Partner.objects.all().filter(id=search_query_partner)
            else:
                results = results.filter(id=search_query_partner)        
        
        if search_flag:
            return render(request,
                'account/partner_list.html',     # 使用するテンプレート
                {'partners': results, 'search_query_partner': search_query_partner})         # テンプレートに渡すデータ
        else:
            return render(request,
                'account/partner_list.html',     # 使用するテンプレート
                {'partners': partners})         # テンプレートに渡すデータ
    
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

def account_list(request):
    """勘定科目(貸借用)の一覧"""
    accounts = Account.objects.all().order_by('id')
    
    return render(request,
                'account/account_list.html',     # 使用するテンプレート
                {'accounts': accounts})         # テンプレートに渡すデータ

def account_sub_list(request):
    """補助科目(貸借用)の一覧"""
    account_subs = Account_Sub.objects.all().order_by('id')
    
    return render(request,
                'account/account_sub_list.html',     # 使用するテンプレート
                {'account_subs': account_subs})      # テンプレートに渡すデータ

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

#特定画面はsoumuユーザーでパスワード認証する
#class PasswordAuth1(View):
#    @method_decorator(login_required)
#    def get(self, request):
#        return render(request, 'account/password_auth_1.html')

#特定画面はsoumuユーザーでパスワード認証する
#支払画面
def password_auth_1(request):
#    #import pdb; pdb.set_trace()
    #return render(request, 'account/payment_list.html')
    
    if(request.method == 'GET'):
        
        return render(request, 'account/password_auth_1.html')
    
    elif(request.method == 'POST'):
    
        username = request.POST['username']
        password = request.POST['password']
        
        #ここは総務用のパスワード認証できるようにする。ベタ打ちで
        check = False
        if (username == "soumu" and password == "470211#"):
            check = True
        
        if check:
            #get ok...
            #return payment_list(request)
            
            return HttpResponseRedirect('../payment')
 
        else:
            return render(request, 'account/index.html')
#取引先画面
def password_auth_2(request):
    
    if(request.method == 'GET'):
        
        return render(request, 'account/password_auth_2.html')
    
    elif(request.method == 'POST'):
    
        username = request.POST['username']
        password = request.POST['password']
        
        #ここは総務用のパスワード認証できるようにする。ベタ打ちで
        check = False
        if (username == "soumu" and password == "470211#"):
            check = True
        
        if check:
            
            return HttpResponseRedirect('../partner')
 
        else:
            return render(request, 'account/index.html')

#未払費用画面
def password_auth_3(request):
    
    if(request.method == 'GET'):
        
        return render(request, 'account/password_auth_3.html')
    
    elif(request.method == 'POST'):
    
        username = request.POST['username']
        password = request.POST['password']
        
        #ここは総務用のパスワード認証できるようにする。ベタ打ちで
        check = False
        if (username == "soumu" and password == "470211#"):
            check = True
        
        if check:
            
            return HttpResponseRedirect('../accrued_expence')
 
        else:
            return render(request, 'account/index.html')

def payment_list(request, number=None):
    """支払の一覧"""
    
    #import pdb; pdb.set_trace()

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
        search_query_update_date = request.GET.get('q_update_date', None)
        
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
        if search_query_trade_division_id == None:
            search_query_trade_division_id = cache.get('search_query_trade_division_id')
        if search_query_payment == None:
            search_query_payment = cache.get('search_query_payment')
        if search_query_partner == None:
            search_query_partner = cache.get('search_query_partner')
        if search_query_paid == None:
            search_query_paid = cache.get('search_query_paid')
            
        if search_query_update_date == None:
            search_query_update_date = cache.get('search_query_update_date')
            
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
        
        #cache.set('search_query_update_date', search_query_update_date, 10800)
        #upd240716
        cache.set('search_query_update_date', search_query_update_date, 86400)
        #
        
        ###フィルタリング
        results = None
        search_flag = False
        search_flag_pay_day = False
        multi_month = False
        search_query_pay_month_from_saved = ""
        
        ############
        #印刷時も同様の集計をしている箇所があるので注意！！
        
        
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
        
        search_query_pay_month_plus_to = None
        
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
            
            #upd210311
            #振込のみ、３ヶ月先まで集計するようにする
            #+3ヶ月足す(add210311)
            plus_date = datetime(end_year, end_month, lastday) + relativedelta(months=3)  #年をまたいだ3ヶ月加算
            end_year_plus = plus_date.year
            end_month_plus = plus_date.month
            _, lastday_plus = calendar.monthrange(end_year_plus,end_month_plus)
            
            search_query_pay_month_plus_to = str(end_year_plus) + "-" + str(end_month_plus) + "-" + str(lastday_plus)
            ##
            
            #import pdb; pdb.set_trace()
            
            if results is None:
                #results = Payment.objects.all().filter(payment_due_date__lte=search_query_pay_month_to)
                results = Payment.objects.all().filter(payment_due_date__lte=search_query_pay_month_plus_to)
            else:
                #results = results.filter(payment_due_date__lte=search_query_pay_month_to)
                results = results.filter(payment_due_date__lte=search_query_pay_month_plus_to)
            ###
        
        if search_query_update_date:
        #if search_query_update_date and search_query_update_date is not None:
        #更新日で絞り込み
            search_flag = True
            try:
                from_datetime = datetime.strptime(search_query_update_date, "%Y/%m/%d")
            except ValueError:
                from_datetime = datetime.now()
                
            #import pdb; pdb.set_trace()
            #１日足す
            to_datetime = from_datetime + timedelta(days=1)
            
            if results is None:
                results = Payment.objects.all().filter(update_at__gte=from_datetime, update_at__lte=to_datetime)
            else:
                results = results.filter(update_at__gte=from_datetime, update_at__lte=to_datetime)
            
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
            #if search_query_pay_month_from:
            if search_query_pay_month_to:
            
                #add210311
                #end_year = int(search_query_pay_month_to[0:4])
                #end_month = int(search_query_pay_month_to[5:7])
                #_, lastday = calendar.monthrange(end_year,end_month)
                #年をまたいだ3ヶ月加算
                #plus_date = datetime(end_year, end_month, lastday) + relativedelta(months=3)  
                #end_year_plus = plus_date.year
                #end_month_plus = plus_date.month
                #_, lastday_plus = calendar.monthrange(end_year_plus,end_month_plus)
                #search_query_pay_month_plus_to = str(end_year_plus) + "-" + str(end_month_plus) + "-" + str(lastday_plus)
                search_month = search_query_pay_month_to
                
                if search_query_pay_month_plus_to:
                    search_month = search_query_pay_month_plus_to
                
                #import pdb; pdb.set_trace()
                #
            
                search_flag = True
                if results is None:
                    #results = Payment.objects.all().filter(payment_date__isnull=True).order_by('order')
                    
                    #upd200507
                    #支払日=null or 未払金有&未払支払日=null
                    results = Payment.objects.all().filter(
                    Q(unpaid_date__isnull=True) , Q(unpaid_amount__gt=0) |
                    Q(payment_date__isnull=True), Q(payment_due_date__lte=search_month)
                    ).order_by('order')
                    
                    
                else:
                    #results = results.filter(payment_date__isnull=True)
                    
                    #upd200507
                    #支払日=null or 未払金有&未払支払日=null
                    results = Payment.objects.all().filter(
                    Q(unpaid_date__isnull=True) , Q(unpaid_amount__gt=0) |
                    Q(payment_date__isnull=True), Q(payment_due_date__lte=search_month)
                    )
                    
                    #Q(payment_date__isnull=True) , Q(billing_amount__gt=0) |
                
                #ここから更に、振込以外のものは指定月以下で抽出させる  add210311
                results = extract_payment(results, search_query_pay_month_to)
        ###
        
        #add240425
        #何も検索項目のない場合は月初からの検索とする
        if search_flag == False:
            search_flag = True
            #
            now_date = datetime.now()
            first_date = now_date.replace(day=1)
            
            search_query_month_from = first_date.strftime ("%Y-%m")
            search_query_month_to = first_date.strftime ("%Y-%m")
            
            cache.set('search_query_month_from', search_query_month_from, 86400)
            cache.set('search_query_month_to', search_query_month_to, 86400)
            #検索用に変換
            search_query_month_from = first_date.strftime ("%Y-%m-%d")
            search_query_month_to = first_date.strftime ("%Y-%m-%d")
            search_query_pay_month_from = ""
            search_query_pay_month_to = ""
            search_query_update_date = ""
            results = Payment.objects.all().filter(billing_year_month__gte=search_query_month_from, \
                                                   billing_year_month__lte=search_query_month_from)
            
            
        #add end
        #
        
        
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
                  'search_query_paid': search_query_paid, 'search_query_update_date': search_query_update_date})         # テンプレートに渡すデータ
        else:
            
                return render(request,
                'account/payment_list.html',     # 使用するテンプレート
                {'payments': payments, 'partners': partners })         # テンプレートに渡すデータ

def extract_payment(results, search_query_pay_month_to):
    #振込以外のものは、指定月より小さくさせる
    list_of_ids = []
    #import pdb; pdb.set_trace()
            
    for payment in results:
        #振込以外は指定月以下のみカウントさせる(未払いかは下で処理)
        chk = False
        
        #import pdb; pdb.set_trace()
        
        #if payment.payment_method_id == 1: #振込
        if payment.trade_division_id == 0:  #仕入・外注
            chk = True
                
            if payment.billing_amount == None or payment.billing_amount == 0:
            #仕入・外注は金額がなければ外す
                chk = False
        else:
            #振込以外は支払予定が指定月以下とする
            dt = datetime.strptime(search_query_pay_month_to, '%Y-%m-%d')
            if payment.payment_due_date <= dt.date():
                chk = True
                
        if chk:
            list_of_ids.append(payment.id)
            
    results = results.filter(id__in=list_of_ids)
    
    return results
            
  
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
    
    #del240702 ここで全件を取ってくるので、データ量が増えると処理がフリーズしてしまう
    #cash_books = Cash_Book.objects.all().order_by('settlement_date', 'order')
    
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
        
        if search_settlement_date_to and search_settlement_date_to is not 'None':
        #請求日で絞り込み(終了)
            search_flag = True
            if results is None:
                results = Cash_Book.objects.all().filter(settlement_date__lte=search_settlement_date_to).order_by('settlement_date', 'order')
            else:
                results = results.filter(settlement_date__lte=search_settlement_date_to).order_by('settlement_date', 'order')
        
        #if search_receipt_date_from:
        if search_receipt_date_from and search_receipt_date_from is not 'None':
        #領収日で絞り込み(開始)
            search_flag = True
            if results is None:
                results = Cash_Book.objects.all().filter(receipt_date__gte=search_receipt_date_from).order_by('receipt_date', 'order')
            else:
                results = results.filter(receipt_date__gte=search_receipt_date_from).order_by('receipt_date', 'order')
        #if search_receipt_date_to:
        if search_receipt_date_to and search_receipt_date_to is not 'None':
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
        
        #add220822
        #何も検索項目のない場合は請求日で当日(-1day)検索する
        if search_flag == False:
            #
            search_flag = True
            
            now_date = datetime.now()
            now_date = now_date + timedelta(days=-1)
            
            search_settlement_date_from = now_date.strftime ("%Y-%m-%d")
            search_settlement_date_to = now_date.strftime ("%Y-%m-%d")
            search_receipt_date_from = ""
            search_receipt_date_to = ""
            
            results = Cash_Book.objects.all().filter(settlement_date__gte=search_settlement_date_from).order_by('settlement_date', 'order')
        
        
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

def cash_flow_header_list(request):
    """資金繰り表"""
    
    #
    #import pdb; pdb.set_trace()
    
    if request.method == 'GET': # If the form is submitted
        
        search_query_cash_flow_date_from = request.GET.get('q_cash_flow_date_from', None)
        if search_query_cash_flow_date_from == None:
            search_query_cash_flow_date_from = cache.get('search_query_cash_flow_date_from')
        if search_query_cash_flow_date_from != None:
            if len(search_query_cash_flow_date_from) == 10:
            #すでに１日が入っている場合、下部で処理するので削っておく
                #search_query_cash_flow_date_from = search_query_cash_flow_date_from.rstrip("-01")
                search_query_cash_flow_date_from = search_query_cash_flow_date_from[:-3]
        if search_query_cash_flow_date_from != None:
            cache.set('search_query_cash_flow_date_from', search_query_cash_flow_date_from, 86400)
        ####
        
        #if 'button_2' in request.GET: 
        #集計の場合、別途集計データを作成する
            #import pdb; pdb.set_trace()
        Aggregate_Cash_Flow.set_cash_flow(request)
        
        #画面表示用の結果を抽出
        date_count = 0
        first_date = date.today()
        last_date = date.today()
        
        #今日の日付から、今年の1月1日を求める(年またがりの場合をまだ考慮していない・・)
        if search_query_cash_flow_date_from is None:
            today = date.today()
            first_date = date(today.year, 1, 1)
            tstr = first_date.strftime('%Y-%m-%d')
            search_query_cash_flow_date_from = tstr[:-3]   #下の計算用に、１日は消しておく
        ##
        
        if search_query_cash_flow_date_from:
        
            search_query_cash_flow_date_only_from = search_query_cash_flow_date_from  #月までの文字でも保存しておく
            
            search_query_cash_flow_date_from += "-01"
        
            ###
            tmp_year = int(search_query_cash_flow_date_from[:-6])
            
            #支払予定のデータより、最終の集計日(指定の年間のみで)を求める
            #cash_flow_detail_expected_last = Cash_Flow_Detail_Expected.objects.all().aggregate(Max('expected_date'))
            cash_flow_detail_expected_last = Cash_Flow_Detail_Expected.objects.filter(expected_date__year=tmp_year).\
                                                              aggregate(Max('expected_date'))
            
            tmp_last_date = cash_flow_detail_expected_last["expected_date__max"]
            
            if tmp_last_date:  #add200212
            
                #最終日は、最終の予定日のデータの入ってる月のものとする
                end_year = tmp_last_date.year
                end_month = tmp_last_date.month
                #end_year = int(search_query_cash_flow_date_from[0:4])
                #end_month = int(search_query_cash_flow_date_from[5:7])
                _, lastday = calendar.monthrange(end_year,end_month)
            
                #最終日付を求める
                last_date = date(end_year, end_month, lastday)
                date_count = (last_date-first_date).days
                ###
        
                #月末日で検索する
           
            
        
        results = None
        
        if search_query_cash_flow_date_from is not None:
        
            #for i in range(lastday):
            #0~月末日-1日でループ
            #    tmpDay = str(i+1).zfill(2)
            
            
            #文字→日付へ変換
            #開始日
            string_date = search_query_cash_flow_date_only_from + "-" + "01"
            cash_flow_date_from = datetime.strptime(string_date, '%Y-%m-%d')
            
            #終了日
            cash_flow_date_to = last_date
            #string_date = search_query_cash_flow_date_only_from + "-" + str(lastday).zfill(2)
            #cash_flow_date_to = datetime.strptime(string_date, '%Y-%m-%d')
            

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
                                                'search_query_cash_flow_date_from': search_query_cash_flow_date_from})
        else:
            return render(request,
                 'account/cash_flow_header_list.html',     # 使用するテンプレート
                  {'cash_flow_headers':results, 
                                   'search_query_cash_flow_date_from': search_query_cash_flow_date_from})


def cash_flow_detail_expected_list(request):
    """資金繰(予定)の一覧"""
    #デバッグ
    #import pdb; pdb.set_trace()
    
    cash_flow_detail_expects = Cash_Flow_Detail_Expected.objects.all().order_by('id')

    if request.method == 'GET': # If the form is submitted
    
        #import pdb; pdb.set_trace()
    
        search_expected_date_from = request.GET.get('q_expected_date_from', None)
        search_expected_date_to = request.GET.get('q_expected_date_to', None)
        
        #支払ID
        search_query_bp_id = request.GET.get('q_bp_id', None)
        #銀行ID
        search_query_bank_id = request.GET.get('q_bank_id', None)
        #銀行支店ID
        search_query_bank_branch_id = request.GET.get('q_bank_branch_id', None)
        
        #キャッシュに保存された検索結果をセット
        if search_expected_date_from == None:
            search_expected_date_from = cache.get('search_expected_date_from')
        if search_expected_date_to == None:
            search_expected_date_to = cache.get('search_expected_date_to')
        #ここはNULLの場合もあるのでキャッシュから取らない
        #if search_query_bp_id == None:
        #    search_query_bp_id = cache.get('search_query_bp_id')
        
        #キャッシュへ検索結果をセット（最後の引数は、保存したい秒数）
        cache.set('search_expected_date_from', search_expected_date_from, 10800)
        cache.set('search_expected_date_to', search_expected_date_to, 10800)
        #cache.set('search_query_bp_id', search_query_bp_id, 10800)
        
        ###フィルタリング
        results = None
        search_flag = False
        
        #import pdb; pdb.set_trace()
        
        if search_expected_date_from:
        #発生日で絞り込み(開始)
            
            search_flag = True
            results = Cash_Flow_Detail_Expected.objects.all().filter(expected_date__gte=search_expected_date_from)
        
        if search_expected_date_to:
        #発生日で絞り込み(終了)
            search_flag = True
            if results is None:
                results = Cash_Flow_Detail_Expected.objects.all().filter(expected_date__lte=search_expected_date_to)
            else:
                results = results.filter(expected_date__lte=search_expected_date_to)
        
        if search_query_bp_id:
        #収支で絞り込み
            search_flag = True
            if results is None:
                if search_query_bp_id == "0":
                #支払
                    results = Cash_Flow_Detail_Expected.objects.all().filter(expected_expense__gt=0)
                elif search_query_bp_id == "1":
                #収入
                    results = Cash_Flow_Detail_Expected.objects.all().filter(expected_income__gt=0)
            else:
                if search_query_bp_id == "0":
                #支払
                    results = results.filter(expected_expense__gt=0)
                elif search_query_bp_id == "1":
                #収入
                    results = results.filter(expected_income__gt=0)
        
        if search_query_bank_id:
        #銀行で絞り込み
            search_flag = True
            if results is None:
                
                if search_query_bank_id != "99":
                    if not search_query_bank_branch_id:
                    #北越の場合
                        results = Cash_Flow_Detail_Expected.objects.all().filter(payment_bank_id=search_query_bank_id)
                    else:
                    #さんしん(本店・塚野目)の場合
                        results = Cash_Flow_Detail_Expected.objects.all().filter(payment_bank_id=search_query_bank_id, 
                                                                                 payment_bank_branch_id=search_query_bank_branch_id)
                else:
                #現金の場合
                    results = Cash_Flow_Detail_Expected.objects.all().filter(cash_id=1)
            else:
                
                if search_query_bank_id != "99":
                    if not search_query_bank_branch_id:
                    #北越の場合
                        results = results.filter(payment_bank_id=search_query_bank_id)
                    else:
                    #さんしん(本店・塚野目)の場合
                        results = results.filter(payment_bank_id=search_query_bank_id, 
                                                                     payment_bank_branch_id=search_query_bank_branch_id)
                                                                                 
                    #results = results.filter(payment_bank_id=search_query_bank_id)
                else:
                #現金の場合
                    results = results.filter(cash_id=1)
        
                    
        if search_flag == True:
        #検索クエリーが入力されている場合のみ
            
            #合計
            sum_amount = 0
            
            tmp_amount = results.aggregate(Sum('expected_expense'))
            if tmp_amount:
                sum_amount = tmp_amount["expected_expense__sum"]
            
            
            tmp_amount = results.aggregate(Sum('expected_income'))
            if tmp_amount:
                sum_amount += tmp_amount["expected_income__sum"]
                        
            return render(request,
                'account/cash_flow_detail_expected_list.html',     # 使用するテンプレート
                {'cash_flow_detail_expects': results, 'search_expected_date_from': search_expected_date_from,
                 'search_expected_date_to': search_expected_date_to,
                 'sum_amount': sum_amount})         # テンプレートに返すデータ
        else:
            return render(request,
                'account/cash_flow_detail_expected_list.html',     # 使用するテンプレート
                {'cash_flow_detail_expects': cash_flow_detail_expects})         # テンプレートに渡すデータ
    else:
        return render(request,
                'account/cash_flow_detail_expected_list.html',     # 使用するテンプレート
                {'cash_flow_detail_expects': cash_flow_detail_expects})         # テンプレートに渡すデータ

def cash_flow_detail_actual_list(request):
    """資金繰(実際)の一覧"""
    #デバッグ
    #import pdb; pdb.set_trace()
    
    cash_flow_detail_expects = Cash_Flow_Detail_Actual.objects.all().order_by('id')

    if request.method == 'GET': # If the form is submitted
        
        search_actual_date_from = request.GET.get('q_actual_date_from', None)
        search_actual_date_to = request.GET.get('q_actual_date_to', None)
        
        #支払ID
        search_query_bp_id = request.GET.get('q_bp_id', None)
        #銀行ID
        search_query_bank_id = request.GET.get('q_bank_id', None)
        #銀行支店ID
        search_query_bank_branch_id = request.GET.get('q_bank_branch_id', None)
        
        #キャッシュに保存された検索結果をセット
        if search_actual_date_from == None:
            search_actual_date_from = cache.get('search_actual_date_from')
        if search_actual_date_to == None:
            search_actual_date_to = cache.get('search_actual_date_to')
        #ここはNULLの場合もあるのでキャッシュから取らない
        #if search_query_bp_id == None:
        #    search_query_bp_id = cache.get('search_query_bp_id')
        
        #キャッシュへ検索結果をセット（最後の引数は、保存したい秒数）
        cache.set('search_actual_date_from', search_actual_date_from, 10800)
        cache.set('search_actual_date_to', search_actual_date_to, 10800)
        
        ###フィルタリング
        results = None
        search_flag = False
        
        #import pdb; pdb.set_trace()
        
        if search_actual_date_from:
        #発生日で絞り込み(開始)
            
            search_flag = True
            results = Cash_Flow_Detail_Actual.objects.all().filter(actual_date__gte=search_actual_date_from)
        
        if search_actual_date_to:
        #発生日で絞り込み(終了)
            search_flag = True
            if results is None:
                results = Cash_Flow_Detail_Actual.objects.all().filter(actual_date__lte=search_actual_date_to)
            else:
                results = results.filter(actual_date__lte=search_actual_date_to)
        
        if search_query_bp_id:
        #収支で絞り込み
            search_flag = True
            if results is None:
                if search_query_bp_id == "0":
                #支払
                    #results = Cash_Flow_Detail_Actual.objects.all().filter(actual_expense__gt=0)
                    results = Cash_Flow_Detail_Actual.objects.all().exclude(actual_expense=0)
                elif search_query_bp_id == "1":
                #収入
                    #results = Cash_Flow_Detail_Actual.objects.all().filter(actual_income__gt=0)
                    results = Cash_Flow_Detail_Actual.objects.all().exclude(actual_income=0)
            else:
                if search_query_bp_id == "0":
                #支払
                    #results = results.filter(actual_expense__gt=0)
                    results = results.exclude(actual_expense=0)
                elif search_query_bp_id == "1":
                #収入
                    #results = results.filter(actual_income__gt=0)
                    results = results.exclude(actual_income=0)
        
        cash_flag = False
        
        if search_query_bank_id:
        #銀行で絞り込み
            search_flag = True
            if results is None:
                
                if search_query_bank_id != "99":
                    if not search_query_bank_branch_id:
                    #北越の場合
                        results = Cash_Flow_Detail_Actual.objects.all().filter(payment_bank_id=search_query_bank_id)
                    else:
                    #さんしん(本店・塚野目)の場合
                        results = Cash_Flow_Detail_Actual.objects.all().filter(payment_bank_id=search_query_bank_id, 
                                                                                 payment_bank_branch_id=search_query_bank_branch_id)
                else:
                #現金の場合
                    cash_flag = True
                    results = Cash_Flow_Detail_Actual.objects.all().filter(cash_id=1)
            else:
                
                if search_query_bank_id != "99":
                    if not search_query_bank_branch_id:
                    #北越の場合
                        results = results.filter(payment_bank_id=search_query_bank_id)
                    else:
                    #さんしん(本店・塚野目)の場合
                        results = results.filter(payment_bank_id=search_query_bank_id, 
                                                                     payment_bank_branch_id=search_query_bank_branch_id)
                                                                                 
                else:
                #現金の場合
                    cash_flag = True
                    results = results.filter(cash_id=1)
        
                    
        if search_flag == True:
        #検索クエリーが入力されている場合のみ
            
            #import pdb; pdb.set_trace()
            
            #合計
            sum_amount = 0
            
            tmp_amount = results.aggregate(Sum('actual_expense'))
            if tmp_amount:
                if not cash_flag:
                    sum_amount = tmp_amount["actual_expense__sum"]
                else:
                #現金の場合は、マイナスとする
                    sum_amount = -tmp_amount["actual_expense__sum"]
            
            tmp_amount = results.aggregate(Sum('actual_income'))
            #if tmp_amount:
            if tmp_amount["actual_income__sum"]:   #upd200212
                sum_amount += tmp_amount["actual_income__sum"]
                        
            return render(request,
                'account/cash_flow_detail_actual_list.html',     # 使用するテンプレート
                {'cash_flow_detail_expects': results, 'search_actual_date_from': search_actual_date_from,
                 'search_actual_date_to': search_actual_date_to,
                 'sum_amount': sum_amount})         # テンプレートに返すデータ
        else:
            return render(request,
                'account/cash_flow_detail_actual_list.html',     # 使用するテンプレート
                {'cash_flow_detail_expects': cash_flow_detail_expects})         # テンプレートに渡すデータ
    else:
        return render(request,
                'account/cash_flow_detail_actual_list.html',     # 使用するテンプレート
                {'cash_flow_detail_expects': cash_flow_detail_expects})         # テンプレートに渡すデータ


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
        
        #add240425
        #何も検索項目のない場合は月初からの検索とする
        if search_flag == False:
            search_flag = True
            #
            now_date = datetime.now()
            first_date = now_date.replace(day=1)
            search_accrual_date_from = first_date.strftime ("%Y-%m-%d")
            search_accrual_date_to = ""
            #search_accrual_date_to = first_date.strftime ("%Y-%m-%d")
            
            results = Balance_Sheet.objects.all().filter(accrual_date__gte=search_accrual_date_from)
            #
            
        #add end
        
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

#作成中 240425
def daily_representative_loan_list(request):
    """代表者貸付金の一覧"""
    #デバッグ
    #import pdb; pdb.set_trace()
    #return HttpResponse('◯◯◯の一覧')
    daily_representative_loans = Daily_Representative_Loan.objects.all().order_by('id')
    
    if request.method == 'GET': # If the form is submitted
        search_occur_date_from = request.GET.get('q_occur_date_from', None)
        search_occur_date_to = request.GET.get('q_occur_date_to', None)
        #キャッシュに保存された検索結果をセット
        if search_occur_date_from == None:
            search_occur_date_from = cache.get('search_occur_date_from')
        if search_occur_date_to == None:
            search_occur_date_to = cache.get('search_occur_date_to')
        #キャッシュへ検索結果をセット（最後の引数は、保存したい秒数）
        cache.set('search_occur_date_from', search_occur_date_from, 10800)
        cache.set('search_occur_date_to', search_occur_date_to, 10800)
        #
        results = None
        search_flag = False
        
        if search_occur_date_from:
            search_flag = True
            results = Daily_Representative_Loan.objects.all().filter(occurred_on__gte=search_occur_date_from)
        if search_occur_date_to:
            search_flag = True
            if results is None:
                results = Daily_Representative_Loan.objects.all().filter(occurred_on__lte=search_occur_date_to)
            else:
                results = results.filter(occurred_on__lte=search_occur_date_to)
        
        #何も検索項目のない場合は月初で検索
        if search_flag == False:
            search_flag = True
            
            now_date = datetime.now()
            first_date = now_date.replace(day=1)
            
            search_occur_date_from = first_date.strftime ("%Y-%m-%d")
            search_occur_date_to = first_date.strftime ("%Y-%m-%d")
            
            results = Daily_Representative_Loan.objects.all().filter(occurred_on__gte=search_occur_date_from, \
                                                                     occurred_on__lte=search_occur_date_to)
        #        
        
        if search_flag == True:
            return render(request,
            'account/daily_representative_loan_list.html',     # 使用するテンプレート
                  {'daily_representative_loans': results, 'search_query_date_from': search_occur_date_from, 
                                                          'search_query_date_to': search_occur_date_to})         # テンプレートに渡すデータ
        else:
            return render(request,
            'account/daily_representative_loan_list.html',     # 使用するテンプレート
                  {'daily_representative_loans': daily_representative_loans})         # テンプレートに渡すデータ
    else:
        # Your code
        return render(request,
                  'account/daily_representative_loan_list.html',     # 使用するテンプレート
                  {'daily_representative_loans': daily_representative_loans})         # テンプレートに渡すデータ

def monthly_representative_loan_list(request):
    """月次貸付金の一覧"""
        
    monthly_representative_loans = Monthly_Representative_Loan.objects.all().order_by('id')
    
    if request.method == 'GET': # If the form is submitted
        search_date_from = request.GET.get('q_date_from', None)
        search_date_to = request.GET.get('q_date_to', None)
        #キャッシュに保存された検索結果をセット
        if search_date_from == None:
            search_date_from = cache.get('search_date_from')
        if search_date_to == None:
            search_date_to = cache.get('search_date_to')
        #キャッシュへ検索結果をセット（最後の引数は、保存したい秒数）
        cache.set('search_date_from', search_date_from, 10800)
        cache.set('search_date_to', search_date_to, 10800)
        
        results = None
        search_flag = False
        
        if search_date_from:
            search_flag = True
            #◯月１日で検索するようにする
            search_date_from += "-01"
            results = Monthly_Representative_Loan.objects.all().filter(occurred_year_month__gte=search_date_from)
        if search_date_to:
            search_flag = True
            #◯月１日で検索するようにする
            search_date_to += "-01"
            if results is None:
                results = Monthly_Representative_Loan.objects.all().filter(occurred_year_month__lte=search_date_to)
            else:
                results = results.filter(occurred_year_month__lte=search_date_to)
        
        if search_flag == True:
            
            if search_date_from:
                search_date_from = search_date_from[:-3]
            if search_date_to:
                search_date_to = search_date_to[:-3]
        
            return render(request,
                   'account/monthly_representative_loan_list.html',     
                   {'monthly_representative_loans': results, 'search_query_date_from': search_date_from,
                                                             'search_query_date_to': search_date_to })    
        else:
            return render(request,
                   'account/monthly_representative_loan_list.html',    
                   {'monthly_representative_loans': monthly_representative_loans})   
    else:
        return render(request,
                   'account/monthly_representative_loan_list.html',     # 使用するテンプレート
                   {'monthly_representative_loans': monthly_representative_loans})         # テンプレートに渡すデータ
    
    
#add240727
def accrued_expence_list(request):
    """未払費用の一覧"""
    
    #デバッグ
    #import pdb; pdb.set_trace()
    #return HttpResponse('◯◯◯の一覧')
    accrued_expences = Accrued_Expence.objects.all().order_by('id')
    
    if request.method == 'GET': # If the form is submitted
        search_date_from = request.GET.get('q_date_from', None)
        search_date_to = request.GET.get('q_date_to', None)
        #キャッシュに保存された検索結果をセット
        if search_date_from == None:
            search_date_from = cache.get('search_date_from')
        if search_date_to == None:
            search_date_to = cache.get('search_date_to')
        
        #キャッシュへ検索結果をセット（最後の引数は、保存したい秒数）
        cache.set('search_date_from', search_date_from, 10800)
        cache.set('search_date_to', search_date_to, 10800)
        
        results = None
        search_flag = False
        
        #import pdb; pdb.set_trace()
        
        if search_date_from:
            search_flag = True
            #◯月１日で検索するようにする
            #search_date_from += "-01"
            results = Accrued_Expence.objects.all().filter(occurred_on__gte=search_date_from)
        
        if search_date_to:
            search_flag = True
            results = Accrued_Expence.objects.all().filter(occurred_on__lte=search_date_to)
        
        if search_flag == True:
        
            return render(request,
                   'account/accrued_expence_list.html',     
                   {'accrued_expences': results, 'search_query_date_from': search_date_from,
                                                             'search_query_date_to': search_date_to })
        else:
            return render(request,
                  'account/accrued_expence_list.html',     # 使用するテンプレート
                  {'accrued_expences': accrued_expences})         # テンプレートに渡すデータ
    else:
        return render(request,
                  'account/accrued_expence_list.html',     # 使用するテンプレート
                  {'accrued_expences': accrued_expences})         # テンプレートに渡すデータ


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

def account_edit(request, account_id=None):
    """勘定科目(貸借用)の編集"""
#    return HttpResponse('勘定科目の編集')
    if account_id:   # account_id が指定されている (修正時)
        account = get_object_or_404(Account, pk=account_id)
    else:         # account_id が指定されていない (追加時)
        account = Account()
    if request.method == 'POST':
        form = AccountForm(request.POST, instance=account)  # POST された request データからフォームを作成
        if form.is_valid():    # フォームのバリデーション
            account = form.save(commit=False)
            account.save()
            return redirect('account:account_list')
    else:    # GET の時
        form = AccountForm(instance=account)  # account インスタンスからフォームを作成

    return render(request, 'account/account_edit.html', dict(form=form, account_id=account_id))

def account_sub_edit(request, account_sub_id=None):
    """勘定補助科目(貸借用)の編集"""
#    return HttpResponse('勘定科目の編集')
    if account_sub_id:   # sub_account_id が指定されている (修正時)
        account_sub = get_object_or_404(Account_Sub, pk=account_sub_id)
    else:                # sub_account_id が指定されていない (追加時)
        account_sub = Account_Sub()
    if request.method == 'POST':
        form = Account_SubForm(request.POST, instance=account_sub)  # POST された request データからフォームを作成
        
        if form.is_valid():    # フォームのバリデーション
            account_sub = form.save(commit=False)
            account_sub.save()
            return redirect('account:account_sub_list')
    else:    # GET の時
        form = Account_SubForm(instance=account_sub)  # account インスタンスからフォームを作成

    return render(request, 'account/account_sub_edit.html', dict(form=form, account_sub_id=account_sub_id))

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
    
    #変更前のもの
    pre_payment_amount = 0    
    pre_payment_date = None
    pre_payment_due_date = None
    #変更前のもの(未払)
    pre_unpaid_amount = 0
    pre_unpaid_date = None
    pre_unpaid_due_date = None
    #関数用
    pre_amount = 0
    pre_date = None
    pre_due_date = None
    #
    after_amount = 0
    after_due_date = None
    after_due_date_changed = None  #add231028
    after_date = None
    #
    
    differ_amount = 0  #差異金額
    new_flag = False
    completed_flag = 0
    is_estimate = 0
    
    global table_type_id
    table_type_id = 1
    
    global income_expence_flag
    income_expence_flag = settings.FLAG_BP_EXPENCE   #収入支出フラグ(支出)
    
#    return HttpResponse('勘定科目の編集')
    if payment_id:   # payment_id が指定されている (修正時)
        payment = get_object_or_404(Payment, pk=payment_id)
        
        #変更前の日付・金額をセット
        pre_payment_amount = payment.billing_amount
        if pre_payment_amount is None:
            pre_payment_amount = payment.rough_estimate
        pre_payment_date = payment.payment_date
        pre_payment_due_date = payment.payment_due_date
        #add131028
        pre_payment_due_date_changed = payment.payment_due_date_changed
        
        #変更前の日付・金額をセット
        pre_unpaid_amount = payment.unpaid_amount
        pre_unpaid_date = payment.unpaid_date
        pre_unpaid_due_date = payment.unpaid_due_date
        #
    else:         # payment_id が指定されていない (追加時)
        payment = Payment()
        
        new_flag = True
        
    if request.method == 'POST':
        form = PaymentForm(request.POST, instance=payment)  # POST された request データからフォームを作成
        
        #import pdb; pdb.set_trace()
                        
        if form.is_valid():    # フォームのバリデーション
        
            ####
            #add230130
            #日次入出金ファイルを更新
            
            completed_flag =  payment.completed_flag  #完了フラグ(フォーム入力後)
            payment_id = payment.id
            
            #
            
            #変更前の日付・金額をセット(関数用)
            pre_amount = pre_payment_amount
            pre_date = pre_payment_date
            pre_due_date = pre_payment_due_date
            #
            
            #差異数量をセット
            #after_amount = 0
            if (request.POST["billing_amount"] != ""):
                after_amount = int(request.POST["billing_amount"])
            elif (request.POST["rough_estimate"] != ""):
                after_amount = int(request.POST["rough_estimate"])
                is_estimate = 1
            
            #after_due_date = None
            #after_date = None
            if request.POST["payment_due_date"] != "":
                after_due_date = datetime.strptime(request.POST["payment_due_date"], '%Y-%m-%d')
                after_due_date = date(after_due_date.year, after_due_date.month, after_due_date.day)
            if request.POST["payment_date"] != "":
                after_date = datetime.strptime(request.POST["payment_date"], '%Y-%m-%d')
                after_date = date(after_date.year, after_date.month, after_date.day)
            
            #add231028
            #支払予定日の変更日対応
            if request.POST["payment_due_date_changed"] != "":
                after_due_date_changed = datetime.strptime(request.POST["payment_due_date_changed"], '%Y-%m-%d')
                after_due_date_changed = date(after_due_date_changed.year, after_due_date_changed.month, after_due_date_changed.day)
                
                if pre_payment_due_date_changed is None and after_due_date_changed is not None:
                    #支払予定変更日が新たにセットされた場合
                    #支払予定日(後)を支払予定変更日としてセット
                    if pre_due_date != after_due_date_changed:
                        after_due_date = after_due_date_changed
                elif after_due_date_changed is not None and \
                     pre_payment_due_date_changed != after_due_date_changed:
                    #支払予定変更日が変更になった場合
                    #予定日(前後)へ変更日ををセット
                    pre_due_date = pre_payment_due_date_changed
                    after_due_date = after_due_date_changed
                elif pre_due_date is not None and pre_payment_due_date_changed is not None and \
                     pre_due_date != pre_payment_due_date_changed:
                    #金額のみのケースを考慮。支払予定変更日がセットされている場合。
                    #予定日(前後)へ変更日をセット
                    pre_due_date = pre_payment_due_date_changed
                    after_due_date = after_due_date_changed
            #add end 
            
            #まず通常の支払日でdaily_cash_flowへ書き込む。
            first_flag = True
            
            #import pdb; pdb.set_trace()
            
            set_amount_to_daily_cash_flow(request, new_flag, completed_flag, first_flag, payment_id, 
                                                 pre_amount, pre_date, pre_due_date,
                                                 after_amount, after_date, after_due_date)
            
            #ここでPaymentを保存(通常の処理)
            payment = form.save(commit=False)
            payment.save()
            
            #日次出金データへも保存(上の行でID作成されていることが前提)
            tmp_date = after_due_date
            if after_date is not None:
                tmp_date = after_date
            
            #Set_Daily_Cash_flow.set_expence(payment, tmp_date, after_amount, is_estimate)
            Set_Daily_Cash_flow.set_payment_to_expence(payment, tmp_date, after_amount, is_estimate)
            ####
                        
            #変更前の未払日付・未払金額をセット(関数用)
            first_flag = False
            
            pre_amount = 0
            if pre_unpaid_amount is not None:
                pre_amount = pre_unpaid_amount
            pre_date = pre_unpaid_date
            pre_due_date = pre_unpaid_due_date
            
            after_amount = 0
            if (request.POST["unpaid_amount"] != ""):
                after_amount = int(request.POST["unpaid_amount"])
            
            #未払金額が発生している場合のみ、日次入出金ファイルを更新
            if after_amount > 0 or \
               pre_amount > 0 and after_amount == 0: 
                
                after_due_date = None
                after_date = None
                
                if request.POST["unpaid_due_date"] != "":
                    after_due_date = datetime.strptime(request.POST["unpaid_due_date"], '%Y-%m-%d')
                    after_due_date = date(after_due_date.year, after_due_date.month, after_due_date.day)
                if request.POST["unpaid_date"] != "":
                    after_date = datetime.strptime(request.POST["unpaid_date"], '%Y-%m-%d')
                    after_date = date(after_date.year, after_date.month, after_date.day)
                    
                set_amount_to_daily_cash_flow(request, new_flag, completed_flag, first_flag, payment_id,
                                                 pre_amount, pre_date, pre_due_date,
                                                 after_amount, after_date, after_due_date)
            ####
            
        
            #payment = form.save(commit=False)
            #payment.save()
            
            ##日次出金データへも保存(上の行でID作成されていることが前提)
            #Set_Daily_Cash_flow.set_expence(payment, after_due_date, after_amount, is_estimate)
            
            #add200121
            #資金繰明細データも保存する
            Set_Cash_Flow_Detail.set_cash_flow_detail(payment.id)
            
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

#日次入出金ファイルへ書き込み
def set_amount_to_daily_cash_flow(request, new_flag, completed_flag, first_flag, table_id, 
                                         pre_amount, pre_date, pre_due_date, 
                                         after_amount, after_date, after_due_date):

    #共通化できるか？？

    differ_amount = 0
    differ_flag = 0
    
    #未処理...
    if new_flag:
    #新規の場合
        differ_amount = after_amount  #数量をそのままセット
        if after_date is not None:
            after_due_date = after_date
    else:
    #更新の場合
        differ_flag = 0
                
        if after_date == None or \
            pre_due_date == after_date:
            #予定日と支払日付が同じで数量のみ変更 = flag0
                
            if pre_date is not None and \
                pre_date != after_date:
            #日付が予定日と同じだが、前回データと支払日が異なる場合
                differ_flag = 1
            elif pre_due_date != after_due_date:
            #予定日が変更になった場合
                differ_flag = 1
        else:
        #予定日と支払日付が異なる場合
            differ_flag = 1
                
        if differ_flag == 0:
            #差異数量を求める
            if pre_amount != after_amount:
                if pre_amount is None:
                    pre_amount = 0
                differ_amount = after_amount - pre_amount
            else:
                differ_amount = 0
        else:
            #日付が違う場合
                    
            if pre_date is None:  #支払日を最初から変更した場合
                pre_date = pre_due_date
                    
            #一旦、変更前の日付から減算する
            Set_Daily_Cash_flow.delete_daily_cash_flow(table_type_id, pre_date, pre_amount, income_expence_flag)
            #
            differ_amount = after_amount     #数量をそのままセット(追加更新のため)
            if after_date is not None:
                after_due_date = after_date  #同様に日付もセット
    
    #import pdb; pdb.set_trace()
    
    #日次入出金ファイルをセット
    #Set_Daily_Cash_flow.set_daily_cash_flow(after_due_date, differ_amount)
    Set_Daily_Cash_flow.set_daily_cash_flow(after_due_date, differ_amount, income_expence_flag)
            
    #日次入出金ファイルの完了フラグをセット
    if first_flag:
        Set_Daily_Cash_flow.set_complete_flag(table_id, table_type_id, after_due_date, completed_flag, income_expence_flag)
            
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
    
    #変数初期化
    pre_cash_book_income = 0
    pre_cash_book_expence = 0
    pre_settlement_date = None
    #関数用
    pre_amount = 0
    pre_date = None
    pre_due_date = None
    #
    after_cash_book_income = 0
    after_cash_book_expence = 0
    after_amount = 0
    after_due_date = None
    after_date = None
    #
    differ_amount = 0  #差異金額
    new_flag = False
    completed_flag = 0
    
    global table_type_id
    table_type_id = 3
    
    global income_expence_flag
    
    #
    
#    return HttpResponse('勘定科目の編集')
    if cash_book_id:   # cash_book_id が指定されている (修正時)
        cash_book = get_object_or_404(Cash_Book, pk=cash_book_id)
        
        #変更前の日付・金額をセット
        if cash_book.incomes is not None:
            pre_cash_book_income = cash_book.incomes
        if cash_book.expences is not None:
            pre_cash_book_expence = cash_book.expences
        pre_settlement_date = cash_book.settlement_date
        #
        
    else:         # cash_book_id が指定されていない (追加時)
        cash_book = Cash_Book()
        new_flag = True
    if request.method == 'POST':
        form = Cash_BookForm(request.POST, instance=cash_book)  # POST された request データからフォームを作成
        if form.is_valid():    # フォームのバリデーション
            
            #import pdb; pdb.set_trace()
            
            #日次入出金ファイルを更新
            completed_flag = 1  #1固定で
            cash_book_id = cash_book.id
            
            #取引先コードの有無(有の場合、入出金ファイルにアクセスしない
            is_partner = False
            if request.POST["partner"] != "":
                is_partner = True
            #
            
            #変更前の日付・金額をセット(関数用)
            if pre_cash_book_expence > 0:
                pre_amount = pre_cash_book_expence
            elif pre_cash_book_income > 0:
                pre_amount = pre_cash_book_income
            
            pre_date = pre_settlement_date
            pre_due_date = pre_settlement_date  #予定日はないが関数用に実績日をそのままセット
            
            #after_cash_book_income = 0
            if request.POST["incomes"] != "":
                after_cash_book_income = int(request.POST["incomes"])
            #after_cash_book_expence = 0
            if request.POST["expences"] != "":
                after_cash_book_expence = int(request.POST["expences"])
            
            #支出→入金or 入金→支出の場合、
            #一旦、変更前の日付から減算する
            if is_partner == False:
                if after_cash_book_income > 0 and pre_cash_book_income == 0:
                    #支出→入金に変更したとみなす
                    new_flag = True
                    Expence.objects.filter(table_id=cash_book_id, table_type_id=settings.TABLE_TYPE_CASH_BOOK).delete()
                    income_expence_flag = settings.FLAG_BP_EXPENCE
                    Set_Daily_Cash_flow.delete_daily_cash_flow(table_type_id, pre_date, pre_amount, income_expence_flag)
                elif after_cash_book_expence > 0 and pre_cash_book_expence == 0:
                    #入金→支出に変更したとみなす
                    new_flag = True
                    Deposit.objects.filter(table_id=cash_book_id, table_type_id=settings.TABLE_TYPE_CASH_BOOK).delete()
                    income_expence_flag = settings.FLAG_BP_INCOME
                    Set_Daily_Cash_flow.delete_daily_cash_flow(table_type_id, pre_date, pre_amount, income_expence_flag)
            
            #変更後金額をセット
            if after_cash_book_income > 0:
                after_amount = after_cash_book_income
                income_expence_flag = settings.FLAG_BP_INCOME
            elif after_cash_book_expence > 0:
                after_amount = after_cash_book_expence
                income_expence_flag = settings.FLAG_BP_EXPENCE
            #変更後日付をセット
            if request.POST["settlement_date"] != "":
                after_date = datetime.strptime(request.POST["settlement_date"], '%Y-%m-%d')
                after_date = date(after_date.year, after_date.month, after_date.day)
            after_due_date = after_date  #予定日はないが関数用に実績日をそのままセット
            #
            first_flag = True
            #if cash_book.partner is None:
            if is_partner == False:
                set_amount_to_daily_cash_flow(request, new_flag, completed_flag, first_flag, cash_book_id, pre_amount, pre_date, pre_due_date,
                                                 after_amount, after_date, after_due_date)
            #
            
            
            cash_book = form.save(commit=False)
            cash_book.save()
            
            #日次入金・出金データを作成(上の行でID作成されていることが前提)
            tmp_date = after_date
            if is_partner == False:
                if after_cash_book_income > 0:
                #収入の場合
                    Set_Daily_Cash_flow.set_cash_book_to_deposit(cash_book, tmp_date, after_amount)
                #支出の場合
                elif after_cash_book_expence > 0:
                    Set_Daily_Cash_flow.set_cash_book_to_expence(cash_book, tmp_date, after_amount)
                
            #add200124
            #社長のデータの場合は、試算表・貸借表のデータにも保存する
            Set_Cash_Flow_Detail.set_cash_flow_detail_from_cash_book(cash_book.id)
            
            #del230330 使われてない為(別用途で使用開始した)
            #Set_Cash_Book_To_Balance_Sheet.set_balance_sheet(cash_book.id)
            #
            
            #upd231129
            #代表者貸付金データへも保存
            Set_Representative_Loan.set_cash_book_to_representative(cash_book)
            
            #table_id, occurred_on, description, amount, is_representative
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
    
    #変数初期化
    
    pre_balance_sheet_amount = 0
    pre_accrual_date = None
    #関数用
    pre_amount = 0
    pre_date = None
    pre_due_date = None
    #
    after_amount = 0
    after_due_date = None
    after_date = None
    #
    differ_amount = 0  #差異金額
    new_flag = False
    completed_flag = 0
    
    pre_income_expence_flag = None
    
    global table_type_id
    table_type_id = settings.TABLE_TYPE_BALANCE_SHEET
    
    global income_expence_flag
    #global no_complete_flag
    #no_complete_flag = True  #complete_flagを操作しない
    #
        
#    return HttpResponse('貸借表の編集')
    if balance_sheet_id:   # account_title_id が指定されている (修正時)
        balance_sheet = get_object_or_404(Balance_Sheet, pk=balance_sheet_id)
        
        #add230328
        #変更前の日付・金額をセット
        pre_balance_sheet_amount = balance_sheet.amount
        pre_accrual_date = balance_sheet.accrual_date
        #
        
        pre_income_expence_flag = settings.FLAG_BP_EXPENCE     #デフォルト(貸)
        
        if balance_sheet.borrow_lend_id is not None and \
           balance_sheet.borrow_lend_id == 1:
            pre_income_expence_flag = settings.FLAG_BP_INCOME  #借
        
    else:         # cash_flow_header_id が指定されていない (追加時)
        balance_sheet = Balance_Sheet()
    
        new_flag = True
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
        
        #?? del230329
        #発生日をセット(開始日より)
        #if search_accrual_date_from:
        #    balance_sheet.accrual_date = search_accrual_date_from
        #貸借IDをセット
        #if search_query_borrow_lend_id:
        #    balance_sheet.borrow_lend_id = search_query_borrow_lend_id
            
        #import pdb; pdb.set_trace()
    #
    
    if request.method == 'POST':
        form = Balance_SheetForm(request.POST, instance=balance_sheet)  # POST された request データからフォームを作成
        
        #import pdb; pdb.set_trace()
        
        if form.is_valid():    # フォームのバリデーション
            
            #日次入出金ファイルを更新
            
            completed_flag = 1  #1固定で
            balance_sheet_id = balance_sheet.id
            #
            
            #変更前の日付・金額をセット(関数用)
            pre_amount = pre_balance_sheet_amount
            pre_date = pre_accrual_date
            pre_due_date = pre_accrual_date  #予定日はないが関数用に実績日をそのままセット
            #
            
            #収支フラグ判定
            income_expence_flag = settings.FLAG_BP_INCOME
            if request.POST["borrow_lend_id"] != "":
                if request.POST["borrow_lend_id"] == "0":  #貸
                    income_expence_flag = settings.FLAG_BP_EXPENCE  #支出
            
            #import pdb; pdb.set_trace()
            
            ###income_expence_flag !==== borrow_lend_id
            
            #貸→借 or 借→貸の場合
            #一旦、変更前の日付から減算する
            if pre_income_expence_flag is not None and \
               pre_income_expence_flag != income_expence_flag:
               
                if pre_income_expence_flag == settings.FLAG_BP_EXPENCE:
                #貸→借の場合
                    new_flag = True
                    Expence.objects.filter(table_id=balance_sheet_id, table_type_id=settings.TABLE_TYPE_BALANCE_SHEET).delete()
                    Set_Daily_Cash_flow.delete_daily_cash_flow(table_type_id, pre_date, pre_amount, pre_income_expence_flag)
                elif pre_income_expence_flag == settings.FLAG_BP_INCOME:
                #借→貸の場合
                    new_flag = True
                    Deposit.objects.filter(table_id=balance_sheet_id, table_type_id=settings.TABLE_TYPE_BALANCE_SHEET).delete()
                    Set_Daily_Cash_flow.delete_daily_cash_flow(table_type_id, pre_date, pre_amount, pre_income_expence_flag)
            #
            
            #差異数量をセット
            if (request.POST["amount"] != ""):
                after_amount = int(request.POST["amount"])
            
            #日付をセット
            if request.POST["accrual_date"] != "":
                after_date = datetime.strptime(request.POST["accrual_date"], '%Y-%m-%d')
                after_date = date(after_date.year, after_date.month, after_date.day)
            after_due_date = after_date  #予定日はないが関数用に実績日をそのままセット
            
            
            #import pdb; pdb.set_trace()
            
            #まず通常の支払日でdaily_cash_flowへ書き込む。
            first_flag = True
            
            set_amount_to_daily_cash_flow(request, new_flag, completed_flag, first_flag, balance_sheet_id, pre_amount, pre_date, pre_due_date,
                                                 after_amount, after_date, after_due_date)
            
            
            #保存(通常の処理)
            balance_sheet = form.save(commit=False)
            balance_sheet.save()
            
            #日次入金・出金データを作成(上の行でID作成されていることが前提)
            #tmp_date = after_due_date
            tmp_date = after_date
            #if after_date is not None:
            #    tmp_date = after_date
            
            if income_expence_flag == settings.FLAG_BP_INCOME:
            #収入の場合
                Set_Daily_Cash_flow.set_deposit(balance_sheet, tmp_date, after_amount)
            elif income_expence_flag == settings.FLAG_BP_EXPENCE:
            #支払の場合
                Set_Daily_Cash_flow.set_balance_sheet_to_expence(balance_sheet, tmp_date, after_amount)
            
            #
            
            #代表者貸付金データへも保存
            Set_Representative_Loan.set_balance_sheet_to_representative(balance_sheet.id, after_date, \
                                    balance_sheet.description2, income_expence_flag, after_amount, \
                                    balance_sheet.bank_id, balance_sheet.is_representative)
            #
            
            
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

def daily_representative_loan_edit(request, daily_representative_loan_id=None):
    """代表者貸付金の編集"""
#    return HttpResponse('取引先の編集')
    if daily_representative_loan_id:   # daily_representative_loan_id が指定されている (修正時)
        daily_representative_loan = get_object_or_404(Daily_Representative_Loan, pk=daily_representative_loan_id)
    else:         # partner_id が指定されていない (追加時)
        daily_representative_loan = Daily_Representative_Loan()

    if request.method == 'POST':
        form = Daily_Representative_LoanForm(request.POST, instance=daily_representative_loan)  # POST された request データからフォームを作成
        if form.is_valid():    # フォームのバリデーション
            daily_representative_loan = form.save(commit=False)
            daily_representative_loan.save()
            return redirect('account:daily_representative_loan_list')
    else:    # GET の時
        form = Daily_Representative_LoanForm(instance=daily_representative_loan)  # partner インスタンスからフォームを作成

    return render(request, 'account/daily_representative_loan_edit.html', dict(form=form, daily_representative_loan_id=daily_representative_loan_id))

def monthly_representative_loan_edit(request, monthly_representative_loan_id=None):
    """月次貸付金の編集"""
#    return HttpResponse('取引先の編集')
    if monthly_representative_loan_id:   # daily_representative_loan_id が指定されている (修正時)
        monthly_representative_loan = get_object_or_404(Monthly_Representative_Loan, pk=monthly_representative_loan_id)
    else:         # partner_id が指定されていない (追加時)
        monthly_representative_loan = Monthly_Representative_Loan()

    if request.method == 'POST':
        form = Monthly_Representative_LoanForm(request.POST, instance=monthly_representative_loan)  # POST された request データからフォームを作成
        if form.is_valid():    # フォームのバリデーション
            monthly_representative_loan = form.save(commit=False)
            monthly_representative_loan.save()
            return redirect('account:monthly_representative_loan_list')
    else:    # GET の時
        form = Monthly_Representative_LoanForm(instance=monthly_representative_loan)  # partner インスタンスからフォームを作成

    return render(request, 'account/monthly_representative_loan_edit.html', dict(form=form, monthly_representative_loan_id=monthly_representative_loan_id))

#add240729
def accrued_expence_edit(request, accrued_expence_id=None):
    """未払費用の編集"""
    
    #作成中.....
    if accrued_expence_id:   # accrued_expence_id が指定されている (修正時)
        accrued_expence = get_object_or_404(Accrued_Expence, pk=accrued_expence_id)
    else:         # partner_id が指定されていない (追加時)
        accrued_expence = Accrued_Expence()

    if request.method == 'POST':
        form = Accrued_ExpenceForm(request.POST, instance=accrued_expence)  # POST された request データからフォームを作成
        if form.is_valid():    # フォームのバリデーション
            accrued_expence = form.save(commit=False)
            accrued_expence.save()
            return redirect('account:accrued_expence_list')
    else:    # GET の時
        form = Accrued_ExpenceForm(instance=accrued_expence)  # partner インスタンスからフォームを作成

    return render(request, 'account/accrued_expence_edit.html', dict(form=form, accrued_expence_id=accrued_expence_id))
    
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

def account_del(request, account_id):
    """勘定科目(貸借用)の削除"""
    if int(account_id) > 4:
        account = get_object_or_404(Account, pk=account_id)
        account.delete()
        return redirect('account:account_list')
    else:
        #特定のIDは削除させない
        messages.success(request, '※指定したIDはシステムで使用する為、削除できません。')
        return redirect('account:account_list')

def account_sub_del(request, account_sub_id):
    """勘定補助科目(貸借用)の削除"""
    account_sub = get_object_or_404(Account_Sub, pk=account_sub_id)
    account_sub.delete()
    return redirect('account:account_sub_list')
    
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
    
    #日次出金データを削除
    #Set_Daily_Cash_flow.delete_expence(payment_id)
    #貸借表データがあれば削除
    #Expence.objects.filter(table_id=payment_id).delete()
    Expence.objects.filter(table_id=payment_id, table_type_id=1).delete()
    
    global table_type_id
    table_type_id = 1
    
    global income_expence_flag
    income_expence_flag = 1   #収入支出フラグ(支出)
    
    #日次入出金データも減算(削除はしない)
    if payment.payment_date is not None:
        Set_Daily_Cash_flow.delete_daily_cash_flow(table_type_id, payment.payment_date, payment.billing_amount, income_expence_flag)
    elif payment.payment_due_date_changed is not None:
    #add240522
    #支払予定変更日があれば、そこから削除するようにする。
        Set_Daily_Cash_flow.delete_daily_cash_flow(table_type_id, payment.payment_due_date_changed, payment.billing_amount, income_expence_flag)
    else:
        Set_Daily_Cash_flow.delete_daily_cash_flow(table_type_id, payment.payment_due_date, payment.billing_amount, income_expence_flag)
    #
    
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
    
    #日次入金・出金データを削除
    #if cash_book.expences is not None and cash_book.expences > 0:
        
    #elif cash_book.incomes is not None and cash_book.incomes > 0:
    if cash_book.incomes is not None and cash_book.incomes > 0:
        #入金
        Deposit.objects.filter(table_id=cash_book_id, table_type_id=settings.TABLE_TYPE_CASH_BOOK).delete()
    elif cash_book.expences is not None and cash_book.expences > 0:
        #出金
        Expence.objects.filter(table_id=cash_book_id, table_type_id=settings.TABLE_TYPE_CASH_BOOK).delete()
    
    #日次入出金データも減算(削除はしない)
    global table_type_id
    table_type_id = settings.TABLE_TYPE_CASH_BOOK
    
    amount = 0
    global income_expence_flag
    if cash_book.expences is not None and cash_book.expences > 0:
        income_expence_flag = settings.FLAG_BP_EXPENCE
        amount = cash_book.expences
    elif cash_book.incomes is not None and cash_book.incomes > 0:
        income_expence_flag = settings.FLAG_BP_INCOME
        amount = cash_book.incomes
    
    if cash_book.partner is None:  #取引先ID未入力の場合のみ消去
        Set_Daily_Cash_flow.delete_daily_cash_flow(table_type_id, cash_book.settlement_date, amount, income_expence_flag)
    #
    
    #貸付金データの削除 (add240130)
    Daily_Representative_Loan.objects.filter(table_type_id=2, table_id=cash_book_id).delete()
    #
    
    return redirect('account:cash_book_list')

def cash_book_weekly_del(request, cash_book_weekly_id):
    """支払の削除"""
    cash_book_weekly = get_object_or_404(Cash_Book, pk=cash_book_weekly_id)
    cash_book_weekly.delete()
    return redirect('account:cash_book_weekly_list')

def cash_flow_detail_expected_del(request, cash_flow_detail_expected_id):
    """資金繰明細(予定)の削除"""
    cash_flow_detail_expected = get_object_or_404(Cash_Flow_Detail_Expected, pk=cash_flow_detail_expected_id)
    cash_flow_detail_expected.delete()
    return redirect('account:cash_flow_detail_expected_list')
def cash_flow_detail_actual_del(request, cash_flow_detail_actual_id):
    """資金繰明細(予定)の削除"""
    cash_flow_detail_actual = get_object_or_404(Cash_Flow_Detail_Actual, pk=cash_flow_detail_actual_id)
    cash_flow_detail_actual.delete()
    return redirect('account:cash_flow_detail_actual_list')
def balance_sheet_del(request, balance_sheet_id):
    """貸借表の削除"""
    #import pdb; pdb.set_trace()
    
    balance_sheet = get_object_or_404(Balance_Sheet, pk=balance_sheet_id)
    balance_sheet.delete()
    
    #日次入金・出金データを削除
    if balance_sheet.borrow_lend_id == 0: #貸
        Expence.objects.filter(table_id=balance_sheet_id, table_type_id=2).delete()
    else:  #借
        Deposit.objects.filter(table_id=balance_sheet_id, table_type_id=2).delete()
    
    #日次入出金データも減算(削除はしない)
    global table_type_id
    table_type_id = settings.TABLE_TYPE_BALANCE_SHEET
    
    global income_expence_flag
    income_expence_flag = settings.FLAG_BP_EXPENCE
    if balance_sheet.borrow_lend_id == 1:
        income_expence_flag = settings.FLAG_BP_INCOME
        
    Set_Daily_Cash_flow.delete_daily_cash_flow(table_type_id, balance_sheet.accrual_date, balance_sheet.amount, income_expence_flag)
    #
    
    #貸付金データの削除 (add240130)
    Daily_Representative_Loan.objects.filter(table_type_id=1, table_id=balance_sheet_id).delete()
    #
    
    return redirect('account:balance_sheet_list')
    
def daily_representative_loan_del(request, daily_representative_loan_id):
    """代表者貸付金の削除"""
    #return HttpResponse('代表者貸付金の削除')
    daily_representative_loan = get_object_or_404(Daily_Representative_Loan, pk=daily_representative_loan_id)
    daily_representative_loan.delete()
    return redirect('account:daily_representative_loan_list')

def monthly_representative_loan_del(request, monthly_representative_loan_id):
    """月次貸付金の削除"""
    #return HttpResponse('代表者貸付金の削除')
    monthly_representative_loan = get_object_or_404(Monthly_Representative_Loan, pk=monthly_representative_loan_id)
    monthly_representative_loan.delete()
    return redirect('account:monthly_representative_loan_list')

def accrued_expence_del(request, accrued_expence_id):
    """未払費用の削除"""
    #return HttpResponse('未払費用の削除')
    accrued_expence = get_object_or_404(Accrued_Expence, pk=accrued_expence_id)
    accrued_expence.delete()
    return redirect('account:accrued_expence_list')
    
#検索フォーム用・・・
#def get_queryset(self):
#    #デバッグ？
#    import pdb; pdb.set_trace()

#    query = self.request.GET.get('q') 
#    if query:
#        return Account_Title.objects.filter(name__icontains=query)
#    else:
#        return Account_Title.objects.all()

