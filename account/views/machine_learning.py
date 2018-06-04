from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, HttpResponse, QueryDict

from account.models import Cash_Book
from account.models import Account_Title
from account.models import Staff

from django.conf import settings
from django.core.cache import cache
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from sklearn import cross_validation
from sklearn.svm import LinearSVC
from sklearn.externals import joblib
#import pickle

#出納帳--勘定科目の教師データ作成
def training_account_title(request):
    
    #デバッグ
    #import pdb; pdb.set_trace()
    
    #全取得するが、将来的には絞ったほうが（x年間位）よいかも？
    cash_books = Cash_Book.objects.all()
    
    contents = []
    
    for cash_book in cash_books:
        contents.append(cash_book.description_content)
    
    vect = TfidfVectorizer()
    vect.fit(contents)
    
    #Xへは摘要内容をセット
    X = vect.transform(contents)
    #yへは勘定科目コードをセット
    y = np.array(cash_books.values_list('account_title', flat=True))
    
    X_train = []
    y_train = []
    
    #数値に変換したデータをクロスバリデーションで学習データと検証データに分割
    test_size = 0.2
    try:
    # Your code that may throw an exception
        X_train, X_test, y_train, y_test = cross_validation.train_test_split(X, y, test_size=test_size)
    except Exception as e:
        print (str(e))
    
    #分割したデータを使って学習する（モデルとしてLinearSVC使用）
    clf = LinearSVC(C=120.0, random_state=42)
    clf.fit(X_train, y_train)
    clf.score(X_test, y_test)
    
    #学習結果を保存
    joblib.dump(vect, settings.DIR_VECT_CASH_BOOK)
    joblib.dump(clf, settings.DIR_CLF_CASH_BOOK)
    
    #再レンダリング（あまり必要ないかも・・・）
    cash_books = Cash_Book.objects.all().order_by('settlement_date', 'order')
    #検索フォーム用に勘定科目も取得 
    account_titles = Account_Title.objects.all().order_by('order')
    #検索フォーム用に社員も取得 
    staffs = Staff.objects.all()
    #キャッシュに保存された検索結果をセット
    balance = cache.get('balance')
    balance_president = cache.get('balance_president')
    balance_staff = cache.get('balance_staff')
    #
        
    return render(request,
                'account/cash_book_list.html',     # 使用するテンプレート
                {'cash_books': cash_books, 'account_titles': account_titles, 'staffs': staffs,
                 'balance': balance, 'balance_president': balance_president, 'balance_staff': balance_staff})     # テンプレートに渡すデータ
                 
    #return request
