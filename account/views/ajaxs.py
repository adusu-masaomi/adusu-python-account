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
from account.models import Compensation         #add250407
from account.models import Daily_Compensation   #add250423

from django.conf import settings
import json 
from itertools import chain
from django.core.cache import cache
#from django.db.models import Sum

from django.http import Http404, HttpResponse, QueryDict
import json
from django.http.response import JsonResponse
from django.template import RequestContext

from datetime import datetime
from dateutil.relativedelta import relativedelta

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

#役員報酬への振り分け
def ajax_set_compensation(request):
    
    if request.method == 'GET':
        
        paid_on_str = request.GET['paid_on']
        daily_amount = request.GET['amount']
        id = request.GET['id']
        
        if daily_amount is not None:
            daily_amount = int(daily_amount)
        else:
            daily_amount = 0
        
        #変更前後比較？
        is_update = False
        differ_amount = 0
        differ_paid_amount = 0
        daily_compensation_before = None
        
        #
        deduction_amount_1 = 0
        deduction_amount_2 = 0
        deduction_amount_3 = 0
        
        carryover_amount_1 = 0
        carryover_amount_2 = 0
        carryover_amount_3 = 0
        #
        
        #if id is not None:
        if id is not None and id != "None":
            
            daily_compensation_before = Daily_Compensation.objects.filter(pk=id).first()
            if daily_compensation_before is not None:
                
                if daily_amount != daily_compensation_before.amount:
                    is_update = True
                    
                    differ_amount = daily_amount - daily_compensation_before.amount
                    
                    deduction_amount_1 = daily_compensation_before.deduction_amount_1
                    deduction_amount_2 = daily_compensation_before.deduction_amount_2
                    deduction_amount_3 = daily_compensation_before.deduction_amount_3
                    
                    carryover_amount_1 = daily_compensation_before.carryover_amount_1
                    carryover_amount_2 = daily_compensation_before.carryover_amount_2
                    carryover_amount_3 = daily_compensation_before.carryover_amount_3
                    
                #daily_amount = differ_amount
        #import pdb; pdb.set_trace()
        ##
        
    #３ヶ月前まで見る
        #import pdb; pdb.set_trace()
        paid_on = datetime.strptime(paid_on_str, '%Y-%m-%d')
        
        paid_on_month = paid_on.month
        paid_on_day = paid_on.day
        
        #import pdb; pdb.set_trace()
        start_date = datetime.now()
        
        next_date = datetime.now()  #次月
        
        if paid_on_day > 20:
            
            start_date = paid_on + relativedelta(months=-2)
            end_date = paid_on
            
            next_date = paid_on + relativedelta(months=+1)
        else:
            #通常(20日以前)
            #開始月=3ヶ月前、終了月1ヶ月前とする
            start_date = paid_on + relativedelta(months=-3)
            end_date = paid_on + relativedelta(months=-1)
            
            next_date = paid_on
            
        start_date = start_date.replace(day=1)
        end_date = end_date.replace(day=1)
        
        next_date = next_date.replace(day=1)
        
        #３ヶ月前までループしデータ見る
        #payment_reserves = Payment_Reserve.objects.all().filter(billing_year_month=assigned_date)
        compensations = Compensation.objects.filter(payment_year_month__gte=start_date, \
                                                    payment_year_month__lte=end_date).order_by('payment_year_month')
                
        
        paid_count = 0
        
        paid_amount = []
        carryover_amount = []
        paid_on = []
        
        tmp_amount = 0
        cnt = 0
        total_cnt = 0
        completed_cnt = 0
        inherit_amount = 0
        
        #for payment_reserve in payment_reserves:
        for compensation in compensations: 
            if compensation.is_completed is not 1:
                cnt += 1
                total_cnt += 1
                
                #引き継ぎ金額
                if cnt == 1:
                    inherit_amount = daily_amount
                
                #更新の場合の設定
                if is_update:
                    damount = 0
                    camount = 0
                    if total_cnt == 1:
                        damount = deduction_amount_1
                        camount = carryover_amount_1
                    elif total_cnt == 2:
                        damount = deduction_amount_2
                        camount = carryover_amount_2
                    else:
                        damount = deduction_amount_3
                        camount = carryover_amount_3
                #
                
                
                if inherit_amount > 0:
                
                    if compensation.paid_amount is None or compensation.paid_amount == 0:
                    
                        if compensation.amount >= inherit_amount:
                            #元の報酬からそのまま引く
                            #tmp_amount = compensation.amount - inherit_amount
                            tmp_amount = inherit_amount
                            inherit_amount = 0
                        else:
                            #日次金額が大きい場合
                            tmp_amount = compensation.amount
                            inherit_amount = inherit_amount - compensation.amount
                        
                        #多い場合、翌月へ持ち越し？
                        #import pdb; pdb.set_trace()
                        #
                    
                        #if cnt == 1:  #test
                        paid_amount.append(tmp_amount)
                        carryover_amount.append(inherit_amount)
                        paid_on.append(compensation.payment_year_month)
                
                    else:
                        #支払済の有る場合
                        
                        if is_update == False:
                            
                            rest_pay_amount = compensation.amount - compensation.paid_amount 
                    
                            #if rest_amount >= daily_amount:
                            if rest_pay_amount >= inherit_amount:
                                #支払残り金額が日次金額以上
                    
                                #支払分を算出
                                #tmp_amount = rest_pay_amount - inherit_amount
                                tmp_amount = inherit_amount
                                inherit_amount = 0
                            else:
                                #残り金額が日次金額より下
                                #tmp_tmp_amount = inherit_amount - rest_pay_amount
                        
                                #rest_paid_amount = tmp_tmp_amount + rest_pay_amount
                                rest_paid_amount = inherit_amount
                        
                                tmp_amount = rest_pay_amount
                                inherit_amount -= rest_pay_amount
                                
                            
                            paid_amount.append(tmp_amount)
                            carryover_amount.append(inherit_amount)
                            paid_on.append(compensation.payment_year_month)
                        else:
                            #更新の場合
                            #修正中 250423....
                            
                            rest_pay_amount = compensation.amount - inherit_amount
                            coamount = 0
                            
                            #if rest_pay_amount >= inherit_amount:
                            if compensation.amount >= inherit_amount:
                                #未検証
                                tmp_amount = inherit_amount
                                #coamount = 0
                            else:
                                tmp_amount = compensation.amount
                                #inherit_amount -= rest_pay_amount
                                coamount -= rest_pay_amount
                            paid_amount.append(tmp_amount)
                            #carryover_amount.append(inherit_amount)
                            carryover_amount.append(coamount)
                            paid_on.append(compensation.payment_year_month)
                            
                    #tmp_amout = compensation.paid_amount + daily_amount
            else:
                #支払済でも、繰り越すケースも有
                
                #import pdb; pdb.set_trace()
                
                completed_cnt += 1
                
                if completed_cnt == len(compensations):
                    
                    total_cnt += 1
                    
                    if is_update == False:
                        #import pdb; pdb.set_trace()
                        
                        paid_amount.append(0)
                        inherit_amount = daily_amount
                        #paid_amount.append(inherit_amount)
                    
                        carryover_amount.append(inherit_amount)
                        #restore 250428
                        #carryover_amount.append(0)
                        
                        paid_on.append(next_date)
                        
                        #250425
                        #データ有無のチェックも必要?
                        
                    else:
                    #訂正の場合
                        damount = 0
                        camount = 0
                        
                        if total_cnt == 1:
                            damount = deduction_amount_1
                            camount = carryover_amount_1
                        elif total_cnt == 2:
                            damount = deduction_amount_2
                            camount = carryover_amount_2
                        else:
                            damount = deduction_amount_3
                            camount = carryover_amount_3
                        
                        #import pdb; pdb.set_trace()
                        
                        if camount == 0 or camount is None:
                            if compensation.is_completed != 1:
                                damount += differ_amount
                            else:
                                camount += differ_amount
                        else:
                            camount += differ_amount
                        
                        paid_amount.append(damount)
                        carryover_amount.append(camount)
                        
                        #paid_on.append(next_date)  #???
                        paid_on.append(compensation.payment_year_month)
                
                
        #import pdb; pdb.set_trace()
        #json用のリストへセット
        amount_length = len(paid_amount)
        json_amount = []
        json_carryover_amount = []
        json_date = []
        
        if amount_length == 3:
            json_amount = [paid_amount[0], paid_amount[1], paid_amount[2]]
        elif amount_length == 2:
            json_amount = [paid_amount[0], paid_amount[1], 0]
        else:
            json_amount = [paid_amount[0], 0, 0]
        #
        
        #繰越金額
        #json_carryover_amount = [0, 0, 0]
        carryover_amount_length = len(carryover_amount)
           
        if carryover_amount_length == 3:
            #json_carryover_amount = [carryover_amount[0], carryover_amount[1], carryover_amount[2]]
            json_carryover_amount = [0, 0, carryover_amount[2]]
        elif carryover_amount_length == 2:
            #json_carryover_amount = [carryover_amount[0], carryover_amount[1], 0]
            json_carryover_amount = [0, carryover_amount[1], 0]
        else:
            json_carryover_amount = [carryover_amount[0], 0, 0]
        #
        
        paid_on_length = len(paid_on)
        
        if paid_on_length == 3:
            json_date = [paid_on[0], paid_on[1], paid_on[2]]
        elif paid_on_length == 2:
            json_date = [paid_on[0], paid_on[1], 0]
        else:
            json_date = [paid_on[0], 0, 0]
        
        #戻り値
        response = [json_amount[0], json_amount[1], json_amount[2], \
                    json_carryover_amount[0], json_carryover_amount[1], json_carryover_amount[2], \
                    json_date[0], json_date[1], json_date[2]]
                    #json_date[0], json_date[1], json_date[2]]
        
        
        json_data = json.dumps({"HTTPRESPONSE":response}, default=str)   # JSON形式に直す
        #json_data = json.dumps(response, dafault=str)   # JSON形式に直す
        return HttpResponse(json_data, content_type="application/json")
        
    #return render(request, 'account/daily_compensation_edit.html', \
    #       dict(form=form, daily_compensation_id=daily_compensation_id))
    else:
        return None
    #test

def ajax_set_carryover(request):
    
    #import pdb; pdb.set_trace()
    
    if request.method == 'GET':
        
        paid_on_str = request.GET['paid_on']
        paid_on_str = paid_on_str + "-1"  #１日を加える
        paid_on = datetime.strptime(paid_on_str, '%Y-%m-%d')
        
        
        #先月の繰越金があるか確認
        
        last_month = paid_on + relativedelta(months=-1)
        #last_compensation = Compensation.objects.filter(payment_year_month=last_month)
        try:
            last_compensation = Compensation.objects.get(payment_year_month=last_month)
        except Compensation.DoesNotExist:
            last_compensation = None
        
        carryover_amount = 0
        
        #import pdb; pdb.set_trace()
        
        if last_compensation is not None:
            if last_compensation.carryover_amount > 0:
                carryover_amount = last_compensation.carryover_amount
                #
                
        response = [carryover_amount]
        json_data = json.dumps({"HTTPRESPONSE":response}, default=str)  #JSON形式に直す
        return HttpResponse(json_data, content_type="appliation_json")       
    else:
        return None
