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
#↑要整理
from account.models import Cash_Flow_Header
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

from datetime import date
import calendar    #月末日取得用  add180911
#fontname = "IPA Gothic"

PAYMENT_METHOD_TRANSFER = 1       #支払方法（振込）の場合
PAYMENT_METHOD_DIRECT_DEBIT = 2   #支払方法（口座振替）の場合
PAYMENT_METHOD_CACHE = 4          #支払方法（現金）の場合

MAX_LINE_LIST_1 = 48    #支払集計表の１ページ最大行数

#資金繰り表(1)
def cash_flow_list_1(request):
    
    #レポート関連定数(主に、サブルーチン用にグローバル化)
    #global HEADER_X; HEADER_X = 75
    global HEADER_X; HEADER_X = 5
    
    #global DETAIL_START_X; DETAIL_START_X = 20
    global DETAIL_START_X; DETAIL_START_X = 12
    #
    global HEADER_Y; HEADER_Y = 20
    #global START_Y; START_Y = 30
    global START_Y; START_Y = 25
    
    global SEP_Y; SEP_Y = 5 
    
    #縦線用定数
    global POS_LEFT_SIDE; POS_LEFT_SIDE = 5    #左端
    #global POS_LEFT_SIDE; POS_LEFT_SIDE = 20    #左端
    
    #global POS_RIGHT_SIDE; POS_RIGHT_SIDE = 296  #右端
    global POS_RIGHT_SIDE; POS_RIGHT_SIDE = 262  #右端
    
    global POS_DATE; POS_DATE = 19
    global POS_WEEK; POS_WEEK = 24
    #global POS_EXPENSE; POS_EXPENSE = 56
    global POS_PLAN_EXPENSE; POS_PLAN_EXPENSE = 41
    global POS_EXPENSE; POS_EXPENSE = 58
    
    #global POS_INCOME; POS_INCOME = 70
    global POS_PLAN_INCOME; POS_PLAN_INCOME = 75
    global POS_INCOME; POS_INCOME = 92
    
    global POS_PLAN_HOKUETSU; POS_PLAN_HOKUETSU = 109  #+22  +17
    global POS_ACTUAL_HOKUETSU; POS_ACTUAL_HOKUETSU = 126
    global POS_PLAN_SANSHIN; POS_PLAN_SANSHIN = 143
    global POS_ACTUAL_SANSHIN; POS_ACTUAL_SANSHIN = 160
    #global POS_PLAN_SANSHIN_H; POS_PLAN_SANSHIN_H = 188
    global POS_PLAN_SANSHIN_H; POS_PLAN_SANSHIN_H = 177
    global POS_ACTUAL_SANSHIN_H; POS_ACTUAL_SANSHIN_H = 194
    
    global POS_PLAN_CASH_C; POS_PLAN_CASH_C = 211
    global POS_ACTUAL_CASH_C; POS_ACTUAL_CASH_C = 228
    global POS_PLAN_TOTAL_L; POS_PLAN_TOTAL_L = 245
    global POS_ACTUAL_TOTAL_L; POS_ACTUAL_TOTAL_L = 262
    
    
    #global POS_PLAN_CASH_P; POS_PLAN_CASH_P = 211
    #global POS_ACTUAL_CASH_P; POS_ACTUAL_CASH_P = 228
    #global POS_PLAN_CASH_C; POS_PLAN_CASH_C = 245
    #global POS_ACTUAL_CASH_C; POS_ACTUAL_CASH_C = 262
    #global POS_PLAN_TOTAL_L; POS_PLAN_TOTAL_L = 279
    #global POS_ACTUAL_TOTAL_L; POS_ACTUAL_TOTAL_L = 296
    
    global POS_ADJUST; POS_ADJUST = 0.5  #調整用
    
    #横線用定数
    #global POS_HEADER_HEIGHT; POS_HEADER_HEIGHT = 8   #ヘッダの線高さ
    global POS_HEADER_HEIGHT; POS_HEADER_HEIGHT = 11   #ヘッダの線高さ
    
    POS_DETAIL_HEIGHT = 5  #明細部の線の高さ(文字基準)
    POS_AJDUST_HEIGHT = 4  #明細部の線の高さ（調整値）
    
    #文字位置定数(加算値)
    POS_TOTAL_CHAR = 66           #小計・合計位置
    POS_PLAN_ACTUAL_CHAR = 17  #概算
    
    #日付表示用
    end_year = 0
    end_month = 0
    lastday = 0
    # 曜日情報の文字列表現
    week_name_list='月火水木金土日'
    
    
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
    p = canvas.Canvas(response, pagesize=landscape(A4), bottomup=False)
    p.setFont(font_name, 12)
    
    # PDF に描画します。 PDF 生成のキモの部分です。
    
    #条件でクエリーセット抽出
    #payments = filter_month(end_year, end_month, lastday)
    results = None
    search_query_pay_month_from = None
    search_query_pay_month_to = None
    
    #search_query_pay_month_from = cache.get('search_query_bp_month_from')
    search_query_pay_month_from = cache.get('search_query_cash_flow_date_from')
    
    #
    search_query_pay_month_only_from = ""
    
    if search_query_pay_month_from:
        
        search_query_pay_month_only_from = search_query_pay_month_from  #月までの文字でも保存しておく
        
        search_query_pay_month_from += "-01"
        
        #月末日で検索する
        end_year = int(search_query_pay_month_from[0:4])
        end_month = int(search_query_pay_month_from[5:7])
            
        _, lastday = calendar.monthrange(end_year,end_month)
    
    
    #import pdb; pdb.set_trace()
    
    
    #タイトル部出力
    x = 0
    y = 0
    
    p,x,y = set_title_normal(p,x,y)
        
    #小計・合計用
    payment_method_id_saved = None
    subtotal_amount = 0
    total_amount = 0
    subtotal_rough_estimate = 0
    total_rough_estimate = 0
    i = 0
    cnt = 0  #ページ内の行カウント用
    
    #縦計用
    expected_expense_total = 0
    actual_expense_total = 0
    expected_income_total = 0
    actual_income_total = 0
    expected_hokuetsu_total = 0
    actual_hokuetsu_total = 0
    expected_sanshin_tsukanome_total = 0
    actual_sanshin_tsukanome_total = 0
    expected_sanshin_main_total = 0
    actual_sanshin_main_total = 0
    expected_cash_president_total = 0
    actual_cash_president_total = 0
    expected_cash_company_total = 0
    actual_cash_company_total = 0
    #
    
    #for i in range(1, lastday+1):
    for i in range(lastday):   
        #小計
        #i += 1 #カウンター
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
            #p.drawString(x*mm, y*mm, "計")
            
            x = DETAIL_START_X + POS_TOTAL_CHAR
            
            p.setFillColorRGB(0,0,188) #色を指定(青系)
            m = "￥" + str("{0:,d}".format(subtotal_amount))
            #p.drawRightString(x*mm, y*mm, m)
            subtotal_amount = 0
            
            x += POS_PLAN_ACTUAL_CHAR
            p.setFillColorRGB(0.15686,0.639215,0.58039) #色を指定(ビリジャン)
            m = "￥" + str("{0:,d}".format(subtotal_rough_estimate))
            #p.drawRightString(x*mm, y*mm, m)
            subtotal_rough_estimate = 0
            
            
            #罫線をセット
            p.line(POS_LEFT_SIDE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_LEFT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) 
            p.line(POS_DATE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_DATE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #未の箇所の右端
            p.line(POS_WEEK*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_WEEK*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #未の箇所の右端
            p.line(POS_EXPENSE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_EXPENSE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #支払先の右端
            p.line(POS_PLAN_EXPENSE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_PLAN_EXPENSE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #支払先の右端
            p.line(POS_INCOME*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_INCOME*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #収入の右端
            p.line(POS_PLAN_INCOME*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_PLAN_INCOME*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #収入の右端
            p.line(POS_PLAN_HOKUETSU*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_PLAN_HOKUETSU*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #金額の右端
            p.line(POS_ACTUAL_HOKUETSU*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_ACTUAL_HOKUETSU*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #概算の右端
            p.line(POS_PLAN_SANSHIN*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_PLAN_SANSHIN*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #支払方法の右端
            p.line(POS_ACTUAL_SANSHIN*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_ACTUAL_SANSHIN*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #振込先の右端
            p.line(POS_PLAN_SANSHIN_H*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_PLAN_SANSHIN_H*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #支払予定日の右端
            p.line(POS_ACTUAL_SANSHIN_H*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_ACTUAL_SANSHIN_H*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #三信本店の右端
            
            p.line(POS_PLAN_CASH_P*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_PLAN_CASH_P*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #三信本店の右端
            p.line(POS_ACTUAL_CASH_P*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_ACTUAL_CASH_P*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #三信本店の右端
            p.line(POS_PLAN_CASH_C*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_PLAN_CASH_C*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #三信本店の右端
            p.line(POS_ACTUAL_CASH_C*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_ACTUAL_CASH_C*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #三信本店の右端
            p.line(POS_PLAN_TOTAL_L*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_PLAN_TOTAL_L*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #三信本店の右端
            
            
            p.line(POS_RIGHT_SIDE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_RIGHT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) 
            p.line(POS_LEFT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm, POS_RIGHT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #横線
            #
            #Yインクリメント
            y += SEP_Y
            
        p.setFillColorRGB(0,0,0)
        #p.setFont(font_name, 7)
        
        #x = DETAIL_START_X + 6
        x = DETAIL_START_X - 5
        #日付
        
        #曜日
        #d = date(end_year,end_month,i)
        d = date(end_year,end_month,i+1)
        weekday = week_name_list[d.weekday()]
        
        #monthDate = str(end_month) + "月" + str(i) + "日"
        monthDate = str(end_month) + "月" + str(i+1) + "日"
        p.drawString(x*mm, y*mm, monthDate)
        
        p.drawString((POS_WEEK - 3.5)*mm, y*mm, weekday)
        
        
        tmpDay = str(i+1).zfill(2)
            
        #文字→日付へ変換
        string_date = search_query_pay_month_only_from + "-" + tmpDay
        cash_flow_date = datetime.strptime(string_date, '%Y-%m-%d')
        
        #日付をセットし見出データを取得
        try:
            cash_flow_header = Cash_Flow_Header.objects.all().filter(cash_flow_date=cash_flow_date).first()
        except ObjectDoesNotExist:
            cash_flow_header = None
            
        #データ存在する場合のみ発行
        if cash_flow_header:
        
            #p.setFont(font_name, 7)
            #x += 37
           
            p.setFont(font_name, 6.5)
            
            total_expected = 0  #横計(予定)
            total_actual = 0    #横計(実際)
            
            #支出金額(予定)
            x = POS_PLAN_EXPENSE - POS_ADJUST
             
            if cash_flow_header.expected_expense is not None:
                if cash_flow_header.expected_expense > 0:
                    expected_expense_total += cash_flow_header.expected_expense #縦計用
                    expected_expense = "￥" + str("{0:,d}".format(cash_flow_header.expected_expense))  #桁区切り
                    p.drawRightString(x*mm, y*mm, expected_expense)
            
            #支出金額(実際)
            x = POS_EXPENSE - POS_ADJUST
             
            if cash_flow_header.actual_expense is not None:
                if cash_flow_header.actual_expense > 0:
                    actual_expense_total += cash_flow_header.actual_expense #縦計用
                    actual_expense = "￥" + str("{0:,d}".format(cash_flow_header.actual_expense))  #桁区切り
                    p.drawRightString(x*mm, y*mm, actual_expense)
            
            #収入金額(予定)
            x = POS_PLAN_INCOME - POS_ADJUST
             
            if cash_flow_header.expected_income is not None:
                #収入のマイナスは考慮してない(abs)
                if cash_flow_header.expected_income > 0:
                    expected_income_total += cash_flow_header.expected_income #縦計用
                    expected_income = "￥" + str("{0:,d}".format(cash_flow_header.expected_income))  #桁区切り
                    p.drawRightString(x*mm, y*mm, expected_income)
            
            
            #収入金額(実際)
            x = POS_INCOME - POS_ADJUST
             
            if cash_flow_header.actual_income is not None:
                #収入のマイナスは考慮してない(abs)
                if cash_flow_header.actual_income > 0:
                    actual_income_total += cash_flow_header.actual_income #縦計用
                    actual_income = "￥" + str("{0:,d}".format(cash_flow_header.actual_income))  #桁区切り
                    p.drawRightString(x*mm, y*mm, actual_income)
                
            #北越(予定)
            x = POS_PLAN_HOKUETSU - POS_ADJUST
             
            if cash_flow_header.expected_hokuetsu is not None:
                if abs(cash_flow_header.expected_hokuetsu) > 0:
                    expected_hokuetsu_total += cash_flow_header.expected_hokuetsu #縦計用
                    expected_hokuetsu = "￥" + str("{0:,d}".format(cash_flow_header.expected_hokuetsu))  #桁区切り
                    p.drawRightString(x*mm, y*mm, expected_hokuetsu)
            
            #北越(実際)
            x = POS_ACTUAL_HOKUETSU - POS_ADJUST
             
            if cash_flow_header.actual_hokuetsu is not None:
                if abs(cash_flow_header.actual_hokuetsu) > 0:
                    actual_hokuetsu_total += cash_flow_header.actual_hokuetsu #縦計用
                    actual_hokuetsu = "￥" + str("{0:,d}".format(cash_flow_header.actual_hokuetsu))  #桁区切り
                    p.drawRightString(x*mm, y*mm, actual_hokuetsu)
            
            #三信塚野目(予定)
            x = POS_PLAN_SANSHIN - POS_ADJUST
             
            if cash_flow_header.expected_sanshin_tsukanome is not None:
                if abs(cash_flow_header.expected_sanshin_tsukanome) > 0:
                    expected_sanshin_tsukanome_total += cash_flow_header.expected_sanshin_tsukanome #縦計用
                    expected_sanshin_tsukanome = "￥" + str("{0:,d}".format(cash_flow_header.expected_sanshin_tsukanome))  #桁区切り
                    p.drawRightString(x*mm, y*mm, expected_sanshin_tsukanome)
            
            #三信塚野目(実際)
            x = POS_ACTUAL_SANSHIN - POS_ADJUST
             
            if cash_flow_header.actual_sanshin_tsukanome is not None:
                if abs(cash_flow_header.actual_sanshin_tsukanome) > 0:
                    actual_sanshin_tsukanome_total += cash_flow_header.actual_sanshin_tsukanome #縦計用
                    actual_sanshin_tsukanome = "￥" + str("{0:,d}".format(cash_flow_header.actual_sanshin_tsukanome))  #桁区切り
                    p.drawRightString(x*mm, y*mm, actual_sanshin_tsukanome)
            
            #三信本店(予定)
            x = POS_PLAN_SANSHIN_H - POS_ADJUST
             
            if cash_flow_header.expected_sanshin_main is not None:
                if abs(cash_flow_header.expected_sanshin_main) > 0:
                    expected_sanshin_main_total += cash_flow_header.expected_sanshin_main #縦計用
                    expected_sanshin_main = "￥" + str("{0:,d}".format(cash_flow_header.expected_sanshin_main))  #桁区切り
                    p.drawRightString(x*mm, y*mm, expected_sanshin_main)
            
            #三信本店(実際)
            x = POS_ACTUAL_SANSHIN_H - POS_ADJUST
             
            if cash_flow_header.actual_sanshin_main is not None:
                if abs(cash_flow_header.actual_sanshin_main) > 0:
                    actual_sanshin_main_total += cash_flow_header.actual_sanshin_main #縦計用
                    actual_sanshin_main = "￥" + str("{0:,d}".format(cash_flow_header.actual_sanshin_main))  #桁区切り
                    p.drawRightString(x*mm, y*mm, actual_sanshin_main)
            
            #現金社長(予定)
            #x = POS_PLAN_CASH_P - POS_ADJUST
            #if cash_flow_header.expected_cash_president is not None:
            #    if abs(cash_flow_header.expected_cash_president) > 0:
            #        expected_cash_president_total += cash_flow_header.expected_cash_president #縦計用
            #        expected_cash_president = "￥" + str("{0:,d}".format(cash_flow_header.expected_cash_president))  #桁区切り
            #        p.drawRightString(x*mm, y*mm, expected_cash_president)
            #現金社長(実際)
            #x = POS_ACTUAL_CASH_P - POS_ADJUST
            #if cash_flow_header.actual_cash_president is not None:
            #    if abs(cash_flow_header.actual_cash_president) > 0:
            #        actual_cash_president_total += cash_flow_header.actual_cash_president  #縦計用
            #        actual_cash_president = "￥" + str("{0:,d}".format(cash_flow_header.actual_cash_president))  #桁区切り
            #        p.drawRightString(x*mm, y*mm, actual_cash_president)
            
            #現金会社(予定)
            x = POS_PLAN_CASH_C - POS_ADJUST
             
            if cash_flow_header.expected_cash_company is not None:
                if abs(cash_flow_header.expected_cash_company) > 0:
                    expected_cash_company_total += cash_flow_header.expected_cash_company  #縦計用
                    expected_cash_company = "￥" + str("{0:,d}".format(cash_flow_header.expected_cash_company))  #桁区切り
                    p.drawRightString(x*mm, y*mm, expected_cash_company)
            
            #現金会社(実際)
            x = POS_ACTUAL_CASH_C - POS_ADJUST
             
            if cash_flow_header.actual_cash_company is not None:
                if abs(cash_flow_header.actual_cash_company) > 0:
                    actual_cash_company_total += cash_flow_header.actual_cash_company  #縦計用
                    actual_cash_company = "￥" + str("{0:,d}".format(cash_flow_header.actual_cash_company))  #桁区切り
                    p.drawRightString(x*mm, y*mm, actual_cash_company)
        
            #横計(予定)
            total_expected = cash_flow_header.expected_income - cash_flow_header.expected_expense
            if abs(total_expected) > 0:
                x = POS_PLAN_TOTAL_L - POS_ADJUST
                total_expected_s = "￥" + str("{0:,d}".format(total_expected))  #桁区切り
                p.drawRightString(x*mm, y*mm, total_expected_s)
            
            
            #横計(実際)
            total_actual = cash_flow_header.actual_income - cash_flow_header.actual_expense
            if abs(total_actual) > 0:
                x = POS_ACTUAL_TOTAL_L - POS_ADJUST
                total_actual_s = "￥" + str("{0:,d}".format(total_actual))  #桁区切り
                p.drawRightString(x*mm, y*mm, total_actual_s)
            
        
        
        #概算金額
        x += POS_PLAN_ACTUAL_CHAR
        #if payment.rough_estimate is not None:
        #    p.setFillColorRGB(0.5490,0.5490,0.5490) #色を指定(グレー)
        
        #    rough_estimate = "￥" + str("{0:,d}".format(payment.rough_estimate))  #桁区切り
        #    p.drawRightString(x*mm, y*mm, rough_estimate)
        #p.setFillColorRGB(0,0,0) #色を黒に戻す
        
        #支払方法
        x += 7
        
        #色に関して--RGBの各本来数値÷255となっている
        
        #if payment.payment_method_id == PAYMENT_METHOD_TRANSFER:
        #振込
        #    p.setFillColorRGB(0,0,1) #色を指定(青系)
            
        #elif payment.payment_method_id == PAYMENT_METHOD_DIRECT_DEBIT:
        #口座振替
        #    p.setFillColorRGB(0.71764,0.2549,0.05490) #色を指定(茶系-赤錆色)
            
        #elif payment.payment_method_id == PAYMENT_METHOD_CACHE:
        #現金
        #    p.setFillColorRGB(0.1843,0.3098,0.2941)   #色を指定(緑系)
        
        #payment_method = str(payment._meta.get_field('payment_method_id').choices[payment.payment_method_id][1])
        #p.drawCentredString(x*mm, y*mm, payment_method)
        
        p.setFillColorRGB(0,0,0) #色を黒に戻す
        
        #口座番号等（振込の場合）
        x += 10
        
        x += 43
        
        #支払予定日
        x += 15
        #if payment.payment_due_date is not None:
        #    d = payment.payment_due_date.strftime('%m/%d')
        #    payment_due_date = str(d)
        #    p.drawString(x*mm, y*mm, payment_due_date)
        x += 12
        #if payment.payment_date is not None:
        #    d = payment.payment_date.strftime('%m/%d')
        #    payment_date = str(d)
        #    p.drawString(x*mm, y*mm, payment_date)
        #else:
        #未払の場合
        #    x = DETAIL_START_X-1.5
        #    p.setFillColorRGB(1,0.3686,0.098) #色を指定(オレンジ系)
        #    p.rect(POS_LEFT_SIDE*mm, (y-POS_AJDUST_HEIGHT)*mm, (POS_WEEK-POS_LEFT_SIDE)*mm, POS_DETAIL_HEIGHT*mm, fill=True) #枠
        #    p.setFillColorRGB(0,0,0)  #黒に戻す
        
        #罫線をセット
        p.line(POS_LEFT_SIDE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_LEFT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) 
        p.line(POS_DATE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_DATE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #未の箇所の右端
        p.line(POS_WEEK*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_WEEK*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #未の箇所の右端
        p.line(POS_EXPENSE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_EXPENSE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #支払先の右端
        p.line(POS_PLAN_EXPENSE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_PLAN_EXPENSE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #支払先の右端
        p.line(POS_INCOME*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_INCOME*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #項目の右端
        p.line(POS_PLAN_INCOME*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_PLAN_INCOME*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #項目の右端
        p.line(POS_PLAN_HOKUETSU*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_PLAN_HOKUETSU*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #金額の右端
        p.line(POS_ACTUAL_HOKUETSU*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_ACTUAL_HOKUETSU*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #概算の右端
        p.line(POS_PLAN_SANSHIN*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_PLAN_SANSHIN*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #支払方法の右端
        p.line(POS_ACTUAL_SANSHIN*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_ACTUAL_SANSHIN*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #振込先の右端
        p.line(POS_PLAN_SANSHIN_H*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_PLAN_SANSHIN_H*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #支払予定日の右端
        p.line(POS_ACTUAL_SANSHIN_H*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_ACTUAL_SANSHIN_H*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #三信(本店)の右端
        
        #p.line(POS_PLAN_CASH_P*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_PLAN_CASH_P*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #三信(本店)の右端
        #p.line(POS_ACTUAL_CASH_P*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_ACTUAL_CASH_P*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #三信(本店)の右端
        p.line(POS_PLAN_CASH_C*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_PLAN_CASH_C*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #三信(本店)の右端
        p.line(POS_ACTUAL_CASH_C*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_ACTUAL_CASH_C*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #三信(本店)の右端
        p.line(POS_PLAN_TOTAL_L*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_PLAN_TOTAL_L*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #三信(本店)の右端
        
        p.line(POS_RIGHT_SIDE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_RIGHT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) 
        p.line(POS_LEFT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm, POS_RIGHT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #横線
        #
        
        
        #小計・合計(最終行)
        #if i == lastday:
        if i == (lastday - 1):   
            #y += SEP_Y
            
            totalY = y + SEP_Y
            
            #金額小計
            #x = DETAIL_START_X + 42
            x = DETAIL_START_X - 3
            #p.drawString(x*mm, (y+SEP_Y)*mm, "合計")
            p.drawString(x*mm, totalY*mm, "合計")
            
            #支出金額合計(予定)
            x = POS_PLAN_EXPENSE - POS_ADJUST
            tmp_str = "￥" + str("{0:,d}".format(expected_expense_total))  #桁区切り
            p.drawRightString(x*mm, totalY*mm, tmp_str)
            
            #支出金額合計(予定)
            x = POS_EXPENSE - POS_ADJUST
            tmp_str = "￥" + str("{0:,d}".format(actual_expense_total))  #桁区切り
            p.drawRightString(x*mm, totalY*mm, tmp_str)
            
            #収入金額合計(予定)
            x = POS_PLAN_INCOME - POS_ADJUST
            tmp_str = "￥" + str("{0:,d}".format(expected_income_total))  #桁区切り
            p.drawRightString(x*mm, totalY*mm, tmp_str)
            
            #収入金額合計(実際)
            x = POS_INCOME - POS_ADJUST
            tmp_str = "￥" + str("{0:,d}".format(actual_income_total))  #桁区切り
            p.drawRightString(x*mm, totalY*mm, tmp_str)
            
            #北越合計(予定)
            x = POS_PLAN_HOKUETSU - POS_ADJUST
            tmp_str = "￥" + str("{0:,d}".format(expected_hokuetsu_total))  #桁区切り
            p.drawRightString(x*mm, totalY*mm, tmp_str)
            
            #北越合計(実際)
            x = POS_ACTUAL_HOKUETSU - POS_ADJUST
            tmp_str = "￥" + str("{0:,d}".format(actual_hokuetsu_total))  #桁区切り
            p.drawRightString(x*mm, totalY*mm, tmp_str)
            
            #三信塚野目合計(予定)
            x = POS_PLAN_SANSHIN - POS_ADJUST
            tmp_str = "￥" + str("{0:,d}".format(expected_sanshin_tsukanome_total))  #桁区切り
            p.drawRightString(x*mm, totalY*mm, tmp_str)
            
             #三信塚野目合計(実際)
            x = POS_ACTUAL_SANSHIN - POS_ADJUST
            tmp_str = "￥" + str("{0:,d}".format(actual_sanshin_tsukanome_total))  #桁区切り
            p.drawRightString(x*mm, totalY*mm, tmp_str)
            
            
            #三信本店合計(予定)
            x = POS_PLAN_SANSHIN_H - POS_ADJUST
            tmp_str = "￥" + str("{0:,d}".format(expected_sanshin_main_total))  #桁区切り
            p.drawRightString(x*mm, totalY*mm, tmp_str)
            
            #三信本店合計(実際)
            x = POS_ACTUAL_SANSHIN_H - POS_ADJUST
            tmp_str = "￥" + str("{0:,d}".format(actual_sanshin_main_total))  #桁区切り
            p.drawRightString(x*mm, totalY*mm, tmp_str)
            
            #現金社長(予定)
            #x = POS_PLAN_CASH_P - POS_ADJUST
            #tmp_str = "￥" + str("{0:,d}".format(expected_cash_president_total))  #桁区切り
            #p.drawRightString(x*mm, totalY*mm, tmp_str)
            
            #現金社長(実際)
            #x = POS_ACTUAL_CASH_P - POS_ADJUST
            #tmp_str = "￥" + str("{0:,d}".format(actual_cash_president_total))  #桁区切り
            #p.drawRightString(x*mm, totalY*mm, tmp_str)
            
            #現金会社(予定)
            x = POS_PLAN_CASH_C - POS_ADJUST
            tmp_str = "￥" + str("{0:,d}".format(expected_cash_company_total))  #桁区切り
            p.drawRightString(x*mm, totalY*mm, tmp_str)
            
            #現金会社(実際)
            x = POS_ACTUAL_CASH_C - POS_ADJUST
            tmp_str = "￥" + str("{0:,d}".format(actual_cash_company_total))  #桁区切り
            p.drawRightString(x*mm, totalY*mm, tmp_str)
            
            #総合計(予定)
            x = POS_PLAN_TOTAL_L - POS_ADJUST
            expected_total = expected_income_total - expected_expense_total
            tmp_str = "￥" + str("{0:,d}".format(expected_total))  #桁区切り
            p.drawRightString(x*mm, totalY*mm, tmp_str)
            
            #総合計(実際)
            x = POS_ACTUAL_TOTAL_L - POS_ADJUST
            actual_total = actual_income_total - actual_expense_total
            tmp_str = "￥" + str("{0:,d}".format(actual_total))  #桁区切り
            p.drawRightString(x*mm, totalY*mm, tmp_str)
            
            #x = DETAIL_START_X + POS_TOTAL_CHAR
            #p.setFillColorRGB(0,0,188) #色を指定
            #m = "￥" + str("{0:,d}".format(subtotal_amount))
            #p.drawRightString(x*mm, y*mm, m)
            
            #概算金額小計
            #if (payment.payment_method_id == (PAYMENT_METHOD_DIRECT_DEBIT)) or (payment.payment_method_id == (PAYMENT_METHOD_CACHE)):
            #x += POS_PLAN_ACTUAL_CHAR
            #p.setFillColorRGB(0.15686,0.639215,0.58039) #色を指定(ビリジャン)
            #m = "￥" + str("{0:,d}".format(subtotal_rough_estimate))
            #p.drawRightString(x*mm, y*mm, m)
            
            #subtotal_amount = 0
            #罫線をセット
            p.line(POS_LEFT_SIDE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_LEFT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) 
            p.line(POS_DATE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_DATE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #未の箇所の右端
            p.line(POS_WEEK*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_WEEK*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #未の箇所の右端
            p.line(POS_EXPENSE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_EXPENSE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #支払先の右端
            p.line(POS_PLAN_EXPENSE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_PLAN_EXPENSE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #支払先の右端
            p.line(POS_INCOME*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_INCOME*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #項目の右端
            p.line(POS_PLAN_INCOME*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_PLAN_INCOME*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #支払先の右端
            p.line(POS_PLAN_HOKUETSU*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_PLAN_HOKUETSU*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #金額の右端
            p.line(POS_ACTUAL_HOKUETSU*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_ACTUAL_HOKUETSU*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #概算の右端
            p.line(POS_PLAN_SANSHIN*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_PLAN_SANSHIN*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #支払方法の右端
            p.line(POS_ACTUAL_SANSHIN*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_ACTUAL_SANSHIN*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #振込先の右端
            p.line(POS_PLAN_SANSHIN_H*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_PLAN_SANSHIN_H*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #支払予定日の右端
            p.line(POS_ACTUAL_SANSHIN_H*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_ACTUAL_SANSHIN_H*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #さんしん（本店）の右端
            
            #p.line(POS_PLAN_CASH_P*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_PLAN_CASH_P*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #さんしん（本店）の右端
            #p.line(POS_ACTUAL_CASH_P*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_ACTUAL_CASH_P*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #さんしん（本店）の右端
            p.line(POS_PLAN_CASH_C*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_PLAN_CASH_C*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #さんしん（本店）の右端
            p.line(POS_ACTUAL_CASH_C*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_ACTUAL_CASH_C*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #さんしん（本店）の右端
            p.line(POS_PLAN_TOTAL_L*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_PLAN_TOTAL_L*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #さんしん（本店）の右端
            
            p.line(POS_RIGHT_SIDE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_RIGHT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) 
            p.line(POS_LEFT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm, POS_RIGHT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #横線
            #
    
            #金額合計
            y += SEP_Y #Yインクリメント
            x = DETAIL_START_X + 40.5
            #p.drawString(x*mm, y*mm, "合計")
            
            x = DETAIL_START_X + POS_TOTAL_CHAR
            p.setFillColorRGB(0,0,188) #色を指定
            m = "￥" + str("{0:,d}".format(total_amount))
            #p.drawRightString(x*mm, y*mm, m)
            
            #概算金額
            x += POS_PLAN_ACTUAL_CHAR
            p.setFillColorRGB(0.15686,0.639215,0.58039) #色を指定(ビリジャン)
            m = "￥" + str("{0:,d}".format(total_rough_estimate))
            #p.drawRightString(x*mm, y*mm, m)
            
            #subtotal_amount = 0
            #罫線をセット
            p.line(POS_LEFT_SIDE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_LEFT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) 
            p.line(POS_DATE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_DATE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #未の箇所の右端
            p.line(POS_WEEK*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_WEEK*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #未の箇所の右端
            p.line(POS_EXPENSE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_EXPENSE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #支払先の右端
            p.line(POS_PLAN_EXPENSE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_PLAN_EXPENSE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #支払先の右端
            p.line(POS_INCOME*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_INCOME*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #項目の右端
            p.line(POS_PLAN_INCOME*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_PLAN_INCOME*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #項目の右端
            p.line(POS_PLAN_HOKUETSU*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_PLAN_HOKUETSU*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #金額の右端
            p.line(POS_ACTUAL_HOKUETSU*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_ACTUAL_HOKUETSU*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #概算の右端
            p.line(POS_PLAN_SANSHIN*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_PLAN_SANSHIN*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #支払方法の右端
            p.line(POS_ACTUAL_SANSHIN*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_ACTUAL_SANSHIN*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #振込先の右端
            p.line(POS_PLAN_SANSHIN_H*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_PLAN_SANSHIN_H*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #支払予定日の右端
            p.line(POS_ACTUAL_SANSHIN_H*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_ACTUAL_SANSHIN_H*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #さんしん(本店)の右端
            
            #p.line(POS_PLAN_CASH_P*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_PLAN_CASH_P*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #さんしん(本店)の右端
            #p.line(POS_ACTUAL_CASH_P*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_ACTUAL_CASH_P*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #さんしん(本店)の右端
            p.line(POS_PLAN_CASH_C*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_PLAN_CASH_C*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #さんしん(本店)の右端
            p.line(POS_ACTUAL_CASH_C*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_ACTUAL_CASH_C*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #さんしん(本店)の右端
            p.line(POS_PLAN_TOTAL_L*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_PLAN_TOTAL_L*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #さんしん(本店)の右端
            
            p.line(POS_RIGHT_SIDE*mm, (y-POS_AJDUST_HEIGHT)*mm, POS_RIGHT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) 
            p.line(POS_LEFT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm, POS_RIGHT_SIDE*mm, ((y-POS_AJDUST_HEIGHT) + POS_DETAIL_HEIGHT)*mm) #横線
            #
            
            #概算集計方法の注釈
            #y += SEP_Y #Yインクリメント
            #p.setFillColorRGB(0,0,0)  #黒に戻す→概算と同じ色で
            #x = DETAIL_START_X -5
            #x = DETAIL_START_X + 122
            #message = "※概算の各計は、未払のものだけを集計しています。"
            #p.drawString(x*mm, y*mm, message)
            
        #Y座標インクリメント
        y += SEP_Y
    # PDF オブジェクトをきちんと閉じて終わり。
    p.showPage()
    p.save()
    return response


    
    
def set_title_normal(p,x,y):
#タイトル（ヘッダ部）出力(通常用)
   
    y = START_Y;
    
    #タイトル
    p.setFont(font_name, 14)
    
    deadline_string = ""   #締日検索の場合の文字
    
    #import pdb; pdb.set_trace()
    
    #if not cache.get('search_query_pay_month_from') and not cache.get('search_query_pay_month_from'):
    ##請求日で検索の場合
    #    deadline_string = "〆"
    
    #    tmp_date_from = cache.get('search_query_month_from')
    #    tmp_date_to = cache.get('search_query_month_to')
    #else:
    ##支払日で検索の場合
    #    tmp_date_from = cache.get('search_query_pay_month_from')
    #    tmp_date_to = cache.get('search_query_pay_month_to')
    
    multi_month = False
    
    #if tmp_date_from is not None:
    #    #◯◯◯◯年◯◯月〆の文字を作る
    #    tmp_year = tmp_date_from[0:4]
    #    tmp_month = tmp_date_from[5:7]
    #    
    #    if tmp_date_from != tmp_date_to:
    #        multi_month = True
        
        
    #    #if search_query_paid == False:
    #    if not search_query_paid:
    #        #if tmp_date_from == tmp_date_to:
    #        if multi_month == False:
    #        #単月の場合
    #            str_title = tmp_year + "年" + tmp_month + "月" + deadline_string + '　資金繰り表'
    #        else:
    #        #複数月の場合
    #            str_title = tmp_year + "年" + tmp_month + "月" + deadline_string
    #        p.drawString(HEADER_X*mm, HEADER_Y*mm, str_title)
        
    #        #月が複数指定の場合は、終了月も出力
    #        #if tmp_date_from != tmp_date_to:
    #        if multi_month == True:
    #            str_title = '資金繰り表'
    #            p.drawString((HEADER_X+35)*mm, (HEADER_Y+3)*mm, str_title)
                
    #            #◯◯◯◯年◯◯月〆の文字を作る
    #            tmp_year = tmp_date_to[0:4]
    #            tmp_month = tmp_date_to[5:7]
    #            str_title = "〜" + tmp_year + "年" + tmp_month + "月" + deadline_string 
    #            p.drawString((HEADER_X-5)*mm, (HEADER_Y+6)*mm, str_title)
    #    else:
    #        str_title = '資金繰り表'
    #        p.drawString((HEADER_X+15)*mm, HEADER_Y*mm, str_title)
        
    #else:
    #月指定してない場合
    str_title = '資金繰り表'
    p.drawString((HEADER_X)*mm, HEADER_Y*mm, str_title)
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
    
    #if multi_month == True:
    #    p.drawString((x-8)*mm, (y+2)*mm, '〆')
    
    p.drawString(x*mm, (y+4)*mm, '日付')
    
    x += 26
    p.drawString(x*mm, (y-0.5)*mm, '支出')
    
    tmpX = x - 8
    p.drawString(tmpX*mm, (y+5)*mm, '予定')
    tmpX += 17
    p.drawString(tmpX*mm, (y+5)*mm, '実際')
    
    #x += 25.5
    x += 35
    p.drawString(x*mm, (y-0.5)*mm, '収入')
    
    tmpX = x - 9
    p.drawString(tmpX*mm, (y+5)*mm, '予定')
    tmpX += 17
    p.drawString(tmpX*mm, (y+5)*mm, '実際')
    
    tmpX = x + 31
    p.drawString(tmpX*mm, (y+3.5)*mm, '北越銀行')
    tmpX -= 7
    p.drawString(tmpX*mm, (y+7.5)*mm, '予定')
    tmpX += 17
    p.drawString(tmpX*mm, (y+7.5)*mm, '実際')
    
    tmpX += 22
    p.drawString(tmpX*mm, (y+3.5)*mm, '三信(塚野目)')
    tmpX -= 4
    p.drawString(tmpX*mm, (y+7.5)*mm, '予定')
    tmpX += 17
    p.drawString(tmpX*mm, (y+7.5)*mm, '実際')
    
    tmpX += 22
    p.drawString(tmpX*mm, (y+3.5)*mm, '三信(本店)')
    tmpX -= 5
    p.drawString(tmpX*mm, (y+7.5)*mm, '予定')
    tmpX += 17
    p.drawString(tmpX*mm, (y+7.5)*mm, '実際')
    
    #tmpX += 22
    #p.drawString(tmpX*mm, (y+3.5)*mm, '現金(社長)')
    #tmpX -= 5
    #p.drawString(tmpX*mm, (y+7.5)*mm, '予定')
    #tmpX += 17
    #p.drawString(tmpX*mm, (y+7.5)*mm, '実際')
    
    tmpX += 22
    p.drawString(tmpX*mm, (y+3.5)*mm, '現金(会社)')
    tmpX -= 5
    p.drawString(tmpX*mm, (y+7.5)*mm, '予定')
    tmpX += 17
    p.drawString(tmpX*mm, (y+7.5)*mm, '実際')
    
    tmpX += 25
    p.drawString(tmpX*mm, (y+3.5)*mm, '合計')
    tmpX -= 8
    p.drawString(tmpX*mm, (y+7.5)*mm, '予定')
    tmpX += 17
    p.drawString(tmpX*mm, (y+7.5)*mm, '実際')
    
    #x += 15
    x += 118
    p.drawString(x*mm, (y-0.5)*mm, '残高')
    
    #x += 17
    #p.drawString(x*mm, (y+2)*mm, '概算')
    
    #x += 13
    #p.drawString(x*mm, (y+2)*mm, '支払方法')
    
    #x += 36
    #p.drawString(x*mm, (y+2)*mm, '振込先')
    
    #x += 37.5
    #p.drawString(x*mm, y*mm, '支払')
    #p.drawString((x-1)*mm, (y+3)*mm, '予定日')
    
    #x += 11.5
    #p.drawString(x*mm, (y+2)*mm, '支払日')
    
    #Y座標インクリメント
    #y += SEP_Y+3
    y += SEP_Y+7
    
    #ヘッダ部罫線
    p.rect(POS_LEFT_SIDE*mm, (START_Y-1)*mm, (POS_RIGHT_SIDE-POS_LEFT_SIDE)*mm, POS_HEADER_HEIGHT*mm, fill=0) #枠
    #p.line(x1,y1,x2,y2)
    p.line(POS_WEEK*mm, (START_Y-1)*mm, POS_WEEK*mm, ((START_Y-1) + POS_HEADER_HEIGHT)*mm) #日付の箇所の右端
    p.line(POS_PLAN_EXPENSE*mm, (START_Y+2.5)*mm, POS_PLAN_EXPENSE*mm, ((START_Y-1) + POS_HEADER_HEIGHT)*mm) #支払先の右端
    p.line(POS_EXPENSE*mm, (START_Y-1)*mm, POS_EXPENSE*mm, ((START_Y-1) + POS_HEADER_HEIGHT)*mm) #支払先の右端
    p.line(POS_PLAN_INCOME*mm, (START_Y+2.5)*mm, POS_PLAN_INCOME*mm, ((START_Y-1) + POS_HEADER_HEIGHT)*mm) #収入の右端
    p.line(POS_INCOME*mm, (START_Y-1)*mm, POS_INCOME*mm, ((START_Y-1) + POS_HEADER_HEIGHT)*mm) #収入の右端
    
    p.line(POS_PLAN_HOKUETSU*mm, (START_Y+6.5)*mm, POS_PLAN_HOKUETSU*mm, ((START_Y-1) + POS_HEADER_HEIGHT)*mm) #北越予定の右端
    p.line(POS_ACTUAL_HOKUETSU*mm, (START_Y+2.5)*mm, POS_ACTUAL_HOKUETSU*mm, ((START_Y-1) + POS_HEADER_HEIGHT)*mm) #北越実際の右端
    p.line(POS_PLAN_SANSHIN*mm, (START_Y+6.5)*mm, POS_PLAN_SANSHIN*mm, ((START_Y-1) + POS_HEADER_HEIGHT)*mm) #三信(塚野目)予定の右端
    p.line(POS_ACTUAL_SANSHIN*mm, (START_Y+2.5)*mm, POS_ACTUAL_SANSHIN*mm, ((START_Y-1) + POS_HEADER_HEIGHT)*mm) #振込先の右端
    p.line(POS_PLAN_SANSHIN_H*mm, (START_Y+6.5)*mm, POS_PLAN_SANSHIN_H*mm, ((START_Y-1) + POS_HEADER_HEIGHT)*mm) #三信(本店)予定の右端
    p.line(POS_ACTUAL_SANSHIN_H*mm, (START_Y+2.5)*mm, POS_ACTUAL_SANSHIN_H*mm, ((START_Y-1) + POS_HEADER_HEIGHT)*mm) #三信(本店)実際の右端
    #p.line(POS_PLAN_CASH_P*mm, (START_Y+6.5)*mm, POS_PLAN_CASH_P*mm, ((START_Y-1) + POS_HEADER_HEIGHT)*mm) #現金(社長)予定の右端
    #p.line(POS_ACTUAL_CASH_P*mm, (START_Y+2.5)*mm, POS_ACTUAL_CASH_P*mm, ((START_Y-1) + POS_HEADER_HEIGHT)*mm) #さんしん(本店)の右端
    p.line(POS_PLAN_CASH_C*mm, (START_Y+6.5)*mm, POS_PLAN_CASH_C*mm, ((START_Y-1) + POS_HEADER_HEIGHT)*mm) #現金(会社)予定の右端
    p.line(POS_ACTUAL_CASH_C*mm, (START_Y+2.5)*mm, POS_ACTUAL_CASH_C*mm, ((START_Y-1) + POS_HEADER_HEIGHT)*mm) #さんしん(本店)の右端
    p.line(POS_PLAN_TOTAL_L*mm, (START_Y+6.5)*mm, POS_PLAN_TOTAL_L*mm, ((START_Y-1) + POS_HEADER_HEIGHT)*mm) #合計(予定)の右端
    
    #横線
    p.line(POS_WEEK*mm, (START_Y+2.5)*mm, POS_RIGHT_SIDE*mm, (START_Y+2.5)*mm) #収入の右端
    p.line(POS_INCOME*mm, (START_Y+6.5)*mm, POS_RIGHT_SIDE*mm, (START_Y+6.5)*mm) #収入の右端
    #
    return p, x, y
    

def filter_month(end_year, end_month, lastday):
    results = None
    search_query_pay_month_from = None
    search_query_pay_month_to = None
    
    search_query_pay_month_from = cache.get('search_query_pay_month_from')
    
    #
    
    if search_query_pay_month_from:
        search_query_pay_month_from += "-01"
        
        #月末日で検索する
        end_year = int(search_query_pay_month_from[0:4])
        end_month = int(search_query_pay_month_from[5:7])
            
        _, lastday = calendar.monthrange(end_year,end_month)
    
    #import pdb; pdb.set_trace()
    
def filter():
#フィルタリング
    results = None
    
    #支払日検索用    add180911
    search_query_pay_month_from = None
    search_query_pay_month_to = None
    search_query_pay_month_from_saved = None
    search_flag_pay_day = False
    #
    search_query_month_from = None
    search_query_month_to = None
    global multi_month; multi_month = False
    
    global search_query_paid
    search_query_paid = cache.get('search_query_paid')
    
    #del190411
    #支払開始日の絞り込みは無しにする（あくまでも指定月以下で未払のものを検索）
    #支払開始月で抽出
    search_query_pay_month_from = cache.get('search_query_pay_month_from')
    if search_query_pay_month_from:
        search_flag_pay_day = True
        #◯月１日で検索するようにする
        search_query_pay_month_from_saved = search_query_pay_month_from
        search_query_pay_month_from += "-01"
        
                
        #test del 191216
            
        if search_query_paid and search_query_paid == "1":
            
            #支払済のものだけ検索した場合に、検索開始月のフィルターを有効にする
            if results == None:
                results = Payment.objects.all().filter(payment_due_date__gte=search_query_pay_month_from)
            else:
                results = results.filter(payment_due_date__gte=search_query_pay_month_from)
            
    #支払終了月で抽出
    search_query_pay_month_to = cache.get('search_query_pay_month_to')
    
    #import pdb; pdb.set_trace()
    
    if search_query_pay_month_to:
    
        search_flag_pay_day = True
    
        #import pdb; pdb.set_trace()
    
        #複数月で検索しているか判定
        #if search_query_pay_month_from_saved < search_query_pay_month_to:
        if (search_query_pay_month_from_saved == None) or (search_query_pay_month_from_saved < search_query_pay_month_to):
            multi_month = True
    
        #◯月１日で検索する
        #search_query_pay_month_to += "-01"
        #月末日で検索する
        end_year = int(search_query_pay_month_to[0:4])
        end_month = int(search_query_pay_month_to[5:7])
            
        _, lastday = calendar.monthrange(end_year,end_month)
        
        #◯月１日で検索するようにする
        #search_query_pay_month_to += "-01"
        #指定月末日で検索するようにする
        search_query_pay_month_to += "-" + str(lastday)
                
        if results == None:
            results = Payment.objects.all().filter(payment_due_date__lte=search_query_pay_month_to)
            #test 191216
            #results = Payment.objects.all().filter(payment_date__lte=search_query_pay_month_to)
        else:
            results = results.filter(payment_due_date__lte=search_query_pay_month_to)
            #test 191216
            #results = results.filter(payment_date__lte=search_query_pay_month_to)
     
        
     
    ##add end
        
    #請求開始月で抽出
    search_query_month_from = cache.get('search_query_month_from')
    if search_query_month_from:
        #◯月１日で検索するようにする
        search_query_month_from += "-01"
        if results == None:
            results = Payment.objects.all().filter(billing_year_month__gte=search_query_month_from)
        else:
            results = results.filter(billing_year_month__gte=search_query_month_from)
    #請求終了月で抽出
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
    
    #import pdb; pdb.set_trace()
    
    if search_query_payment:
        if results == None:
            results = Payment.objects.all().filter(payment_method_id=search_query_payment)
        else:
            results = results.filter(payment_method_id=search_query_payment)
     
    
    #global search_query_paid
    #search_query_paid = cache.get('search_query_paid')
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
                
    else:
        #add190412
        #支払済未選択の場合でも、支払日検索の場合は”未”の扱いとする
        #(社長仕様)
        if search_query_pay_month_from:
            search_flag = True
            if results is None:
                results = Payment.objects.all().filter(payment_date__isnull=True).order_by('order')
            else:
                results = results.filter(payment_date__isnull=True)
            
    if results is not None:
    #条件検索なら、並び順を設定
        if search_flag_pay_day == False:
        #請求日検索の場合
            if multi_month == False:
                results = results.order_by('payment_method_id', 'trade_division_id', 'order', 'id')
            else:
                results = results.order_by('payment_method_id', 'trade_division_id', 'partner_id', 'billing_year_month', 'order', 'id')
        else:
        #支払日検索の場合
            if multi_month == False:
            #単月
                results = results.order_by('payment_method_id', 'trade_division_id', 'payment_due_date', 'order', 'partner_id')
            else:
            #複数月
                results = results.order_by('payment_method_id', 'trade_division_id', 'partner_id', 'payment_due_date', 'order')
    else:
    #条件なしの場合
        results = Payment.objects.all()
    
    return results


