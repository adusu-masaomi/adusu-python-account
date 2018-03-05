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

PAYMENT_METHOD_TRANSFER = 1   #支払方法（振込）の場合
PAYMENT_METHOD_DIRECT_DEBIT = 2   #支払方法（口座振替）の場合
PAYMENT_METHOD_CACHE = 3   #支払方法（現金）の場合

#支払集計表
def payment_list_1(request):
    
    #レポート関連定数
    HEADER_X = 75
    DETAIL_START_X = 20
    #
    HEADER_Y = 20
    START_Y = 30
    SEP_Y = 7
    
    #縦線用定数
    POS_LEFT_SIDE = 16    #左端
    POS_RIGHT_SIDE = 200  #右端
    
    POS_CHECK_PAYED = 24
    POS_NAME = 56
    POS_ACCOUNT_TITLE = 70
    POS_AMOUNT = 90
    POS_ROUGH_ESTIMATE = 104
    POS_PAYMENT_METHOD = 117
    POS_TRANSFER = 176
    POS_PAY_DUE_DATE = 188
    #横線用定数
    POS_HEADER_HEIGHT = 8   #ヘッダの線高さ
    POS_DETAIL_HEIGHT = 7  #明細部の線の高さ
    
    # 適切な PDF 用応答ヘッダを持った HttpResponse オブジェクトを
    # 作成します。
    response = HttpResponse(content_type='application/pdf')
    #response['Content-Disposition'] = 'attachment; filename=payment_list_1.pdf'
    response['Content-Disposition'] = 'inline; filename=payment_list_1.pdf'
    
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
    
    tmp_date = cache.get('search_query_month')
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
    
    x += 17
    p.drawString(x*mm, (y+2)*mm, '金額')
    
    x += 17
    p.drawString(x*mm, (y+2)*mm, '概算')
    
    x += 11
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
    
    #import pdb; pdb.set_trace()
    
    #支払モデル取得（月指定）
    if cache.get('search_query_month') != None:
        search_query_month = cache.get('search_query_month')
        #◯月１日で検索するようにする
        search_query_month += "-01"
        payments = Payment.objects.all().filter(billing_year_month=search_query_month).order_by('payment_method_id', 'trade_division_id', 'order')
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
            
            x = DETAIL_START_X + 68
            
            p.setFillColorRGB(0,0,188) #色を指定(青系)
            m = "￥" + str("{0:,d}".format(subtotal_amount))
            p.drawRightString(x*mm, y*mm, m)
            subtotal_amount = 0
            
            #概算金額小計(口座の場合のみ)
            if payment.payment_method_id == (PAYMENT_METHOD_DIRECT_DEBIT + 1) :
                x += 15
                #p.setFillColorRGB(0.3882,0.48627,0.20784) #色を指定(緑系)
                p.setFillColorRGB(0.8980,0,0.5254) #色を指定(ピンク系)
                m = "￥" + str("{0:,d}".format(subtotal_rough_estimate))
                p.drawRightString(x*mm, y*mm, m)
                subtotal_rough_estimate = 0
            #罫線をセット
            p.line(POS_LEFT_SIDE*mm, (y-5)*mm, POS_LEFT_SIDE*mm, ((y-5) + POS_DETAIL_HEIGHT)*mm) 
            p.line(POS_CHECK_PAYED*mm, (y-5)*mm, POS_CHECK_PAYED*mm, ((y-5) + POS_DETAIL_HEIGHT)*mm) #未の箇所の右端
            p.line(POS_NAME*mm, (y-5)*mm, POS_NAME*mm, ((y-5) + POS_DETAIL_HEIGHT)*mm) #支払先の右端
            p.line(POS_ACCOUNT_TITLE*mm, (y-5)*mm, POS_ACCOUNT_TITLE*mm, ((y-5) + POS_DETAIL_HEIGHT)*mm) #項目の右端
            p.line(POS_AMOUNT*mm, (y-5)*mm, POS_AMOUNT*mm, ((y-5) + POS_DETAIL_HEIGHT)*mm) #金額の右端
            p.line(POS_ROUGH_ESTIMATE*mm, (y-5)*mm, POS_ROUGH_ESTIMATE*mm, ((y-5) + POS_DETAIL_HEIGHT)*mm) #概算の右端
            p.line(POS_PAYMENT_METHOD*mm, (y-5)*mm, POS_PAYMENT_METHOD*mm, ((y-5) + POS_DETAIL_HEIGHT)*mm) #支払方法の右端
            p.line(POS_TRANSFER*mm, (y-5)*mm, POS_TRANSFER*mm, ((y-5) + POS_DETAIL_HEIGHT)*mm) #振込先の右端
            p.line(POS_PAY_DUE_DATE*mm, (y-5)*mm, POS_PAY_DUE_DATE*mm, ((y-5) + POS_DETAIL_HEIGHT)*mm) #支払予定日の右端
            p.line(POS_RIGHT_SIDE*mm, (y-5)*mm, POS_RIGHT_SIDE*mm, ((y-5) + POS_DETAIL_HEIGHT)*mm) 
            p.line(POS_LEFT_SIDE*mm, ((y-5) + POS_DETAIL_HEIGHT)*mm, POS_RIGHT_SIDE*mm, ((y-5) + POS_DETAIL_HEIGHT)*mm) #横線
            #
            #Yインクリメント
            y += SEP_Y
            
        p.setFillColorRGB(0,0,0)
        #p.setFont(font_name, 7)
        
        #小計・合計カウント用
        #金額
        subtotal_amount += payment.billing_amount
        total_amount += payment.billing_amount
        #概算
        if payment.rough_estimate != None:
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
        if payment.trade_division_id is 0:
            p.setFillColorRGB(0.737254,0.784313,0.858823)   #水色
        elif payment.trade_division_id is 1:
            p.setFillColorRGB(0.72549,0.84705,0.64705)   #抹茶色
        p.rect(POS_LEFT_SIDE*mm, (y-5)*mm, (POS_RIGHT_SIDE-POS_LEFT_SIDE)*mm, POS_DETAIL_HEIGHT*mm, fill=True) #枠
        p.setFillColorRGB(0,0,0)  #色を黒に戻す
        #
        
        x = DETAIL_START_X + 6
        
        #import pdb; pdb.set_trace()
        
        #取引先名
        partner_name = str(payment.partner)
        #partner_name = partner_name.encode("utf-8")
        p.drawString(x*mm, y*mm, partner_name)
        
        #項目(勘定科目等)
        x += 37
        if payment.account_title is not None:
          account_title = str(payment.account_title)
        else:
          account_title = settings.EMPTY_MARK
        p.drawCentredString(x*mm, y*mm, account_title)
        
        #支払金額
        x += 25
        billing_amount = "￥" + str("{0:,d}".format(payment.billing_amount))  #桁区切り
        #billing_amount = "{0:>11}".format(billing_amount)  #右寄せ→できない
        p.drawRightString(x*mm, y*mm, billing_amount)
        
        #概算金額
        x += 15
        if payment.rough_estimate is not None:
            rough_estimate = "￥" + str("{0:,d}".format(payment.rough_estimate))  #桁区切り
            p.drawRightString(x*mm, y*mm, rough_estimate)
        
        #支払方法
        x += 7
        
        if payment.payment_method_id is PAYMENT_METHOD_TRANSFER:
        #振込
            #p.setFillColorRGB(0.33725,0.38823,0.56078) #色を指定(青系)
            p.setFillColorRGB(0.1998,0.0196, 1) #色を指定(青系-露草色)
        elif payment.payment_method_id is PAYMENT_METHOD_DIRECT_DEBIT:
        #口座振替
            #p.setFillColorRGB(0.3098,0.2235,0.1843) #色を指定(茶系)
            p.setFillColorRGB(0.6196,0.3098,0.17647) #色を指定(茶系-栗梅)
        elif payment.payment_method_id is PAYMENT_METHOD_CACHE:
        #現金
            p.setFillColorRGB(0.1843,0.3098,0.2941)   #色を指定(緑系)
        
        payment_method = str(payment._meta.get_field('payment_method_id').choices[payment.payment_method_id][1])
        p.drawCentredString(x*mm, y*mm, payment_method)
        
        p.setFillColorRGB(0,0,0) #色を黒に戻す
        
        #口座番号等（振込の場合）
        x += 10
        if payment.payment_method_id == 1:
            partner = Partner.objects.get(pk=payment.partner_id)
            if partner is not  None:
                bank = Bank.objects.get(pk=partner.bank_id)
                if bank is not None:
                    bank_name = str(bank.name)
                    #銀行
                    p.drawString(x*mm, y*mm, bank_name)
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
            p.rect(POS_LEFT_SIDE*mm, (y-5)*mm, (POS_CHECK_PAYED-POS_LEFT_SIDE)*mm, POS_DETAIL_HEIGHT*mm, fill=True) #枠
            
            p.setFillColorRGB(0,0,0)  #黒に戻す
        
        #罫線をセット
        p.line(POS_LEFT_SIDE*mm, (y-5)*mm, POS_LEFT_SIDE*mm, ((y-5) + POS_DETAIL_HEIGHT)*mm) 
        p.line(POS_CHECK_PAYED*mm, (y-5)*mm, POS_CHECK_PAYED*mm, ((y-5) + POS_DETAIL_HEIGHT)*mm) #未の箇所の右端
        p.line(POS_NAME*mm, (y-5)*mm, POS_NAME*mm, ((y-5) + POS_DETAIL_HEIGHT)*mm) #支払先の右端
        p.line(POS_ACCOUNT_TITLE*mm, (y-5)*mm, POS_ACCOUNT_TITLE*mm, ((y-5) + POS_DETAIL_HEIGHT)*mm) #項目の右端
        p.line(POS_AMOUNT*mm, (y-5)*mm, POS_AMOUNT*mm, ((y-5) + POS_DETAIL_HEIGHT)*mm) #金額の右端
        p.line(POS_ROUGH_ESTIMATE*mm, (y-5)*mm, POS_ROUGH_ESTIMATE*mm, ((y-5) + POS_DETAIL_HEIGHT)*mm) #概算の右端
        p.line(POS_PAYMENT_METHOD*mm, (y-5)*mm, POS_PAYMENT_METHOD*mm, ((y-5) + POS_DETAIL_HEIGHT)*mm) #支払方法の右端
        p.line(POS_TRANSFER*mm, (y-5)*mm, POS_TRANSFER*mm, ((y-5) + POS_DETAIL_HEIGHT)*mm) #振込先の右端
        p.line(POS_PAY_DUE_DATE*mm, (y-5)*mm, POS_PAY_DUE_DATE*mm, ((y-5) + POS_DETAIL_HEIGHT)*mm) #支払予定日の右端
        p.line(POS_RIGHT_SIDE*mm, (y-5)*mm, POS_RIGHT_SIDE*mm, ((y-5) + POS_DETAIL_HEIGHT)*mm) 
        p.line(POS_LEFT_SIDE*mm, ((y-5) + POS_DETAIL_HEIGHT)*mm, POS_RIGHT_SIDE*mm, ((y-5) + POS_DETAIL_HEIGHT)*mm) #横線
        #
        
        #Y座標インクリメント
        y += SEP_Y
        
        #小計・合計(最終行)
        if i == len(payments):
            
            #金額小計
            x = DETAIL_START_X + 42
            p.drawString(x*mm, y*mm, "計")
            
            x = DETAIL_START_X + 68
            p.setFillColorRGB(0,0,188) #色を指定
            m = "￥" + str("{0:,d}".format(subtotal_amount))
            p.drawRightString(x*mm, y*mm, m)
            
            #概算金額小計(口座振替の場合のみ)
            if payment.payment_method_id == (PAYMENT_METHOD_DIRECT_DEBIT) :
                x += 16
                p.setFillColorRGB(0.8980,0,0.5254) #色を指定(ピンク系)
                m = "￥" + str("{0:,d}".format(subtotal_rough_estimate))
                p.drawRightString(x*mm, y*mm, m)
                #subtotal_rough_estimate = 0
            #subtotal_amount = 0
            #罫線をセット
            p.line(POS_LEFT_SIDE*mm, (y-5)*mm, POS_LEFT_SIDE*mm, ((y-5) + POS_DETAIL_HEIGHT)*mm) 
            p.line(POS_CHECK_PAYED*mm, (y-5)*mm, POS_CHECK_PAYED*mm, ((y-5) + POS_DETAIL_HEIGHT)*mm) #未の箇所の右端
            p.line(POS_NAME*mm, (y-5)*mm, POS_NAME*mm, ((y-5) + POS_DETAIL_HEIGHT)*mm) #支払先の右端
            p.line(POS_ACCOUNT_TITLE*mm, (y-5)*mm, POS_ACCOUNT_TITLE*mm, ((y-5) + POS_DETAIL_HEIGHT)*mm) #項目の右端
            p.line(POS_AMOUNT*mm, (y-5)*mm, POS_AMOUNT*mm, ((y-5) + POS_DETAIL_HEIGHT)*mm) #金額の右端
            p.line(POS_ROUGH_ESTIMATE*mm, (y-5)*mm, POS_ROUGH_ESTIMATE*mm, ((y-5) + POS_DETAIL_HEIGHT)*mm) #概算の右端
            p.line(POS_PAYMENT_METHOD*mm, (y-5)*mm, POS_PAYMENT_METHOD*mm, ((y-5) + POS_DETAIL_HEIGHT)*mm) #支払方法の右端
            p.line(POS_TRANSFER*mm, (y-5)*mm, POS_TRANSFER*mm, ((y-5) + POS_DETAIL_HEIGHT)*mm) #振込先の右端
            p.line(POS_PAY_DUE_DATE*mm, (y-5)*mm, POS_PAY_DUE_DATE*mm, ((y-5) + POS_DETAIL_HEIGHT)*mm) #支払予定日の右端
            p.line(POS_RIGHT_SIDE*mm, (y-5)*mm, POS_RIGHT_SIDE*mm, ((y-5) + POS_DETAIL_HEIGHT)*mm) 
            p.line(POS_LEFT_SIDE*mm, ((y-5) + POS_DETAIL_HEIGHT)*mm, POS_RIGHT_SIDE*mm, ((y-5) + POS_DETAIL_HEIGHT)*mm) #横線
            #
    
            #金額合計
            y += SEP_Y #Yインクリメント
            x = DETAIL_START_X + 41
            p.drawString(x*mm, y*mm, "合計")
            
            x = DETAIL_START_X + 68
            p.setFillColorRGB(0,0,188) #色を指定
            m = "￥" + str("{0:,d}".format(total_amount))
            p.drawRightString(x*mm, y*mm, m)
            
            #概算金額(ひとまず省略)
            #subtotal_amount = 0
            #罫線をセット
            p.line(POS_LEFT_SIDE*mm, (y-5)*mm, POS_LEFT_SIDE*mm, ((y-5) + POS_DETAIL_HEIGHT)*mm) 
            p.line(POS_CHECK_PAYED*mm, (y-5)*mm, POS_CHECK_PAYED*mm, ((y-5) + POS_DETAIL_HEIGHT)*mm) #未の箇所の右端
            p.line(POS_NAME*mm, (y-5)*mm, POS_NAME*mm, ((y-5) + POS_DETAIL_HEIGHT)*mm) #支払先の右端
            p.line(POS_ACCOUNT_TITLE*mm, (y-5)*mm, POS_ACCOUNT_TITLE*mm, ((y-5) + POS_DETAIL_HEIGHT)*mm) #項目の右端
            p.line(POS_AMOUNT*mm, (y-5)*mm, POS_AMOUNT*mm, ((y-5) + POS_DETAIL_HEIGHT)*mm) #金額の右端
            p.line(POS_ROUGH_ESTIMATE*mm, (y-5)*mm, POS_ROUGH_ESTIMATE*mm, ((y-5) + POS_DETAIL_HEIGHT)*mm) #概算の右端
            p.line(POS_PAYMENT_METHOD*mm, (y-5)*mm, POS_PAYMENT_METHOD*mm, ((y-5) + POS_DETAIL_HEIGHT)*mm) #支払方法の右端
            p.line(POS_TRANSFER*mm, (y-5)*mm, POS_TRANSFER*mm, ((y-5) + POS_DETAIL_HEIGHT)*mm) #振込先の右端
            p.line(POS_PAY_DUE_DATE*mm, (y-5)*mm, POS_PAY_DUE_DATE*mm, ((y-5) + POS_DETAIL_HEIGHT)*mm) #支払予定日の右端
            p.line(POS_RIGHT_SIDE*mm, (y-5)*mm, POS_RIGHT_SIDE*mm, ((y-5) + POS_DETAIL_HEIGHT)*mm) 
            p.line(POS_LEFT_SIDE*mm, ((y-5) + POS_DETAIL_HEIGHT)*mm, POS_RIGHT_SIDE*mm, ((y-5) + POS_DETAIL_HEIGHT)*mm) #横線
            #
    
    
    # PDF オブジェクトをきちんと閉じて終わり。
    p.showPage()
    p.save()
    return response


