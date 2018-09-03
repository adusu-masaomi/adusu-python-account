#レポート関連のビュー
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
#from django.http import HttpResponse
#
from account.models import Partner
from account.models import Account_Title
from account.models import Bank
from account.models import Bank_Branch
from account.models import Payment
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

MAX_LINE_LIST_1 = 48    #支払集計表の１ページ最大行数

#支払集計表
def payment_list_1(request):
    
    #レポート関連定数(主に、サブルーチン用にグローバル化)
    global HEADER_X; HEADER_X = 75
    global DETAIL_START_X; DETAIL_START_X = 20
    #
    global HEADER_Y; HEADER_Y = 20
    global START_Y; START_Y = 30
    
    global SEP_Y; SEP_Y = 5 
    
    #縦線用定数
    global POS_LEFT_SIDE; POS_LEFT_SIDE = 16    #左端
    global POS_RIGHT_SIDE; POS_RIGHT_SIDE = 200  #右端
    global POS_CHECK_PAYED; POS_CHECK_PAYED = 24
    global POS_NAME; POS_NAME = 56
    global POS_ACCOUNT_TITLE; POS_ACCOUNT_TITLE = 70
    global POS_AMOUNT; POS_AMOUNT = 87
    global POS_ROUGH_ESTIMATE; POS_ROUGH_ESTIMATE = 104
    global POS_PAYMENT_METHOD; POS_PAYMENT_METHOD = 117
    global POS_TRANSFER; POS_TRANSFER = 176
    global POS_PAY_DUE_DATE; POS_PAY_DUE_DATE = 188
    #横線用定数
    global POS_HEADER_HEIGHT; POS_HEADER_HEIGHT = 8   #ヘッダの線高さ
    POS_DETAIL_HEIGHT = 5  #明細部の線の高さ(文字基準)
    POS_AJDUST_HEIGHT = 4  #明細部の線の高さ（調整値）
    
    #文字位置定数(加算値)
    POS_TOTAL_CHAR = 66           #小計・合計位置
    POS_ROUGH_ESTIMATE_CHAR = 17  #概算
    
    # 適切な PDF 用応答ヘッダを持った HttpResponse オブジェクトを
    # 作成します。
    response = HttpResponse(content_type='application/pdf')
    #response['Content-Disposition'] = 'attachment; filename=payment_list_1.pdf'
    response['Content-Disposition'] = 'inline; filename=payment_list_1.pdf'
    
    global font_name
    font_name = 'HeiseiKakuGo-W5'
    #font_name_bold = 'HeiseiKakuGo-W5-Bold'
    pdfmetrics.registerFont(UnicodeCIDFont(font_name))
        
    
    # レスポンスオブジェクトを出力「ファイル」にして、 PDF オブジェクト
    # を作成します。
    p = canvas.Canvas(response, pagesize=portrait(A4), bottomup=False)
    p.setFont(font_name, 12)
    
    # PDF に描画します。 PDF 生成のキモの部分です。
    
    #条件でクエリーセット抽出
    payments = filter()
    
    
    #タイトル部出力
    x = 0
    y = 0
    
    p,x,y = set_title_normal(p,x,y)
    
    
    #支払モデル取得（月指定--複数月は今の所考慮していない。）
    #if cache.get('search_query_month_from') != None:
    #    search_query_month = cache.get('search_query_month_from')
    #    #◯月１日で検索するようにする
    #    search_query_month += "-01"
    #    payments = Payment.objects.all().filter(billing_year_month=search_query_month).order_by('payment_method_id', 'trade_division_id', 'order', 'id')
    #else:
    #    payments = Payment.objects.all()
    
    #条件でクエリーセット抽出
    #payments = filter()
    
    #小計・合計用
    payment_method_id_saved = None
    subtotal_amount = 0
    total_amount = 0
    subtotal_rough_estimate = 0
    total_rough_estimate = 0
    i = 0
    cnt = 0  #ページ内の行カウント用
    
    for payment in payments:
        
        #小計
        i += 1 #カウンター
        cnt += 1
        
        #改ページ
        if cnt > MAX_LINE_LIST_1:
            p.showPage()  
            #page_count += 1
            p,x,y = set_title_normal(p,x,y)
            cnt = 0       #カウンターをリセット
        
        if payment_method_id_saved != None and payment_method_id_saved != payment.payment_method_id:
            
            #p.setFont(font_name, 9)
            x = DETAIL_START_X + 42
            p.drawString(x*mm, y*mm, "計")
            
            x = DETAIL_START_X + POS_TOTAL_CHAR
            
            p.setFillColorRGB(0,0,188) #色を指定(青系)
            m = "￥" + str("{0:,d}".format(subtotal_amount))
            p.drawRightString(x*mm, y*mm, m)
            subtotal_amount = 0
            
            #概算金額小計
            #if payment.payment_method_id == (PAYMENT_METHOD_DIRECT_DEBIT + 1) :
            #(口座の場合のみ--現金はここではないものとする（最終行で記述）)
            #(ひとまず全て出すことにした)
            
            x += POS_ROUGH_ESTIMATE_CHAR
            #p.setFillColorRGB(0.3882,0.48627,0.20784) #色を指定(緑系)
            #p.setFillColorRGB(0.8980,0,0.5254) #色を指定(ピンク系)
            p.setFillColorRGB(0.15686,0.639215,0.58039) #色を指定(ビリジャン)
            m = "￥" + str("{0:,d}".format(subtotal_rough_estimate))
            p.drawRightString(x*mm, y*mm, m)
            subtotal_rough_estimate = 0
            
            #else:
            #    #印刷しないがカウンターのみリセット
            #    subtotal_rough_estimate = 0
            
            #罫線をセット
            p.line(POS_LEFT_SIDE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_LEFT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) 
            p.line(POS_CHECK_PAYED*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_CHECK_PAYED*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #未の箇所の右端
            p.line(POS_NAME*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_NAME*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #支払先の右端
            p.line(POS_ACCOUNT_TITLE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_ACCOUNT_TITLE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #項目の右端
            p.line(POS_AMOUNT*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_AMOUNT*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #金額の右端
            p.line(POS_ROUGH_ESTIMATE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_ROUGH_ESTIMATE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #概算の右端
            p.line(POS_PAYMENT_METHOD*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_PAYMENT_METHOD*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #支払方法の右端
            p.line(POS_TRANSFER*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_TRANSFER*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #振込先の右端
            p.line(POS_PAY_DUE_DATE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_PAY_DUE_DATE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #支払予定日の右端
            p.line(POS_RIGHT_SIDE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_RIGHT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) 
            p.line(POS_LEFT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm, POS_RIGHT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #横線
            #
            #Yインクリメント
            y += SEP_Y
            
        p.setFillColorRGB(0,0,0)
        #p.setFont(font_name, 7)
        
        #小計・合計カウント用
        #金額
        if payment.billing_amount is not None:
            subtotal_amount += payment.billing_amount
            total_amount += payment.billing_amount
        #概算(未払のみカウント)
        if payment.payment_date is None:
            if payment.rough_estimate is not None:
                subtotal_rough_estimate += payment.rough_estimate
                total_rough_estimate += payment.rough_estimate
            else:
                subtotal_rough_estimate += 0
                total_rough_estimate += 0
        #
        #保存用
        payment_method_id_saved = payment.payment_method_id
        #
        
        
        #まず塗りつぶしの枠を入れる
        if payment.trade_division_id == 0:
            p.setFillColorRGB(0.737254,0.784313,0.858823)   #水色
        elif payment.trade_division_id == 1:
            p.setFillColorRGB(0.72549,0.84705,0.64705)   #抹茶色
        p.rect(POS_LEFT_SIDE*mm, (y-POS_AJDUST_HEIGHT)*mm, (POS_RIGHT_SIDE-POS_LEFT_SIDE)*mm, POS_DETAIL_HEIGHT*mm, fill=True) #枠
        p.setFillColorRGB(0,0,0)  #色を黒に戻す
        #
        
        #複数月範囲の場合、または未払リストの場合は、見分けられるように月も出力
        if multi_month == True or search_query_paid:
            #import pdb; pdb.set_trace()
            
            if payment.billing_year_month is not None:
                x = DETAIL_START_X
                str_month = str(payment.billing_year_month.month) + "月"
                p.drawString((x-9)*mm, y*mm, str_month)
        
        x = DETAIL_START_X + 6
        
        #取引先名
        partner_name = str(payment.partner)
        
        #pn = partner_name.decode('utf-8')
        pn = partner_name.encode().decode('utf-8')
        
        if len(pn) <= 13:
           p.setFont(font_name, 7)
        else:
            p.setFont(font_name, 5.5)
        
        #partner_name = partner_name.encode("utf-8")
        if partner_name.find('振込手数料') == -1 :
            p.drawString(x*mm, y*mm, partner_name)
        else:
        #振込手数料の文字があれば右に寄せる
            p.drawRightString((x+20)*mm, y*mm, partner_name)
        
        p.setFont(font_name, 7)
        
        #項目(勘定科目等)
        x += 37
        if payment.account_title is not None:
          account_title = str(payment.account_title)
        else:
          account_title = settings.EMPTY_MARK
        p.drawCentredString(x*mm, y*mm, account_title)
        
        #支払金額
        #x += 25
        x += (POS_TOTAL_CHAR -43)
        
        if payment.billing_amount is not None:
            billing_amount = "￥" + str("{0:,d}".format(payment.billing_amount))  #桁区切り
            #billing_amount = "{0:>11}".format(billing_amount)  #右寄せ→できない
            p.drawRightString(x*mm, y*mm, billing_amount)
        
        #概算金額
        x += POS_ROUGH_ESTIMATE_CHAR
        if payment.rough_estimate is not None:
            p.setFillColorRGB(0.5490,0.5490,0.5490) #色を指定(グレー)
        
            rough_estimate = "￥" + str("{0:,d}".format(payment.rough_estimate))  #桁区切り
            p.drawRightString(x*mm, y*mm, rough_estimate)
        p.setFillColorRGB(0,0,0) #色を黒に戻す
        #支払方法
        x += 7
        
        #色に関して--RGBの各本来数値÷255となっている
        
        if payment.payment_method_id == PAYMENT_METHOD_TRANSFER:
        #振込
            p.setFillColorRGB(0,0,1) #色を指定(青系)
            
            #p.setFillColorRGB(0.33725,0.38823,0.56078) #色を指定(青系)
            #p.setFillColorRGB(0.1998,0.0196, 1) #色を指定(青系-露草色)
        elif payment.payment_method_id == PAYMENT_METHOD_DIRECT_DEBIT:
        #口座振替
            p.setFillColorRGB(0.71764,0.2549,0.05490) #色を指定(茶系-赤錆色)
            
            #p.setFillColorRGB(0.3098,0.2235,0.1843) #色を指定(茶系)
            #p.setFillColorRGB(0.6196,0.3098,0.17647) #色を指定(茶系-栗梅)
            #p.setFillColorRGB(1,0.3843,0.19607) #色を指定(茶系-黄丹)
        elif payment.payment_method_id == PAYMENT_METHOD_CACHE:
        #現金
            p.setFillColorRGB(0.1843,0.3098,0.2941)   #色を指定(緑系)
        
        payment_method = str(payment._meta.get_field('payment_method_id').choices[payment.payment_method_id][1])
        p.drawCentredString(x*mm, y*mm, payment_method)
        
        p.setFillColorRGB(0,0,0) #色を黒に戻す
        
        #口座番号等（振込の場合）
        x += 10
        #if payment.payment_method_id == 1:
        if payment.payment_method_id == settings.ID_PAYMENT_METHOD_TRANSFER:
            partner = Partner.objects.get(pk=payment.partner_id)
            if partner is not  None:
                try:
                    bank = Bank.objects.get(pk=partner.bank_id)
                except Bank.DoesNotExist:
                    bank = None
                if bank is not None:
                    bank_name = str(bank.name)
                    
                    if len(bank_name) > 6:
                        #文字数が８文字以上ならカットする
                        if len(bank_name) > 8:
                            bank_name = bank_name[0:8]
                    
                        p.setFont(font_name, 5)  #フォントを下げる
                                
                    #銀行
                    p.drawString(x*mm, y*mm, bank_name)
                    
                    #フォントを戻す
                    p.setFont(font_name, 7)
                    
                    if partner.bank_branch_id is not None:
                        bank_branch = Bank_Branch.objects.get(pk=partner.bank_branch_id)
                        #支店名
                        x += 15
                        if bank_branch is not None:
                            bank_branch_name = str(bank_branch.name)
                            p.drawString(x*mm, y*mm, bank_branch_name)
                            x += 22
                            #口座種別
                            account_type = str(partner._meta.get_field('account_type').choices[partner.account_type][1])
                            p.drawString(x*mm, y*mm, account_type)
                            #口座番号
                            x += 6
                            account_number = str(partner.account_number)
                            p.drawString(x*mm, y*mm, account_number)
                    else:
                    #支店未入力
                        x += 43
                else:
                #取引手数料等
                    x += 43
        else:
            #振込以外は、口座情報がないのでX座標を調整する
            x += 43
        
        #支払予定日
        x += 15
        if payment.payment_due_date is not None:
            d = payment.payment_due_date.strftime('%m/%d')
            payment_due_date = str(d)
            p.drawString(x*mm, y*mm, payment_due_date)
        x += 12
        if payment.payment_date is not None:
            d = payment.payment_date.strftime('%m/%d')
            payment_date = str(d)
            p.drawString(x*mm, y*mm, payment_date)
        else:
        #未払の場合
            x = DETAIL_START_X-1.5
            p.setFillColorRGB(1,0.3686,0.098) #色を指定(オレンジ系)
            #p.drawString(x*mm, y*mm, "未")
            p.rect(POS_LEFT_SIDE*mm, (y-POS_AJDUST_HEIGHT)*mm, (POS_CHECK_PAYED-POS_LEFT_SIDE)*mm, POS_DETAIL_HEIGHT*mm, fill=True) #枠
            
            p.setFillColorRGB(0,0,0)  #黒に戻す
        
        #罫線をセット
        p.line(POS_LEFT_SIDE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_LEFT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) 
        p.line(POS_CHECK_PAYED*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_CHECK_PAYED*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #未の箇所の右端
        p.line(POS_NAME*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_NAME*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #支払先の右端
        p.line(POS_ACCOUNT_TITLE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_ACCOUNT_TITLE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #項目の右端
        p.line(POS_AMOUNT*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_AMOUNT*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #金額の右端
        p.line(POS_ROUGH_ESTIMATE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_ROUGH_ESTIMATE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #概算の右端
        p.line(POS_PAYMENT_METHOD*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_PAYMENT_METHOD*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #支払方法の右端
        p.line(POS_TRANSFER*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_TRANSFER*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #振込先の右端
        p.line(POS_PAY_DUE_DATE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_PAY_DUE_DATE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #支払予定日の右端
        p.line(POS_RIGHT_SIDE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_RIGHT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) 
        p.line(POS_LEFT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm, POS_RIGHT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #横線
        #
        
        #Y座標インクリメント
        y += SEP_Y
        
        #小計・合計(最終行)
        if i == len(payments):
            
            #金額小計
            x = DETAIL_START_X + 42
            p.drawString(x*mm, y*mm, "計")
            
            x = DETAIL_START_X + POS_TOTAL_CHAR
            p.setFillColorRGB(0,0,188) #色を指定
            m = "￥" + str("{0:,d}".format(subtotal_amount))
            p.drawRightString(x*mm, y*mm, m)
            
            #概算金額小計
            #if (payment.payment_method_id == (PAYMENT_METHOD_DIRECT_DEBIT)) or (payment.payment_method_id == (PAYMENT_METHOD_CACHE)):
            x += POS_ROUGH_ESTIMATE_CHAR
            #p.setFillColorRGB(0.8980,0,0.5254) #色を指定(ピンク系)
            p.setFillColorRGB(0.15686,0.639215,0.58039) #色を指定(ビリジャン)
            m = "￥" + str("{0:,d}".format(subtotal_rough_estimate))
            p.drawRightString(x*mm, y*mm, m)
            #subtotal_rough_estimate = 0
            
            #subtotal_amount = 0
            #罫線をセット
            p.line(POS_LEFT_SIDE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_LEFT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) 
            p.line(POS_CHECK_PAYED*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_CHECK_PAYED*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #未の箇所の右端
            p.line(POS_NAME*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_NAME*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #支払先の右端
            p.line(POS_ACCOUNT_TITLE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_ACCOUNT_TITLE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #項目の右端
            p.line(POS_AMOUNT*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_AMOUNT*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #金額の右端
            p.line(POS_ROUGH_ESTIMATE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_ROUGH_ESTIMATE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #概算の右端
            p.line(POS_PAYMENT_METHOD*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_PAYMENT_METHOD*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #支払方法の右端
            p.line(POS_TRANSFER*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_TRANSFER*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #振込先の右端
            p.line(POS_PAY_DUE_DATE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_PAY_DUE_DATE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #支払予定日の右端
            p.line(POS_RIGHT_SIDE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_RIGHT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) 
            p.line(POS_LEFT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm, POS_RIGHT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #横線
            #
    
            #金額合計
            y += SEP_Y #Yインクリメント
            #x = DETAIL_START_X + 41
            x = DETAIL_START_X + 40.5
            p.drawString(x*mm, y*mm, "合計")
            
            x = DETAIL_START_X + POS_TOTAL_CHAR
            p.setFillColorRGB(0,0,188) #色を指定
            m = "￥" + str("{0:,d}".format(total_amount))
            p.drawRightString(x*mm, y*mm, m)
            
            #概算金額
            x += POS_ROUGH_ESTIMATE_CHAR
            #p.setFillColorRGB(0.8980,0,0.5254) #色を指定(ピンク系)
            p.setFillColorRGB(0.15686,0.639215,0.58039) #色を指定(ビリジャン)
            m = "￥" + str("{0:,d}".format(total_rough_estimate))
            p.drawRightString(x*mm, y*mm, m)
            
            #subtotal_amount = 0
            #罫線をセット
            p.line(POS_LEFT_SIDE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_LEFT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) 
            p.line(POS_CHECK_PAYED*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_CHECK_PAYED*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #未の箇所の右端
            p.line(POS_NAME*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_NAME*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #支払先の右端
            p.line(POS_ACCOUNT_TITLE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_ACCOUNT_TITLE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #項目の右端
            p.line(POS_AMOUNT*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_AMOUNT*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #金額の右端
            p.line(POS_ROUGH_ESTIMATE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_ROUGH_ESTIMATE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #概算の右端
            p.line(POS_PAYMENT_METHOD*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_PAYMENT_METHOD*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #支払方法の右端
            p.line(POS_TRANSFER*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_TRANSFER*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #振込先の右端
            p.line(POS_PAY_DUE_DATE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_PAY_DUE_DATE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #支払予定日の右端
            p.line(POS_RIGHT_SIDE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_RIGHT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) 
            p.line(POS_LEFT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm, POS_RIGHT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #横線
            #
            
            #概算集計方法の注釈
            y += SEP_Y #Yインクリメント
            #p.setFillColorRGB(0,0,0)  #黒に戻す→概算と同じ色で
            #x = DETAIL_START_X -5
            x = DETAIL_START_X + 122
            message = "※概算の各計は、未払のものだけを集計しています。"
            p.drawString(x*mm, y*mm, message)
    
    # PDF オブジェクトをきちんと閉じて終わり。
    p.showPage()
    p.save()
    return response

#支払集計表(中越提示用)
def payment_list_2(request):
    
    #レポート関連定数
    HEADER_X = 75
    #DETAIL_START_X = 20
    DETAIL_START_X = 10   #左余白
    #
    HEADER_Y = 20
    START_Y = 30
    #SEP_Y = 7
    SEP_Y = 5
    
    #縦線用定数
    #POS_LEFT_SIDE = 16    #左端
    POS_LEFT_SIDE = 6    #左端
    POS_RIGHT_SIDE = 205  #右端
    
    POS_CHECK_PAYED = POS_LEFT_SIDE + 8       #-10
    POS_NAME = POS_LEFT_SIDE + 40             #-10
    POS_ACCOUNT_TITLE = POS_LEFT_SIDE + 54    #-10
    POS_AMOUNT = POS_LEFT_SIDE + 71           #-10
    #POS_PAYMENT_METHOD = POS_LEFT_SIDE + 101  #-10
    POS_PAYMENT_METHOD = POS_LEFT_SIDE + 84  #-10
    
    POS_PAYMENT_AMOUNT = POS_LEFT_SIDE + 101  #支払金額の右端
    POS_COMMISSION = POS_LEFT_SIDE + 114      #手数料の右端
        
    POS_TRANSFER = POS_LEFT_SIDE + 143        #-10
    POS_PAY_DUE_DATE = POS_LEFT_SIDE + 155    #-10
    POS_PAY_DATE = POS_LEFT_SIDE + 167      #-10
    
    #横線用定数
    POS_HEADER_HEIGHT = 8   #ヘッダの線高さ
    
    #POS_DETAIL_HEIGHT = 7  #明細部の線の高さ
    POS_DETAIL_HEIGHT = 5  #明細部の線の高さ(文字基準)
    POS_AJDUST_HEIGHT = 4  #明細部の線の高さ（調整値）
    
    #文字位置定数(加算値)
    POS_TOTAL_CHAR = 66           #小計・合計位置
    #POS_ROUGH_ESTIMATE_CHAR = 17  #概算
    
    PAYMENT_METHOD_TRANSFER = 1  #振込
    PAYMENT_METHOD_DEBIT = 2     #口座振替
    
    
    # 適切な PDF 用応答ヘッダを持った HttpResponse オブジェクトを
    # 作成します。
    response = HttpResponse(content_type='application/pdf')
    #response['Content-Disposition'] = 'attachment; filename=payment_list_1.pdf'
    response['Content-Disposition'] = 'inline; filename=payment_list_2.pdf'
    
    font_name = 'HeiseiKakuGo-W5'
    #font_name_bold = 'HeiseiKakuGo-W5-Bold'
    pdfmetrics.registerFont(UnicodeCIDFont(font_name))
        
    
    # レスポンスオブジェクトを出力「ファイル」にして、 PDF オブジェクト
    # を作成します。
    p = canvas.Canvas(response, pagesize=portrait(A4), bottomup=False)
    p.setFont(font_name, 12)
    
    # PDF に描画します。 PDF 生成のキモの部分です。
    y = START_Y;
    
    
    #タイトル
    p.setFont(font_name, 14)
    
    #今の所、複数月のレイアウトは考慮していない。
    tmp_date = cache.get('search_query_month_from')
    if tmp_date is not None:
        #◯◯◯◯年◯◯月〆の文字を作る
        tmp_year = tmp_date[0:4]
        tmp_month = tmp_date[5:7]
        
        str_title = tmp_year + "年" + tmp_month + "月" + "〆" + '　支払予定表'
        p.drawString(HEADER_X*mm, HEADER_Y*mm, str_title)
    else:
    #月指定してない場合
        str_title = '支払予定表'
        p.drawString((HEADER_X+15)*mm, HEADER_Y*mm, str_title)
    #
    
    p.setFont(font_name, 7)  #元のサイズに戻す
    
    #現在日付
    d = datetime.now().strftime('%Y/%m/%d')
    today = str(d) + "現在"
    p.drawString((POS_RIGHT_SIDE-22)*mm, (HEADER_Y +3)*mm, today)
    #
    
    #ヘッダー
    y += 2
    x = DETAIL_START_X
    #p.drawString(x*mm, (y+2)*mm, '未')
    
    x += 15
    p.drawString(x*mm, (y+2)*mm, '支払先')
    
    x += 25.5
    p.drawString(x*mm, (y+2)*mm, '項目')
    
    #x += 15
    x += 13
    p.drawString(x*mm, (y+2)*mm, '請求金額')
    
    #x += 17
    #p.drawString(x*mm, (y+2)*mm, '概算')
    
    #x += 13
    x += 15
    p.drawString(x*mm, (y+2)*mm, '支払方法')
    
    x += 15
    p.drawString(x*mm, (y+2)*mm, '支払金額')
    
    
    x += 16
    p.drawString(x*mm, (y+2)*mm, '手数料')
    
    #x += 36
    x += 18
    #p.drawString(x*mm, (y+2)*mm, '振込/引落先')
    p.drawString(x*mm, (y+2)*mm, '振込/振替元')
    
    #x += 37.5
    x += 24.5
    p.drawString(x*mm, y*mm, '支払')
    p.drawString((x-1)*mm, (y+3)*mm, '予定日')
    
    x += 11.5
    p.drawString(x*mm, (y+2)*mm, '支払日')
    
    x += 22
    p.drawString(x*mm, (y+2)*mm, '備考')
    
    #Y座標インクリメント
    y += SEP_Y+3
    
    #ヘッダ部罫線
    p.rect(POS_LEFT_SIDE*mm, (START_Y-1)*mm, (POS_RIGHT_SIDE-POS_LEFT_SIDE)*mm, (POS_HEADER_HEIGHT-1)*mm, fill=0) #枠
    #p.line(x1,y1,x2,y2)
    p.line(POS_CHECK_PAYED*mm, (START_Y-1)*mm, POS_CHECK_PAYED*mm, ((START_Y-1) + POS_HEADER_HEIGHT)*mm) #未の箇所の右端
    p.line(POS_NAME*mm, (START_Y-1)*mm, POS_NAME*mm, ((START_Y-1) + POS_HEADER_HEIGHT)*mm) #支払先の右端
    p.line(POS_ACCOUNT_TITLE*mm, (START_Y-1)*mm, POS_ACCOUNT_TITLE*mm, ((START_Y-1) + POS_HEADER_HEIGHT)*mm) #項目の右端
    p.line(POS_AMOUNT*mm, (START_Y-1)*mm, POS_AMOUNT*mm, ((START_Y-1) + POS_HEADER_HEIGHT)*mm) #金額の右端
    p.line(POS_PAY_DATE*mm, (START_Y-1)*mm, POS_PAY_DATE*mm, ((START_Y-1) + POS_HEADER_HEIGHT)*mm) #概算の右端
    p.line(POS_PAYMENT_METHOD*mm, (START_Y-1)*mm, POS_PAYMENT_METHOD*mm, ((START_Y-1) + POS_HEADER_HEIGHT)*mm) #支払方法の右端
    p.line(POS_PAYMENT_AMOUNT*mm, (START_Y-1)*mm, POS_PAYMENT_AMOUNT*mm, ((START_Y-1) + (POS_HEADER_HEIGHT -1))*mm) #支払金額の右端
    p.line(POS_COMMISSION*mm, (START_Y-1)*mm, POS_COMMISSION*mm, ((START_Y-1) + (POS_HEADER_HEIGHT -1))*mm) #手数料の右端
    p.line(POS_TRANSFER*mm, (START_Y-1)*mm, POS_TRANSFER*mm, ((START_Y-1) + POS_HEADER_HEIGHT)*mm) #振込先の右端
    p.line(POS_PAY_DUE_DATE*mm, (START_Y-1)*mm, POS_PAY_DUE_DATE*mm, ((START_Y-1) + POS_HEADER_HEIGHT)*mm) #支払予定日の右端
    #
    
    #import pdb; pdb.set_trace()
    
    #支払モデル取得（月指定--複数月は今の所考慮していない。）
    if cache.get('search_query_month_from') != None:
        search_query_month = cache.get('search_query_month_from')
        #◯月１日で検索するようにする
        search_query_month += "-01"
        payments = Payment.objects.all().filter(billing_year_month=search_query_month).order_by('payment_method_id', 'trade_division_id', 'order', 'id')
    else:
        payments = Payment.objects.all()
    
    #小計・合計用
    payment_method_id_saved = None
    subtotal_amount = 0
    total_amount = 0
    subtotal_rough_estimate = 0
    total_rough_estimate = 0
    i = 0
    
    for payment in payments:
        
        #小計
        i += 1 #カウンター
        if payment_method_id_saved != None and payment_method_id_saved != payment.payment_method_id:
            #p.setFont(font_name, 9)
            x = DETAIL_START_X + 42
            p.drawString(x*mm, y*mm, "計")
            
            x = DETAIL_START_X + POS_TOTAL_CHAR
            
            p.setFillColorRGB(0,0,188) #色を指定(青系)
            m = "￥" + str("{0:,d}".format(subtotal_amount))
            p.drawRightString(x*mm, y*mm, m)
            subtotal_amount = 0
            
            #概算金額小計
            #x += POS_ROUGH_ESTIMATE_CHAR
            #p.setFillColorRGB(0.15686,0.639215,0.58039) #色を指定(ビリジャン)
            #m = "￥" + str("{0:,d}".format(subtotal_rough_estimate))
            #p.drawRightString(x*mm, y*mm, m)
            #subtotal_rough_estimate = 0
            
            
            #罫線をセット
            p.line(POS_LEFT_SIDE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_LEFT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) 
            p.line(POS_CHECK_PAYED*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_CHECK_PAYED*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #未の箇所の右端
            p.line(POS_NAME*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_NAME*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #支払先の右端
            p.line(POS_ACCOUNT_TITLE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_ACCOUNT_TITLE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #項目の右端
            p.line(POS_AMOUNT*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_AMOUNT*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #金額の右端
            p.line(POS_PAY_DATE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_PAY_DATE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #概算の右端
            p.line(POS_PAYMENT_METHOD*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_PAYMENT_METHOD*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #支払方法の右端
            p.line(POS_PAYMENT_AMOUNT*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_PAYMENT_AMOUNT*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #支払金額の右端
            p.line(POS_COMMISSION*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_COMMISSION*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #手数料の右端
            p.line(POS_TRANSFER*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_TRANSFER*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #振込先の右端
            p.line(POS_PAY_DUE_DATE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_PAY_DUE_DATE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #支払予定日の右端
            p.line(POS_RIGHT_SIDE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_RIGHT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) 
            p.line(POS_LEFT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm, POS_RIGHT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #横線
            #
            #Yインクリメント
            y += SEP_Y
            
        p.setFillColorRGB(0,0,0)
        #p.setFont(font_name, 7)
        
        #小計・合計カウント用
        #金額
        if payment.billing_amount is not None:
            subtotal_amount += payment.billing_amount
            total_amount += payment.billing_amount
        #概算(未払のみカウント)
        if payment.payment_date is None:
            if payment.rough_estimate is not None:
                subtotal_rough_estimate += payment.rough_estimate
                total_rough_estimate += payment.rough_estimate
            else:
                subtotal_rough_estimate += 0
                total_rough_estimate += 0
        #
        #保存用
        payment_method_id_saved = payment.payment_method_id
        #
        
        #upd180405 提示用は、塗りつぶさない
        #p.setFillColorRGB(0,0,0)  #色を黒に戻す
        #
        
        x = DETAIL_START_X + 6
        
        #取引先名
        partner_name = str(payment.partner)
        
        #pn = partner_name.decode('utf-8')
        pn = partner_name.encode().decode('utf-8')
        
        if len(pn) <= 13:
           p.setFont(font_name, 7)
        else:
            p.setFont(font_name, 5.5)
        
        #partner_name = partner_name.encode("utf-8")
        if partner_name.find('振込手数料') == -1 :
            p.drawString(x*mm, y*mm, partner_name)
        else:
        #振込手数料の文字があれば右に寄せる
            p.drawRightString((x+20)*mm, y*mm, partner_name)
        
        p.setFont(font_name, 7)
        
        #項目(勘定科目等)
        x += 37
        if payment.account_title is not None:
          account_title = str(payment.account_title)
        else:
          account_title = settings.EMPTY_MARK
        p.drawCentredString(x*mm, y*mm, account_title)
        
        #支払金額
        #x += 25
        x += (POS_TOTAL_CHAR -43)
        
        if payment.billing_amount is not None:
            billing_amount = "￥" + str("{0:,d}".format(payment.billing_amount))  #桁区切り
            #billing_amount = "{0:>11}".format(billing_amount)  #右寄せ→できない
            p.drawRightString(x*mm, y*mm, billing_amount)
        
        #概算金額
          
        #支払方法
        x += 7
        
        #色に関して--RGBの各本来数値÷255となっている
        
        if payment.payment_method_id == PAYMENT_METHOD_TRANSFER:
        #振込
            p.setFillColorRGB(0,0,1) #色を指定(青系)
            
        elif payment.payment_method_id == PAYMENT_METHOD_DIRECT_DEBIT:
        #口座振替
            p.setFillColorRGB(0.71764,0.2549,0.05490) #色を指定(茶系-赤錆色)
            
        elif payment.payment_method_id == PAYMENT_METHOD_CACHE:
        #現金
            p.setFillColorRGB(0.1843,0.3098,0.2941)   #色を指定(緑系)
        
        payment_method = str(payment._meta.get_field('payment_method_id').choices[payment.payment_method_id][1])
        p.drawCentredString(x*mm, y*mm, payment_method)
        
        p.setFillColorRGB(0,0,0) #色を黒に戻す
        
        #振込・振替元
        x += 10
        if payment.payment_method_id == settings.ID_PAYMENT_METHOD_TRANSFER or \
             payment.payment_method_id == settings.ID_PAYMENT_METHOD_WITHDRAWAL:
        #振込・振替の場合
            #支払金額・手数料
            if (payment.payment_amount is not None and payment.billing_amount is not None and \
                 payment.payment_amount != billing_amount) or payment.commission is not None :
                #支払金額
                x += 13
                if payment.payment_amount is not None:
                    payment_amount = "￥" + str("{0:,d}".format(payment.payment_amount))  #桁区切り
                    p.drawRightString(x*mm, y*mm, payment_amount)
                #手数料
                x += 13
                if payment.commission is not None:
                    commission = "￥" + str("{0:,d}".format(payment.commission))  #桁区切り
                    p.drawRightString(x*mm, y*mm, commission)
                x += 10
            else:
                x += 36 
            #振込・振替元銀行
            try:
                bank = Bank.objects.get(pk=payment.source_bank_id)
            except Bank.DoesNotExist:
                bank = None
            if bank is not None:
                bank_name = str(bank.name)
                p.drawString(x*mm, y*mm, bank_name)
            x += 7
        else:
            x += 43
        #
        
        #支払予定日
        x += 15
        if payment.payment_due_date is not None:
            d = payment.payment_due_date.strftime('%m/%d')
            payment_due_date = str(d)
            p.drawString(x*mm, y*mm, payment_due_date)
        x += 12
        if payment.payment_date is not None:
            d = payment.payment_date.strftime('%m/%d')
            payment_date = str(d)
            p.drawString(x*mm, y*mm, payment_date)
        else:
        #未払の場合
            #x = DETAIL_START_X-1.5
            p.setFillColorRGB(1,0.3686,0.098) #色を指定(オレンジ系)
            #p.drawString(x*mm, y*mm, "未")
            p.rect(POS_LEFT_SIDE*mm, (y-POS_AJDUST_HEIGHT)*mm, (POS_CHECK_PAYED-POS_LEFT_SIDE)*mm, POS_DETAIL_HEIGHT*mm, fill=True) #枠
            
            p.setFillColorRGB(0,0,0)  #黒に戻す
        
        #備考
        x += 12
        note = str(payment.note)
        #p.drawCentredString(x*mm, y*mm, note)
        p.drawString(x*mm, y*mm, note)
        
        #罫線をセット
        p.line(POS_LEFT_SIDE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_LEFT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) 
        p.line(POS_CHECK_PAYED*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_CHECK_PAYED*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #未の箇所の右端
        p.line(POS_NAME*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_NAME*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #支払先の右端
        p.line(POS_ACCOUNT_TITLE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_ACCOUNT_TITLE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #項目の右端
        p.line(POS_AMOUNT*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_AMOUNT*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #金額の右端
        p.line(POS_PAY_DATE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_PAY_DATE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #概算の右端
        p.line(POS_PAYMENT_METHOD*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_PAYMENT_METHOD*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #支払方法の右端
        p.line(POS_PAYMENT_AMOUNT*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_PAYMENT_AMOUNT*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #支払金額の右端
        p.line(POS_COMMISSION*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_COMMISSION*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #手数料の右端
        p.line(POS_TRANSFER*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_TRANSFER*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #振込先の右端
        p.line(POS_PAY_DUE_DATE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_PAY_DUE_DATE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #支払予定日の右端
        p.line(POS_RIGHT_SIDE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_RIGHT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) 
        p.line(POS_LEFT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm, POS_RIGHT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #横線
        #
        
        #Y座標インクリメント
        y += SEP_Y
        
        #小計・合計(最終行)
        if i == len(payments):
            
            #金額小計
            x = DETAIL_START_X + 42
            p.drawString(x*mm, y*mm, "計")
            
            x = DETAIL_START_X + POS_TOTAL_CHAR
            p.setFillColorRGB(0,0,188) #色を指定
            m = "￥" + str("{0:,d}".format(subtotal_amount))
            p.drawRightString(x*mm, y*mm, m)
            
            #概算金額小計
            #x += POS_ROUGH_ESTIMATE_CHAR
            #p.setFillColorRGB(0.15686,0.639215,0.58039) #色を指定(ビリジャン)
            #m = "￥" + str("{0:,d}".format(subtotal_rough_estimate))
            #p.drawRightString(x*mm, y*mm, m)
            
            #subtotal_amount = 0
            #罫線をセット
            p.line(POS_LEFT_SIDE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_LEFT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) 
            p.line(POS_CHECK_PAYED*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_CHECK_PAYED*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #未の箇所の右端
            p.line(POS_NAME*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_NAME*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #支払先の右端
            p.line(POS_ACCOUNT_TITLE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_ACCOUNT_TITLE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #項目の右端
            p.line(POS_AMOUNT*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_AMOUNT*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #金額の右端
            p.line(POS_PAY_DATE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_PAY_DATE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #概算の右端
            p.line(POS_PAYMENT_METHOD*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_PAYMENT_METHOD*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #支払方法の右端
            p.line(POS_PAYMENT_AMOUNT*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_PAYMENT_AMOUNT*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #支払金額の右端
            p.line(POS_COMMISSION*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_COMMISSION*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #手数料の右端
            p.line(POS_TRANSFER*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_TRANSFER*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #振込先の右端
            p.line(POS_PAY_DUE_DATE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_PAY_DUE_DATE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #支払予定日の右端
            p.line(POS_RIGHT_SIDE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_RIGHT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) 
            p.line(POS_LEFT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm, POS_RIGHT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #横線
            #
    
            #金額合計
            y += SEP_Y #Yインクリメント
            #x = DETAIL_START_X + 41
            x = DETAIL_START_X + 40.5
            p.drawString(x*mm, y*mm, "合計")
            
            x = DETAIL_START_X + POS_TOTAL_CHAR
            p.setFillColorRGB(0,0,188) #色を指定
            m = "￥" + str("{0:,d}".format(total_amount))
            p.drawRightString(x*mm, y*mm, m)
            
            #概算金額
            #x += POS_ROUGH_ESTIMATE_CHAR
            #p.setFillColorRGB(0.15686,0.639215,0.58039) #色を指定(ビリジャン)
            #m = "￥" + str("{0:,d}".format(total_rough_estimate))
            #p.drawRightString(x*mm, y*mm, m)
            
            #subtotal_amount = 0
            #罫線をセット
            p.line(POS_LEFT_SIDE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_LEFT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) 
            p.line(POS_CHECK_PAYED*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_CHECK_PAYED*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #未の箇所の右端
            p.line(POS_NAME*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_NAME*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #支払先の右端
            p.line(POS_ACCOUNT_TITLE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_ACCOUNT_TITLE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #項目の右端
            p.line(POS_AMOUNT*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_AMOUNT*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #金額の右端
            p.line(POS_PAY_DATE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_PAY_DATE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #概算の右端
            p.line(POS_PAYMENT_METHOD*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_PAYMENT_METHOD*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #支払方法の右端
            p.line(POS_PAYMENT_AMOUNT*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_PAYMENT_AMOUNT*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #支払金額の右端
            p.line(POS_COMMISSION*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_COMMISSION*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #手数料の右端
            p.line(POS_TRANSFER*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_TRANSFER*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #振込先の右端
            p.line(POS_PAY_DUE_DATE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_PAY_DUE_DATE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #支払予定日の右端
            p.line(POS_RIGHT_SIDE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_RIGHT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) 
            p.line(POS_LEFT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm, POS_RIGHT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #横線
            #
            
            #注釈
            p.setFillColorRGB(0,0,0)
            y += SEP_Y
            x = DETAIL_START_X + 129
            message = "※支払金額は、請求金額と異なるものだけ記載しています。"
            p.drawString(x*mm, y*mm, message)
            
            #概算集計方法の注釈
            #y += SEP_Y #Yインクリメント
            
            #x = DETAIL_START_X + 122
            #message = "※概算の各計は、未払のものだけを集計しています。"
            #p.drawString(x*mm, y*mm, message)
    
    # PDF オブジェクトをきちんと閉じて終わり。
    p.showPage()
    p.save()
    return response
    
    
def set_title_normal(p,x,y):
#タイトル（ヘッダ部）出力(通常用)
   
    y = START_Y;
    
    #タイトル
    p.setFont(font_name, 14)
    
    tmp_date_from = cache.get('search_query_month_from')
    tmp_date_to = cache.get('search_query_month_to')
    
    if tmp_date_from is not None:
        #◯◯◯◯年◯◯月〆の文字を作る
        tmp_year = tmp_date_from[0:4]
        tmp_month = tmp_date_from[5:7]
        
        #if search_query_paid == False:
        if not search_query_paid:
            str_title = tmp_year + "年" + tmp_month + "月" + "〆" + '　支払予定表'
            p.drawString(HEADER_X*mm, HEADER_Y*mm, str_title)
        
            #月が複数指定の場合は、終了月も出力
            if tmp_date_from != tmp_date_to:
                #◯◯◯◯年◯◯月〆の文字を作る
                tmp_year = tmp_date_to[0:4]
                tmp_month = tmp_date_to[5:7]
                str_title = "〜" + tmp_year + "年" + tmp_month + "月" + "〆" 
                p.drawString((HEADER_X-5)*mm, (HEADER_Y+6)*mm, str_title)
        else:
            str_title = '支払予定表'
            p.drawString((HEADER_X+15)*mm, HEADER_Y*mm, str_title)
        
    else:
    #月指定してない場合
        str_title = '支払予定表'
        p.drawString((HEADER_X+15)*mm, HEADER_Y*mm, str_title)
    #
    
    p.setFont(font_name, 7)  #元のサイズに戻す
    
    #現在日付
    d = datetime.now().strftime('%Y/%m/%d')
    today = str(d) + "現在"
    p.drawString((POS_RIGHT_SIDE-22)*mm, (HEADER_Y +3)*mm, today)
    #
    
    #ヘッダー
    y += 2
    x = DETAIL_START_X
    #p.drawString(x*mm, (y+2)*mm, '未')
    
    x += 15
    p.drawString(x*mm, (y+2)*mm, '支払先')
    
    x += 25.5
    p.drawString(x*mm, (y+2)*mm, '項目')
    
    x += 15
    p.drawString(x*mm, (y+2)*mm, '金額')
    
    x += 17
    p.drawString(x*mm, (y+2)*mm, '概算')
    
    x += 13
    p.drawString(x*mm, (y+2)*mm, '支払方法')
    
    x += 36
    p.drawString(x*mm, (y+2)*mm, '振込先')
    
    x += 37.5
    p.drawString(x*mm, y*mm, '支払')
    p.drawString((x-1)*mm, (y+3)*mm, '予定日')
    
    x += 11.5
    p.drawString(x*mm, (y+2)*mm, '支払日')
    
    #Y座標インクリメント
    y += SEP_Y+3
    
    #ヘッダ部罫線
    p.rect(POS_LEFT_SIDE*mm, (START_Y-1)*mm, (POS_RIGHT_SIDE-POS_LEFT_SIDE)*mm, POS_HEADER_HEIGHT*mm, fill=0) #枠
    #p.line(x1,y1,x2,y2)
    p.line(POS_CHECK_PAYED*mm, (START_Y-1)*mm, POS_CHECK_PAYED*mm, ((START_Y-1) + POS_HEADER_HEIGHT)*mm) #未の箇所の右端
    p.line(POS_NAME*mm, (START_Y-1)*mm, POS_NAME*mm, ((START_Y-1) + POS_HEADER_HEIGHT)*mm) #支払先の右端
    p.line(POS_ACCOUNT_TITLE*mm, (START_Y-1)*mm, POS_ACCOUNT_TITLE*mm, ((START_Y-1) + POS_HEADER_HEIGHT)*mm) #項目の右端
    p.line(POS_AMOUNT*mm, (START_Y-1)*mm, POS_AMOUNT*mm, ((START_Y-1) + POS_HEADER_HEIGHT)*mm) #金額の右端
    p.line(POS_ROUGH_ESTIMATE*mm, (START_Y-1)*mm, POS_ROUGH_ESTIMATE*mm, ((START_Y-1) + POS_HEADER_HEIGHT)*mm) #概算の右端
    p.line(POS_PAYMENT_METHOD*mm, (START_Y-1)*mm, POS_PAYMENT_METHOD*mm, ((START_Y-1) + POS_HEADER_HEIGHT)*mm) #支払方法の右端
    p.line(POS_TRANSFER*mm, (START_Y-1)*mm, POS_TRANSFER*mm, ((START_Y-1) + POS_HEADER_HEIGHT)*mm) #振込先の右端
    p.line(POS_PAY_DUE_DATE*mm, (START_Y-1)*mm, POS_PAY_DUE_DATE*mm, ((START_Y-1) + POS_HEADER_HEIGHT)*mm) #支払予定日の右端
    #
    return p, x, y
    
    
def filter():
#フィルタリング
    results = None
    
    search_query_month_from = None
    search_query_month_to = None
    global multi_month; multi_month = False
    
    #開始月で抽出
    search_query_month_from = cache.get('search_query_month_from')
    if search_query_month_from:
        #◯月１日で検索するようにする
        search_query_month_from += "-01"
        results = Payment.objects.all().filter(billing_year_month__gte=search_query_month_from)
    
    #終了月で抽出
    search_query_month_to = cache.get('search_query_month_to')
    if search_query_month_to:
        #◯月１日で検索するようにする
        search_query_month_to += "-01"
        if results == None:
            results = Payment.objects.all().filter(billing_year_month__lte=search_query_month_to)
        else:
            results = results.filter(billing_year_month__lte=search_query_month_to)
    
        #開始月と終了月が異なる場合
        if search_query_month_from != search_query_month_to:
            multi_month = True
    
    #支払先で抽出
    search_query_partner = cache.get('search_query_partner')
    if search_query_partner:
        if results == None:
            results = Payment.objects.all().filter(partner_id=search_query_partner)
        else:
            results = results.filter(partner_id=search_query_partner)
    
    #取引区分で抽出
    search_query_trade_division_id = cache.get('search_query_trade_division_id')
    if search_query_trade_division_id:
        if results == None:
            results = Payment.objects.all().filter(trade_division_id=search_query_trade_division_id)
        else:
            results = results.filter(trade_division_id=search_query_trade_division_id)
     
    #支払方法で抽出
    search_query_payment = cache.get('search_query_payment')
    if search_query_payment:
        if results == None:
            results = Payment.objects.all().filter(payment_method_id=search_query_payment)
        else:
            results = results.filter(payment_method_id=search_query_payment)
     
    
    global search_query_paid
    search_query_paid = cache.get('search_query_paid')
    if search_query_paid:
        #支払状況で絞り込み
        if search_query_paid == "0":
            search_flag = True
            if results is None:
                results = Payment.objects.all().filter(payment_date__isnull=True).order_by('order')
            else:
                results = results.filter(payment_date__isnull=True)
        elif search_query_paid == "1":
        #支払済
            search_flag = True
            if results is None:
                results = Payment.objects.all().filter(payment_date__isnull=False)
            else:
                results = results.filter(payment_date__isnull=False)
    
    
    if results is not None:
    #条件検索なら、並び順を設定
        if multi_month == False:
            results = results.order_by('payment_method_id', 'trade_division_id', 'order', 'id')
        else:
            results = results.order_by('payment_method_id', 'trade_division_id', 'partner_id', 'billing_year_month', 'order', 'id')
    else:
    #条件なしの場合
        results = Payment.objects.all()
    
    return results


