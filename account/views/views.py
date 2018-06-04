from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from account.models import Partner
from account.models import Account_Title
from account.models import Bank
from account.models import Bank_Branch
from account.models import Payment
from account.models import Cash_Book
from account.models import Staff
from account.models import Cash_Book_Weekly
#
from account.forms import PartnerForm
from account.forms import Account_TitleForm
from account.forms import BankForm
from account.forms import Bank_BranchForm
from account.forms import PaymentForm
from account.forms import Cash_BookForm
from account.forms import Cash_Book_WeeklyForm

import json 
from itertools import chain
from django.core.cache import cache
from django.db.models import Sum

from django.http import Http404, HttpResponse, QueryDict
from django.template import RequestContext
#from django.core.urlresolvers import reverse

from account.views import aggregate_weekly as Aggregate

#ログイン用
#from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
from django.views.generic import View
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
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
    #import pdb; pdb.set_trace()
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
        search_query_month_from = request.GET.get('q_month_from', None)
        search_query_month_to = request.GET.get('q_month_to', None)
        search_query_payment = request.GET.get('q_payment', None)
        search_query_partner = request.GET.get('q_partner', None)
        
        #キャッシュに保存された検索結果をセット(年月のみ)
        if search_query_trade_division_id == None:
            search_query_trade_division_id = cache.get('search_query_trade_division_id')
            
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
        #
        #キャッシュへ検索結果をセット（最後の引数は、保存したい秒数）
        cache.set('search_query_trade_division_id', search_query_trade_division_id, 86400)
        cache.set('search_query_month_from', search_query_month_from, 86400)
        cache.set('search_query_month_to', search_query_month_to, 86400)
        
        #add180524
        cache.set('search_query_trade_division_id', search_query_trade_division_id, 10800)
        cache.set('search_query_payment', search_query_payment, 10800)
        cache.set('search_query_partner', search_query_partner, 10800)
        #
        
        ###フィルタリング
        results = None
        search_flag = False
        
        if search_query_month_from:
        #年月で絞り込み(開始)
            search_flag = True
            #◯月１日で検索するようにする
            search_query_month_from += "-01"
            #results = Payment.objects.all().filter(billing_year_month=search_query_month_from).order_by('order')
            results = Payment.objects.all().filter(billing_year_month__gte=search_query_month_from).order_by('order')
        
        if search_query_month_to:
        #年月で絞り込み(終了)
            search_flag = True
            #◯月１日で検索するようにする
            search_query_month_to += "-01"
            #results = Payment.objects.all().filter(billing_year_month=search_query_month_from).order_by('order')
            if results is None:
                results = Payment.objects.all().filter(billing_year_month__lte=search_query_month_to).order_by('order')
            else:
                results = results.filter(billing_year_month__lte=search_query_month_to).order_by('order')
            
        if search_query_trade_division_id:
        #取引区分で絞り込み
            search_flag = True
            if results is None:
                results = Payment.objects.all().filter(trade_division_id__icontains=search_query_trade_division_id).order_by('order')
            else:
                results = results.filter(trade_division_id__icontains=search_query_trade_division_id).order_by('order')
        
        if search_query_payment:
        #支払方法で絞り込み
            search_flag = True
            if results is None:
                results = Payment.objects.all().filter(payment_method_id__icontains=search_query_payment).order_by('order')
            else:
                results = results.filter(payment_method_id__icontains=search_query_payment).order_by('order')
        
        if search_query_partner:
        #支払先で絞り込み
            search_flag = True
            if results is None:
                #results = Partner.objects.all().filter(partner_id=search_query_partner).order_by('order')
                results = Payment.objects.all().filter(partner_id=search_query_partner).order_by('order')
            else:
                results = results.filter(partner_id=search_query_partner).order_by('order')
                
        ###
        
        #sort_by = request.GET.get('sort_by')
        #if sort_by is not None:
        #    results = results.order_by(sort_by)
        
        #if (search_query_trade_division_id or search_query_month):
        if search_flag == True:
        #検索クエリーが入力されている場合のみ
            #合計金額
            total_price = results.aggregate(Sum('billing_amount'))
            
            #日付は再び年月のみにする
            search_query_month_from = search_query_month_from.rstrip("-01")
            search_query_month_to = search_query_month_to.rstrip("-01")
            #
            
            return render(request,
                'account/payment_list.html',     # 使用するテンプレート
                {'payments': results, 'partners': partners, 'total_price': total_price, 'search_query_month_from': search_query_month_from,
                  'search_query_month_to': search_query_month_to, 
                  'search_query_trade_division_id': search_query_trade_division_id, 
                  'search_query_payment': search_query_payment, 'search_query_partner': search_query_partner})         # テンプレートに渡すデータ
        else:
            
                return render(request,
                'account/payment_list.html',     # 使用するテンプレート
                {'payments': payments, 'partners': partners })         # テンプレートに渡すデータ
        
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
        
        search_settlement_date_from = request.GET.get('q_settlement_date_from', None)
        search_settlement_date_to = request.GET.get('q_settlement_date_to', None)
        
        search_receipt_date_from = request.GET.get('q_receipt_date_from', None)
        search_receipt_date_to = request.GET.get('q_receipt_date_to', None)
        
        search_account_title = request.GET.get('q_account_title', None)
        search_staff = request.GET.get('q_staff', None)
        
        
        
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
                 'search_account_title':search_account_title, 'search_staff':search_staff })         # テンプレートに渡すデータ
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
            return redirect('account:payment_list')
    else:    # GET の時
        
    
        form = PaymentForm(instance=payment)  # payment インスタンスからフォームを作成

    return render(request, 'account/payment_edit.html', dict(form=form, payment_id=payment_id))


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


def cash_book_del(request, cash_book_id):
    """支払の削除"""
    cash_book = get_object_or_404(Cash_Book, pk=cash_book_id)
    cash_book.delete()
    return redirect('account:cash_book_list')


def cash_book_weekly_del(request, cash_book_weekly_id):
    """支払の削除"""
    cash_book_weekly = get_object_or_404(Cash_Book, pk=cash_book_weekly_id)
    cash_book_weekly.delete()
    return redirect('account:cash_book_weekly_list')

#検索フォーム用・・・
#def get_queryset(self):
#    #デバッグ？
#    import pdb; pdb.set_trace()

#    query = self.request.GET.get('q') 
#    if query:
#        return Account_Title.objects.filter(name__icontains=query)
#    else:
#        return Account_Title.objects.all()

