#レポート関連のビュー
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
#from django.http import HttpResponse
#
from account.models import Account_Title
from account.models import Cash_Book
from account.models import Staff
from account.models import PurchaseOrderData
#
from django.http import Http404, HttpResponse, QueryDict
#from django.template import RequestContext

from django.core.cache import cache

#レポート関連
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape, portrait
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.pdfmetrics import registerFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
from django.conf import settings
from datetime import datetime
#fontname = "IPA Gothic"

PAYMENT_METHOD_TRANSFER = 1       #支払方法（振込）の場合
PAYMENT_METHOD_DIRECT_DEBIT = 2   #支払方法（口座振替）の場合
PAYMENT_METHOD_CACHE = 4          #支払方法（現金）の場合


#レポート関連定数
#HEADER_X = 75
HEADER_X_TITLE = 92
HEADER_X = 26
    
#DETAIL_START_X = 20
#
HEADER_Y = 20
START_Y = 34
#SEP_Y = 7
SEP_Y = 6
    
#縦線用定数
POS_LEFT_SIDE = 18    #左端
POS_RIGHT_SIDE = 203  #右端
    
STR_ADJUST = 2    #文字位置調整分
    
POS_DATE = 18
POS_ACCOUNT_TITLE = 35
POS_DESCRIPTION = 63
POS_DESCRIPTION_2 = 108
#POS_STAFF = 144
POS_STAFF = 141
POS_INCOMES = 153
POS_EXPENCES = 178
    
  
#横線用定数
POS_HEADER_HEIGHT = 6   #ヘッダの線高さ
#POS_DETAIL_HEIGHT = 7  #明細部の線の高さ
POS_DETAIL_HEIGHT = 6  #明細部の線の高さ(文字基準)
POS_AJDUST_HEIGHT = 4  #明細部の線の高さ（調整値）
    
#文字位置定数(加算値)
POS_TOTAL_CHAR = 66           #小計・合計位置
POS_ROUGH_ESTIMATE_CHAR = 17  #概算
#
FONT_NORMAL_SIZE = 10 

