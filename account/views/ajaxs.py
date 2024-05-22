#Ajax用ビュー
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from account.models import Partner
from account.models import Account
from account.models import Account_Sub
from account.models import Account_Title
from account.models import Bank
from account.models import Bank_Branch
from account.models import Payment
from account.models import Cash_Book

from django.conf import settings
import json 
from itertools import chain
from django.core.cache import cache
#from django.db.models import Sum

from django.http import Http404, HttpResponse, QueryDict
import json
from django.http.response import JsonResponse
from django.template import RequestContext

#centos7でインストール不可のため、削除 220218
#from sklearn.externals import joblib
#import numpy as np

# Ajax
#銀行から支店を絞り込む
def ajax_bank_branch_extract(req):   
    #import json
    #from django.http import HttpResponse,Http404

    if req.method == 'GET':
        bank_id = req.GET['bank_id']  # GETデータを取得して
        
        empty_value = {'id':"" , 'name':"" }
        
        response = Bank_Branch.objects.all().filter(bank_id__exact=bank_id).values("id","name")
        
        response = list(chain(empty_value,response))
        
        
        json_data = json.dumps({"HTTPRESPONSE":response})   # JSON形式に直す
        return HttpResponse(json_data, content_type="application/json")
    else:
        raise Http404  # GETリクエストを404扱いにしているが、実際は別にしなくてもいいかも

#工事中
#取引先情報を取得する
def ajax_partner_extract(req):   
    import json
    from django.http import HttpResponse,Http404

    if req.method == 'GET':
        partner_id = req.GET['partner_id']  # GETデータを取得して
        
        #add240424 source_bank_id追加
        response = Partner.objects.all().filter(id__exact=partner_id).values("id", "trade_division_id", 
           "account_title", "payment_method_id", "pay_day_division", "pay_day", "source_bank_id" )
        
        response = list(response)
        
        #デバッグ
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

#テンプレートのソート用（勘定科目）
def ajax_account_title_sort(request):
    
    #import pdb; pdb.set_trace()
    
    if request.method == 'POST':

        # request.POST['content'] is a query string like 'entry[]=3&entry[]=2&entry[]=1'
        account_titles = QueryDict(request.POST['content'])
       
        for index, account_title_id in enumerate(account_titles.getlist('account_title[]')):
            # save index of entry_id as it's new order value
            account_title = Account_Title.objects.get(id=account_title_id)
            account_title.order = index
            account_title.save()
            
    return render(request, 'account/account_title_list.html')

#テンプレートのソート用（勘定補助科目(貸借用)）
def ajax_account_sub_sort(request):

    #デバッグ
    #import pdb; pdb.set_trace()

    if request.method == 'POST':

        # request.POST['content'] is a query string like 'entry[]=3&entry[]=2&entry[]=1'
        account_subs = QueryDict(request.POST['content'])
       
        for index, account_sub_id in enumerate(account_subs.getlist('account_sub[]')):
            
            # save index of entry_id as it's new order value
            account_sub = Account_Sub.objects.get(id=account_sub_id)
            account_sub.order = index
            account_sub.save()
            
    return render(request, 'account/account_sub_list.html')

#テンプレートのソート用（勘定科目(貸借用)）
def ajax_account_sort(request):

    #デバッグ
    #import pdb; pdb.set_trace()

    if request.method == 'POST':

        # request.POST['content'] is a query string like 'entry[]=3&entry[]=2&entry[]=1'
        accounts = QueryDict(request.POST['content'])
       
        for index, account_id in enumerate(accounts.getlist('account[]')):
            # save index of entry_id as it's new order value
            account = Account.objects.get(id=account_id)
            account.order = index
            account.save()
            
    return render(request, 'account/account_list.html')

#テンプレートのソート用（銀行）
def ajax_bank_sort(request):
    
    #import pdb; pdb.set_trace()
    
    if request.method == 'POST':

        # request.POST['content'] is a query string like 'entry[]=3&entry[]=2&entry[]=1'
        banks = QueryDict(request.POST['content'])
       
        for index, bank_id in enumerate(banks.getlist('bank[]')):
            # save index of entry_id as it's new order value
            bank = Bank.objects.get(id=bank_id)
            bank.order = index
            bank.save()
            
    return render(request, 'account/bank_list.html')

#テンプレートのソート用（銀行支店）
def ajax_bank_branch_sort(request):

    if request.method == 'POST':

        # request.POST['content'] is a query string like 'entry[]=3&entry[]=2&entry[]=1'
        bank_branchs = QueryDict(request.POST['content'])
       
        for index, bank_branch_id in enumerate(bank_branchs.getlist('bank_branch[]')):
            # save index of entry_id as it's new order value
            bank_branch = Bank_Branch.objects.get(id=bank_branch_id)
            bank_branch.order = index
            bank_branch.save()
            
    return render(request, 'account/bank_branch_list.html')

#テンプレートのソート用（出納帳）
def ajax_cash_book_sort(request):

    if request.method == 'POST':

        # request.POST['content'] is a query string like 'entry[]=3&entry[]=2&entry[]=1'
        cash_books = QueryDict(request.POST['content'])
       
        #デバッグ
        #import pdb; pdb.set_trace()
       
        for index, cash_book_id in enumerate(cash_books.getlist('cash_book[]')):
            # save index of entry_id as it's new order value
            cash_book = Cash_Book.objects.get(id=cash_book_id)
            cash_book.order = index
            cash_book.save()
            
    return render(request, 'account/cash_book_list.html')

def ajax_cash_book_predict_account_tile(req):
    if req.method == 'GET':
        #del220218 centos7インストール不可の為抹消
        #もったいないので、消さないこと
        #clf = joblib.load(settings.DIR_CLF_CASH_BOOK)
        #vect = joblib.load(settings.DIR_VECT_CASH_BOOK)
        
        #content = req.GET['content']  # GETデータを取得して
        #content = np.array([content])
        #content = content.reshape(1)
        
        #X = vect.transform(content)
        
        #result = clf.predict(X)
            
        #response = result[0].tolist()
        
        #json_data = json.dumps({"HTTPRESPONSE":response})   # JSON形式に直す
        #return HttpResponse(json_data, content_type="application/json")
        return 0
