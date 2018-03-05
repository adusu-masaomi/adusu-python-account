from django.shortcuts import render, get_object_or_404, redirect
#from django.core.urlresolvers import reverse

# Create your views here.
#from django.http import HttpResponse
#
from account.models import Partner
from account.models import Account_Title
from account.models import Bank
from account.models import Bank_Branch
from account.models import Payment
#
from account.forms import PartnerForm
from account.forms import Account_TitleForm
from account.forms import BankForm
from account.forms import Bank_BranchForm
from account.forms import PaymentForm

import json 
from itertools import chain
from django.core.cache import cache
from django.db.models import Sum

from django.http import Http404, HttpResponse, QueryDict
from django.template import RequestContext

#レポート関連
#from reportlab.pdfgen import canvas
#from reportlab.lib.pagesizes import A4, landscape, portrait
#from reportlab.pdfbase import pdfmetrics
#from reportlab.pdfbase.cidfonts import UnicodeCIDFont
#from reportlab.pdfbase.pdfmetrics import registerFont
#from reportlab.pdfbase.ttfonts import TTFont
#from reportlab.lib.units import mm
#from django.conf import settings
#from datetime import datetime

def index(request):
    
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
    payments = Payment.objects.all().order_by('id')
        
        
    if request.method == 'GET': # If the form is submitted
        
        search_query_trade_division_id = request.GET.get('q', None)
        search_query_month = request.GET.get('q_month', None)
        
        #キャッシュに保存された検索結果をセット
        if search_query_trade_division_id == None:
            search_query_trade_division_id = cache.get('search_query_trade_division_id')
            
        if search_query_month == None:
            search_query_month = cache.get('search_query_month')
            
        
        #キャッシュへ検索結果をセット（最後の引数は、保存したい秒数）→２４時間とする
        cache.set('search_query_trade_division_id', search_query_trade_division_id, 86400)
        cache.set('search_query_month', search_query_month, 86400)
        #
        
        
        if search_query_trade_division_id:
            if search_query_month:
                #取引区分＆支払月で検索
                #◯月１日で検索するようにする
                search_query_month += "-01"
                results = Payment.objects.all().filter(trade_division_id__icontains=search_query_trade_division_id, billing_year_month=search_query_month)
            else:
                #取引区分で検索
                results = Payment.objects.all().filter(trade_division_id__icontains=search_query_trade_division_id)
        elif search_query_month:
        #支払月のみで検索
            #◯月１日で検索するようにする
            search_query_month += "-01"
            results = Payment.objects.all().filter(billing_year_month=search_query_month)
        else:
            return render(request,
                'account/payment_list.html',     # 使用するテンプレート
                {'payments': payments})         # テンプレートに渡すデータ
        
        if (search_query_trade_division_id or search_query_month):
        #検索クエリーが入力されている場合のみ
            #合計金額
            total_price = results.aggregate(Sum('billing_amount'))
           
            return render(request,
                'account/payment_list.html',     # 使用するテンプレート
                {'payments': results, 'total_price': total_price})         # テンプレートに渡すデータ
        
    # Your code
    #return render(request,
    #              'account/payment_list.html',     # 使用するテンプレート
    #              {'payments': payments})         # テンプレートに渡すデータ

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

# Ajax
#銀行から支店を絞り込む
def ajax_bank_branch_extract(req):   
    import json
    from django.http import HttpResponse,Http404

    if req.method == 'GET':
        bank_id = req.GET['bank_id']  # GETデータを取得して
        
        #response = [{'name': '', 'id': ''}
        empty_value = {'id':"" , 'name':"" }
        
        response = Bank_Branch.objects.all().filter(bank_id__exact=bank_id).values("id","name")
        
        #response.update(filter)
        #response["dict"] = empty_value
        
        #response = list(response)
        response = list(chain(empty_value,response))
        
        #import pdb; pdb.set_trace()
        
        json_data = json.dumps({"HTTPRESPONSE":response})   # JSON形式に直す
        return HttpResponse(json_data, content_type="application/json")
    else:
        raise Http404  # GETリクエストを404扱いにしているが、実際は別にしなくてもいいかも

#テンプレートのソート用（取引先）
def ajax_partner_sort(request):

    if request.method == 'POST':

        # request.POST['content'] is a query string like 'entry[]=3&entry[]=2&entry[]=1'
        # convert to a QueryDict so we can do things with it
        partners = QueryDict(request.POST['content'])
       
        for index, partner_id in enumerate(partners.getlist('partner[]')):
            # save index of entry_id as it's new order value
            partner = Partner.objects.get(id=partner_id)
            partner.order = index
            partner.save()
            
    #２つのリストのソートを行うやり方（使えるかも？しれないので残しておく）
    # split our entries arbitrarily, so we can have two lists on the page...
    #entry_list1 = Partner.objects.order_by('order')[:2]
    #entry_list2 = Partner.objects.order_by('order')[2:]
    #context = {'entry_list1': entry_list1, 'entry_list2': entry_list2}
    #return render_to_response('account/partner_list.html', context, context_instance=RequestContext(request))
    
    return render(request, 'account/partner_list.html')

#テンプレートのソート用（支払先）
def ajax_payment_sort(request):

    if request.method == 'POST':

        # request.POST['content'] is a query string like 'entry[]=3&entry[]=2&entry[]=1'
        # convert to a QueryDict so we can do things with it
        payments = QueryDict(request.POST['content'])
       
        for index, payment_id in enumerate(payments.getlist('payment[]')):
            # save index of entry_id as it's new order value
            payment = Payment.objects.get(id=payment_id)
            payment.order = index
            payment.save()
            
    return render(request, 'account/payment_list.html')


#検索フォーム用・・・
#def get_queryset(self):
#    #デバッグ？
#    import pdb; pdb.set_trace()

#    query = self.request.GET.get('q') 
#    if query:
#        return Account_Title.objects.filter(name__icontains=query)
#    else:
#        return Account_Title.objects.all()