#集計表(抽出用)
def list_2(request):
    
    # 適切な PDF 用応答ヘッダを持った HttpResponse オブジェクトを
    # 作成します。
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename=cash_book_list_2.pdf'
    
    global font_name
    font_name = 'HeiseiKakuGo-W5'
    pdfmetrics.registerFont(UnicodeCIDFont(font_name))
        
    
    # レスポンスオブジェクトを出力「ファイル」にして、 PDF オブジェクト
    # を作成します。
    p = canvas.Canvas(response, pagesize=portrait(A4), bottomup=False)
    p.setFont(font_name, 12)
    
    # PDF に描画します。 PDF 生成のキモの部分です。
    y = START_Y;
    
    
    #検索フォームの値を取得
    global search_settlement_date_from 
    global search_settlement_date_to 
        
    global search_receipt_date_from 
    global search_receipt_date_to 
    
    global search_staff 
    global search_account_title 
    
    
    search_settlement_date_from = cache.get('search_settlement_date_from')
    search_settlement_date_to = cache.get('search_settlement_date_to')
        
    search_receipt_date_from = cache.get('search_receipt_date_from')
    search_receipt_date_to = cache.get('search_receipt_date_to')
    
    search_staff = cache.get('search_staff')
    search_account_title = cache.get('search_account_title')
    #
    
    #デバッグ
    #import pdb; pdb.set_trace()
        
    
    #タイトル
    #p.setFont(font_name, 12)
    global tmp_date_from
    global tmp_date_to
    
    tmp_date_from = search_settlement_date_from
    tmp_date_to = search_settlement_date_to
    
    #請求日があれば優先する
    if search_receipt_date_from:
        #import pdb; pdb.set_trace()
    
        tmp_date_from = search_receipt_date_from
        tmp_date_to = search_receipt_date_to
    
    if tmp_date_from is not None:
        #◯◯◯◯年◯◯月〆の文字を作る
        
        #import pdb; pdb.set_trace()
        
        #タイトル部をセット
        x = 0
        y = 0
        global page_count 
        page_count = 1
        
        p,x,y = set_title(p,x,y)  #タイトル・ヘッダ部をセット
    #
    
    #データ抽出・並び替え
    results = filter()
    
    #小計・合計用
    subtotal_incomes = 0
    total_incomes = 0
    subtotal_expences = 0
    total_expences = 0
    
    #subtotal_rough_estimate = 0
    #total_rough_estimate = 0
    
    i = 0
    cnt = 0 
    
    p_month = 0
    month_total_flag = False
    last_month_total_flag = False
    #y += SEP_Y  #明細位置調整
    
    for cash_book in results:
        
        #小計
        i += 1 #カウンター
        cnt += 1
        
        if cnt > 40:
            p.showPage()  #改ページ
            page_count += 1
            p,x,y = set_title(p,x,y)
            cnt = 0       #カウンターをリセット
        
        y += SEP_Y
        
        #領収日
        d = None
        if cash_book.receipt_date is not None:
            p_date = cash_book.receipt_date
        if search_settlement_date_from:
            #請求日があれば優先
            p_date = cash_book.settlement_date
        
        d = p_date.strftime('%m/%d')
        
        if d is not None:
            #月またがりの場合に小計を出す
            
            if p_month != p_date.month:
                month_total_flag = False
                last_month_total_flag = True
            
            p_month = p_date.month
            p_day = p_date.day
            
            if p_day > 20 and month_total_flag == False:
                #小計・合計用
                #y += SEP_Y
                
                #２１日目が最初に来る場合があるので、その場合は出力しないようにする
                if i != 1:
                
                    x = POS_STAFF + 9
                    p.drawRightString(x*mm, y*mm, str(p_month) + '月計')
    
                    #収入金額合計
                    x = POS_INCOMES + 21 + STR_ADJUST
                    if subtotal_incomes > 0:
                        str_incomes = "￥" + str("{0:,d}".format(subtotal_incomes))  #桁区切り
                        p.drawRightString(x*mm, y*mm, str_incomes)
                
                        subtotal_incomes = 0
                    #支払金額合計
                    x = POS_EXPENCES + 21 + STR_ADJUST
                    if subtotal_expences > 0:
                        str_expences = "￥" + str("{0:,d}".format(subtotal_expences))  #桁区切り
                        p.drawRightString(x*mm, y*mm, str_expences)
                    
                        subtotal_expences = 0
                    #罫線をセット
                    p.line(POS_LEFT_SIDE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_LEFT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) 
                    p.line(POS_INCOMES*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_INCOMES*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) 
                    p.line(POS_EXPENCES*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_EXPENCES*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) 
                    p.line(POS_RIGHT_SIDE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_RIGHT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm)  #右端の縦線
                    p.line(POS_LEFT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm, POS_RIGHT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #横線 
                    
                    y += SEP_Y
                    #
                month_total_flag = True
                last_month_total_flag = True
                
            #import pdb; pdb.set_trace()
            
            
            ###
            
            #日付
            receipt_date = str(d)
            x = POS_DATE + STR_ADJUST
            p.drawString(x*mm, y*mm, receipt_date)
        
        #科目
        x = POS_ACCOUNT_TITLE + STR_ADJUST
        
        if cash_book.account_title is not None:
            name = str(cash_book.account_title)
            p.drawString(x*mm, y*mm, name)
        #摘要
        x = POS_DESCRIPTION + STR_ADJUST
        description = str(cash_book.description_partner)
        p.drawString(x*mm, y*mm, description)
        
        x = POS_DESCRIPTION_2 + STR_ADJUST
        description = str(cash_book.description_content)
        if len(description) > 8:
            p.setFont(font_name, 8)  #フォントを下げる
        
        p.drawString(x*mm, y*mm, description)
        
        p.setFont(font_name, FONT_NORMAL_SIZE)  #元のサイズに戻す
        
        #担当
        x = POS_STAFF + STR_ADJUST
        try:
            staff = Staff.objects.get(pk=cash_book.staff_id)
        except Staff.DoesNotExist:
            staff = None
        if staff is not None:
            name = str(staff.staff_name)[0:2]  #名字だけとする（３文字の名字はないものとする・。）
            
            #薄田さんは社長に変換
            if name == "薄田":
                name = "社長"
            
            p.drawString(x*mm, y*mm, name)
        
        #収入金額
        x = POS_INCOMES + 21 + STR_ADJUST
        incomes = cash_book.incomes or 0
        if incomes > 0:
            str_incomes = "￥" + str("{0:,d}".format(incomes))  #桁区切り
            p.drawRightString(x*mm, y*mm, str_incomes)
        else:
        #注文番号が入力されていた場合は出力する
            try:
                purchase_order = PurchaseOrderData.objects.get(pk=cash_book.purchase_order_code_id)
            except PurchaseOrderData.DoesNotExist:
                purchase_order = None
            if purchase_order is not None:
                str_code = "仕入(" + purchase_order.purchase_order_code + ")"
                p.drawRightString(x*mm, y*mm, str_code)
                
        #支払金額
        x = POS_EXPENCES + 21 + STR_ADJUST
        expences = cash_book.expences or 0
        if expences > 0:
            str_expences = "￥" + str("{0:,d}".format(expences))  #桁区切り
            p.drawRightString(x*mm, y*mm, str_expences)
        
        #小計・合計用にカウント
        #収入
        subtotal_incomes += incomes
        total_incomes += incomes
        #支払
        subtotal_expences += expences
        total_expences += expences
        
        #罫線をセット
        p.line(POS_LEFT_SIDE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_LEFT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) 
        p.line(POS_ACCOUNT_TITLE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_ACCOUNT_TITLE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #科目箇所の右端
        p.line(POS_DESCRIPTION*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_DESCRIPTION*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm)
        p.line(POS_STAFF*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_STAFF*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm)
        p.line(POS_INCOMES*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_INCOMES*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) 
        p.line(POS_EXPENCES*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_EXPENCES*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) 
        
        p.line(POS_RIGHT_SIDE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_RIGHT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm)  #右端の縦線
        p.line(POS_LEFT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm, POS_RIGHT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #横線 
        #
        
    
    #小計用
    if last_month_total_flag == True:
        y += SEP_Y
        
        if p_day > 20:
            p_month += 1
        
        x = POS_STAFF + 9
        p.drawRightString(x*mm, y*mm, str(p_month) + '月計')
    
        #収入金額合計
        x = POS_INCOMES + 21 + STR_ADJUST
        if subtotal_incomes > 0:
            str_incomes = "￥" + str("{0:,d}".format(subtotal_incomes))  #桁区切り
            p.drawRightString(x*mm, y*mm, str_incomes)
            subtotal_incomes = 0
        #支払金額合計
        x = POS_EXPENCES + 21 + STR_ADJUST
        if subtotal_expences > 0:
            str_expences = "￥" + str("{0:,d}".format(subtotal_expences))  #桁区切り
            p.drawRightString(x*mm, y*mm, str_expences)
            subtotal_expences = 0
        #罫線をセット
        p.line(POS_LEFT_SIDE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_LEFT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) 
        p.line(POS_INCOMES*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_INCOMES*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) 
        p.line(POS_EXPENCES*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_EXPENCES*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) 
        p.line(POS_RIGHT_SIDE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_RIGHT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm)  #右端の縦線
        p.line(POS_LEFT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm, POS_RIGHT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #横線 
        #
        month_total_flag = True
        
    ###
    
    
    #合計用
    y += SEP_Y
    
    x = POS_STAFF + 9
    p.drawRightString(x*mm, y*mm, '合計')
    
    #収入金額合計
    x = POS_INCOMES + 21 + STR_ADJUST
    if total_incomes > 0:
        str_incomes = "￥" + str("{0:,d}".format(total_incomes))  #桁区切り
        p.drawRightString(x*mm, y*mm, str_incomes)
    #支払金額合計
    x = POS_EXPENCES + 21 + STR_ADJUST
    if total_expences > 0:
        str_expences = "￥" + str("{0:,d}".format(total_expences))  #桁区切り
        p.drawRightString(x*mm, y*mm, str_expences)
    #罫線をセット
    p.line(POS_LEFT_SIDE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_LEFT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) 
    #p.line(POS_ACCOUNT_TITLE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_ACCOUNT_TITLE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #科目箇所の縦線
    #p.line(POS_DESCRIPTION*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_DESCRIPTION*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm)
    #p.line(POS_STAFF*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_STAFF*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm)
    p.line(POS_INCOMES*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_INCOMES*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) 
    p.line(POS_EXPENCES*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_EXPENCES*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) 
    p.line(POS_RIGHT_SIDE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_RIGHT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm)  #右端の縦線
    p.line(POS_LEFT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm, POS_RIGHT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #横線 
    #
    
    
    # PDF オブジェクトをきちんと閉じて終わり。
    p.showPage()
    p.save()
    return response

def set_title(p,x,y):

    #str_title = '経費集計表' + "　　" + tmp_date_from[0:4] + "/" + tmp_date_from[5:7] + "/" + tmp_date_from[8:10] \
    #            + "〜" + tmp_date_to[0:4] + "/" + tmp_date_to[5:7] + "/" + tmp_date_to[8:10]
    str_title = '経費集計表'
    p.setFont(font_name, 14)
        
    p.drawString((HEADER_X_TITLE)*mm, HEADER_Y*mm, str_title)
    
    p.setFont(font_name, FONT_NORMAL_SIZE) #フォントを元にもどす
    str_page = str(page_count) + "ページ"
    p.drawString(100*mm, 290*mm, str_page)
    
    
    #サブタイトル
    y = HEADER_Y + 8
        
    str_title =  tmp_date_from[0:4] + "/" + tmp_date_from[5:7] + "/" + tmp_date_from[8:10] \
                + "〜" + tmp_date_to[0:4] + "/" + tmp_date_to[5:7] + "/" + tmp_date_to[8:10]
    p.drawString(HEADER_X*mm, y*mm, str_title)
        
    str_title2 = ""
    if search_staff:
            
        #担当名取得
        try:
            staff = Staff.objects.get(pk=search_staff)
        except Staff.DoesNotExist:
            staff = None
            
        if staff is not None:
            str_title2 += staff.staff_name
            str_title2 += "　　"
    if search_account_title:
            
        #科目名取得
        try:
            account_title = Account_Title.objects.get(pk=search_account_title)
        except Account_Title.DoesNotExist:
            account_title = None
            
        if account_title is not None:
            str_title2 += account_title.name
        
    x = 135
    p.drawString(x*mm, y*mm, str_title2)
    #
    
    
    #現在日付(今の所不要)
    #d = datetime.now().strftime('%Y/%m/%d')
    #today = str(d) + "現在"
    #p.drawString((POS_RIGHT_SIDE-22)*mm, (HEADER_Y +3)*mm, today)
    #
    
#   #ヘッダー
    p.setFont(font_name, 10)  #元のサイズに戻す
    #y += 10
    y += 9
    
    x = POS_DATE + STR_ADJUST
    p.drawString(x*mm, y*mm, '日付')
    
    x = POS_ACCOUNT_TITLE + STR_ADJUST
    p.drawString(x*mm, y*mm, '科目')
    
    x = POS_DESCRIPTION + STR_ADJUST
    p.drawString(x*mm, y*mm, '摘要')
    
    x = POS_STAFF + STR_ADJUST
    p.drawString(x*mm, y*mm, '担当')
    
    x = POS_INCOMES + STR_ADJUST + 3
    p.drawString(x*mm, y*mm, '収入金額')
    
    x = POS_EXPENCES + STR_ADJUST + 3
    p.drawString(x*mm, y*mm, '支払金額')
    
#    #Y座標インクリメント
#    y += SEP_Y+3
    
    #ヘッダ部罫線
    p.rect(POS_LEFT_SIDE*mm, (START_Y-1)*mm, (POS_RIGHT_SIDE-POS_LEFT_SIDE)*mm, POS_HEADER_HEIGHT*mm, fill=0) #枠
    p.line(POS_ACCOUNT_TITLE*mm, (START_Y-1)*mm, POS_ACCOUNT_TITLE*mm, ((START_Y-1) + POS_HEADER_HEIGHT)*mm) 
    p.line(POS_DESCRIPTION*mm, (START_Y-1)*mm, POS_DESCRIPTION*mm, ((START_Y-1) + POS_HEADER_HEIGHT)*mm) 
    p.line(POS_STAFF*mm, (START_Y-1)*mm, POS_STAFF*mm, ((START_Y-1) + POS_HEADER_HEIGHT)*mm) 
    p.line(POS_INCOMES*mm, (START_Y-1)*mm, POS_INCOMES*mm, ((START_Y-1) + POS_HEADER_HEIGHT)*mm) 
    p.line(POS_EXPENCES*mm, (START_Y-1)*mm, POS_EXPENCES*mm, ((START_Y-1) + POS_HEADER_HEIGHT)*mm) 
    
    return p, x, y

def filter():
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

    #import pdb; pdb.set_trace()

    return results
