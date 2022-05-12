from django.forms import ModelForm
from account.models import Partner
from account.models import Account_Title
from account.models import Bank
from account.models import Bank_Branch
from account.models import Payment
from account.models import Payment_Reserve
from account.models import Cash_Book
from account.models import Cash_Book_Weekly
from account.models import Cash_Flow_Header
from account.models import Balance_Sheet

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Div, Button, ButtonHolder, Fieldset, Field
#from django.contrib.admin import widgets  
from django.forms import DateTimeField
from datetimewidget.widgets import DateTimeWidget
#from django.core.cache import cache

#from django.core.urlresolvers import reverse

class PartnerForm(forms.ModelForm):
    """取引先のフォーム"""
    class Meta:
        model = Partner
        fields = ('administrative_name', 'name', 'trade_division_id', 'account_title', 'fixed_content_id', 'fixed_cost', 'rough_estimate', 'payment_method_id', 
                  'source_bank', 'source_bank_branch', 'bank', 'bank_branch', 'account_type', 'account_number', 'pay_day', 'pay_day_division',
                  'pay_month_flag_1', 'pay_month_flag_2', 'pay_month_flag_3', 'pay_month_flag_4', 'pay_month_flag_5', 'pay_month_flag_6',
                  'pay_month_flag_7', 'pay_month_flag_8', 'pay_month_flag_9', 'pay_month_flag_10', 'pay_month_flag_11', 'pay_month_flag_12',  )

    def __init__(self, *args, **kwargs):
        super(PartnerForm, self).__init__(*args, **kwargs) # Call to ModelForm constructor
        
        #取引先名(管理用)
        self.fields['administrative_name'].widget.attrs['tabindex'] = 0
        #取引先名
        self.fields['name'].widget.attrs['tabindex'] = 1
        #取引区分
        self.fields['trade_division_id'].widget.attrs['style'] = 'width:150px; height:40px;'
        self.fields['trade_division_id'].widget.attrs['tabindex'] = 2
        
        #支払科目
        self.fields['account_title'].widget.attrs['style'] = 'width:150px; height:40px;'
        self.fields['account_title'].widget.attrs['id'] = 'account_title_select'
        self.fields['account_title'].queryset = self.fields['account_title'].queryset.order_by('order')  #select2をオーダー順にする
        self.fields['account_title'].widget.attrs['tabindex'] = 3
        
        #固定項目フラグ
        self.fields['fixed_content_id'].widget.attrs['tabindex'] = 4
        #概算
        self.fields['rough_estimate'].widget.attrs['tabindex'] = 5
        #固定費
        self.fields['fixed_cost'].widget.attrs['tabindex'] = 6
        #支払方法
        self.fields['payment_method_id'].widget.attrs['style'] = 'width:150px; height:40px;'
        self.fields['payment_method_id'].widget.attrs['tabindex'] = 7
        
        #振込・振替元銀行(select2)
        self.fields['source_bank'].widget.attrs['style'] = 'width:160px; height:40px;'
        self.fields['source_bank'].widget.attrs['id'] = 'source_bank_select'
        self.fields['source_bank'].queryset = self.fields['source_bank'].queryset.order_by('order')  #select2をオーダー順にする
        self.fields['source_bank'].widget.attrs['tabindex'] = 8
        
        #add200120
        #振込・振替元銀行支店(select2)
        self.fields['source_bank_branch'].widget.attrs['style'] = 'width:200px; height:40px;'
        self.fields['source_bank_branch'].widget.attrs['id'] = 'source_bank_branch_select'
        self.fields['source_bank_branch'].queryset = self.fields['source_bank_branch'].queryset.order_by('order')  #select2をオーダー順にする
        self.fields['source_bank_branch'].widget.attrs['tabindex'] = 9
        
        #銀行(select2)
        self.fields['bank'].widget.attrs['style'] = 'width:160px; height:40px;'
        self.fields['bank'].widget.attrs['id'] = 'bank_select'
        self.fields['bank'].queryset = self.fields['bank'].queryset.order_by('order')  #select2をオーダー順にする
        self.fields['bank'].widget.attrs['tabindex'] = 10
        #支店(select2)
        self.fields['bank_branch'].widget.attrs['style'] = 'width:200px; height:40px;'
        self.fields['bank_branch'].widget.attrs['id'] = 'bank_branch_select'
        self.fields['bank_branch'].queryset = self.fields['bank_branch'].queryset.order_by('order')  #select2をオーダー順にする
        self.fields['bank_branch'].widget.attrs['tabindex'] = 11
        #口座種別
        self.fields['account_type'].widget.attrs['style'] = 'width:70px; height:40px;'
        self.fields['account_type'].widget.attrs['tabindex'] = 12
        #口座番号
        self.fields['account_number'].widget.attrs['tabindex'] = 13
        
        #支払日
        self.fields['pay_day'].widget.attrs['style'] = 'width:70px; height:40px;'
        self.fields['pay_day'].widget.attrs['tabindex'] = 14
        
        #支払フラグ
        self.fields['pay_day_division'].widget.attrs['style'] = 'width:150px; height:40px;'
        self.fields['pay_day_division'].widget.attrs['tabindex'] = 15
        #self.fields['payment_method_id'].required = False
        
		#ここは機能するが・・
        #my_field_text= [
        #    # (field_name, Field title label, Detailed field description)
        #    ('pay_month_flag_1', '１月', ''),
        #    ('pay_month_flag_2', '２月', ''),
        #]
        #for x in my_field_text:
        #    self.fields[x[0]].label=x[1]
        #    self.fields[x[0]].help_text=x[2]
        ####
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = 'submit_survey'
        #self.helper.field_class = 'form-control'
        #self.helper.add_input(Submit('submit', 'x'))

        self.helper.layout = Layout(
            Div(
                 Div('administrative_name'),
                 Div('name'),
                 Div('trade_division_id'),
                 Div('account_title'),
                 Div('fixed_content_id'),
                 Div('rough_estimate'),
                 Div('fixed_cost'),
                 Div('payment_method_id'),
                 Div('source_bank', css_class='col-md-3', style='margin-left:-15px;'),
                 Div('source_bank_branch'),
                 Div('bank', css_class='col-md-3', style='margin-left:-15px;'),
                 Div('bank_branch'),
                 Div('account_type'),
                 Div('account_number'),
                 Div('pay_day'),
                 Div('pay_day_division'),
                 Div('pay_month_flag_1',css_class='checkbox-inline'),
                 Div('pay_month_flag_2',css_class='checkbox-inline'),
                 Div('pay_month_flag_3',css_class='checkbox-inline'),
                 Div('pay_month_flag_4',css_class='checkbox-inline'),
                 Div('pay_month_flag_5',css_class='checkbox-inline'),
                 Div('pay_month_flag_6',css_class='checkbox-inline'),
                 Div('pay_month_flag_7',css_class='checkbox-inline'),
                 Div('pay_month_flag_8',css_class='checkbox-inline'),
                 Div('pay_month_flag_9',css_class='checkbox-inline'),
                 Div('pay_month_flag_10',css_class='checkbox-inline'),
                 Div('pay_month_flag_11',css_class='checkbox-inline'),
                 Div('pay_month_flag_12',css_class='checkbox-inline'),
                 ButtonHolder(
                   Submit('submit', '登録', css_class='button white')
                 ),
                  css_class='row col-xs-9',
                 
                ),
            
        )
        
        
       
        
class Account_TitleForm(ModelForm):
    """勘定科目のフォーム"""
    class Meta:
        model = Account_Title
        fields = ('name', 'trade_division_id', )
    def __init__(self, *args, **kwargs):
        super(Account_TitleForm, self).__init__(*args, **kwargs) # Call to ModelForm constructor
        self.fields['trade_division_id'].widget.attrs['style'] = 'width:150px; height:40px;'
class BankForm(ModelForm):
    """銀行のフォーム"""
    class Meta:
        model = Bank
        fields = ('name', )
    def __init__(self, *args, **kwargs):
        super(BankForm, self).__init__(*args, **kwargs) # Call to ModelForm constructor
        self.fields['name'].widget.attrs['style'] = 'width:450px; height:40px;'


class Bank_BranchForm(forms.ModelForm):
    """銀行支店のフォーム"""
    class Meta:
        model = Bank_Branch
        fields = ('bank','name', )
        
    def __init__(self, *args, **kwargs):
        super(Bank_BranchForm, self).__init__(*args, **kwargs) # Call to ModelForm constructor
        self.fields['bank'].widget.attrs['id'] = 'select2_1'
        self.fields['bank'].widget.attrs['style'] = 'width:150px; height:40px;'
        self.fields['bank'].queryset = self.fields['bank'].queryset.order_by('order')  #select2をオーダー順にする
        
        self.fields['name'].widget.attrs['style'] = 'width:450px; height:40px;'


class PaymentForm(forms.ModelForm):
    """支払のフォーム"""
    
    billing_year_month = forms.DateField(label='請求〆年月', input_formats=['%Y-%m'])
    
    class Meta:
        model = Payment
        fields = ('billing_year_month', 'partner', 'trade_division_id','account_title', 
           'payment_method_id', 'source_bank', 'source_bank_branch', 'billing_amount', 'rough_estimate', 'payment_amount', 'commission', 
           'payment_due_date','payment_date','unpaid_amount','unpaid_date','note')
    
    def __init__(self, *args, **kwargs):
        super(PaymentForm, self).__init__(*args, **kwargs) # Call to ModelForm constructor
        
        
        #請求〆日(datepicker)
        self.fields['billing_year_month'].widget.attrs['tabindex'] = 0
        self.fields['billing_year_month'].widget = forms.DateInput(attrs={'class':'datepicker_1', 'id': 'billing_year_month_picker'})
        self.fields['billing_year_month'].widget.attrs['style'] = 'width:100px; height:40px;'
        
        #取引先(select2用)
        self.fields['partner'].widget.attrs['style'] = 'width:200px; height:40px;'
        self.fields['partner'].widget.attrs['id'] = 'partner_select'
        self.fields['partner'].queryset = self.fields['partner'].queryset.order_by('order')  #select2をオーダー順にする
        self.fields['partner'].widget.attrs['tabindex'] = 1
        
        #取引区分
        self.fields['trade_division_id'].widget.attrs['style'] = 'width:140px; height:40px;'
        self.fields['trade_division_id'].widget.attrs['tabindex'] = 2
        self.fields['trade_division_id'].widget.attrs['id'] = 'trade_division_id_select'
        
        
        #項目(select2用)
        self.fields['account_title'].widget.attrs['style'] = 'width:200px; height:40px;'
        self.fields['account_title'].widget.attrs['id'] = 'account_title_select'
        self.fields['account_title'].queryset = self.fields['account_title'].queryset.order_by('order')  #select2をオーダー順にする
        self.fields['account_title'].widget.attrs['tabindex'] = 3
        
        #支払方法
        self.fields['payment_method_id'].widget.attrs['id'] = 'payment_method_id'
        self.fields['payment_method_id'].widget.attrs['style'] = 'width:120px; height:40px;'
        
        #import pdb; pdb.set_trace()
        
        #self.fields['payment_method_id'].label_attrs['style'] = 'margin-left:-15px;'
        self.fields['payment_method_id'].widget.attrs['tabindex'] = 4
        
        #振込・振替元銀行(select2化 200120)
        self.fields['source_bank'].widget.attrs['id'] = 'payment_source_bank'
        self.fields['source_bank'].widget.attrs['style'] = 'width:160px; height:40px;'
        self.fields['source_bank'].queryset = self.fields['source_bank'].queryset.order_by('order')  #select2をオーダー順にする
        self.fields['source_bank'].widget.attrs['tabindex'] = 5
        
        #振込・振替元銀行支店(select2化 200120)
        self.fields['source_bank_branch'].widget.attrs['id'] = 'payment_source_bank_branch'
        self.fields['source_bank_branch'].widget.attrs['style'] = 'width:200px; height:40px;'
        self.fields['source_bank_branch'].queryset = self.fields['source_bank_branch'].queryset.order_by('order')  #select2をオーダー順にする
        self.fields['source_bank_branch'].widget.attrs['tabindex'] = 6
                
        #請求金額
        self.fields['billing_amount'].widget.attrs['id'] = 'billing_amount'
        self.fields['billing_amount'].widget.attrs['onchange'] = "setAmount();"
        self.fields['billing_amount'].widget.attrs['tabindex'] = 7
        
        #概算
        self.fields['rough_estimate'].widget.attrs['id'] = 'rough_estimate'
        self.fields['rough_estimate'].widget.attrs['tabindex'] = 8
       
        #支払金額
        self.fields['payment_amount'].label = '支払金額（請求と異なる場合のみ入力）'
        self.fields['payment_amount'].widget.attrs['id'] = 'payment_amount'
        self.fields['payment_amount'].widget.attrs['onchange'] = "setCommission();"
        self.fields['payment_amount'].widget.attrs['tabindex'] = 9
        
        #手数料
        self.fields['commission'].label = '手数料（発生した場合のみ入力）'
        self.fields['commission'].widget.attrs['id'] = 'commission'
        self.fields['commission'].widget.attrs['tabindex'] = 10
                
        #支払予定日(datepicker)
        self.fields['payment_due_date'].widget = forms.DateInput(attrs={'class':'datepicker_2', 'id': 'payment_due_date_picker'})
        self.fields['payment_due_date'].widget.attrs['style'] = 'width:120px; height:40px;'
        self.fields['payment_due_date'].widget.attrs['tabindex'] = 11
        
        #支払日(datepicker)
        self.fields['payment_date'].widget = forms.DateInput(attrs={'class':'datepicker_3', 'id': 'payment_date_picker'})
        self.fields['payment_date'].widget.attrs['style'] = 'width:120px; height:40px;'
        self.fields['payment_date'].widget.attrs['tabindex'] =  12
        
        #add200507
        #未払金額
        self.fields['unpaid_amount'].widget.attrs['id'] = 'unpaid_amount'
        #self.fields['unpayment_amount'].widget.attrs['onchange'] = "setAmount();"
        self.fields['unpaid_amount'].widget.attrs['tabindex'] = 13
        
        #未払支払日(datepicker)
        self.fields['unpaid_date'].widget = forms.DateInput(attrs={'class':'datepicker_3', 'id': 'unpaid_date_picker'})
        self.fields['unpaid_date'].widget.attrs['style'] = 'width:120px; height:40px;'
        self.fields['unpaid_date'].widget.attrs['tabindex'] =  14
        
        #備考
        self.fields['note'].widget.attrs['tabindex'] = 15
        
        #upd180418 フォーム揃える
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = 'submit_survey'
        
        self.helper.layout = Layout(
            Div(
                 Div('billing_year_month'),
                 Div('partner'),
                 Div('trade_division_id'),
                 Div('account_title'),
                 Div('payment_method_id', css_class='col-md-3', style='margin-left:-15px;' ),
                 Div('source_bank', css_class='col-md-3', style='margin-left:20px;' ),
                 Div('source_bank_branch'),
                 Div('billing_amount'),
                 Div('rough_estimate'),
                 Div('payment_amount'),
                 Div('commission'),
                 Div('payment_due_date'),
                 Div('payment_date'),
                 Div('unpaid_amount'),
                 Div('unpaid_date'),
                 Div('note'),
                 ButtonHolder(
                   Submit('submit', '登録', css_class='button white')
                 ),
                  css_class='row col-xs-9',
                 
                ),
            
        )

        #Div('pay_month_flag_12',css_class='checkbox-inline'),

class Payment_ReserveForm(forms.ModelForm):
    """支払予定(予約)のフォーム"""
    
    billing_year_month = forms.DateField(label='請求〆年月', input_formats=['%Y-%m'])
    
    class Meta:
        model = Payment_Reserve
        fields = ('billing_year_month', 'partner', 'trade_division_id','account_title', 
           'payment_method_id', 'source_bank', 'source_bank_branch', 'billing_amount', 'rough_estimate', 
           'payment_due_date')
    
    def __init__(self, *args, **kwargs):
        super(Payment_ReserveForm, self).__init__(*args, **kwargs) # Call to ModelForm constructor
        
        
        #請求〆日(datepicker)
        self.fields['billing_year_month'].widget.attrs['tabindex'] = 0
        self.fields['billing_year_month'].widget = forms.DateInput(attrs={'class':'datepicker_1', 'id': 'billing_year_month_picker'})
        self.fields['billing_year_month'].widget.attrs['style'] = 'width:100px; height:40px;'
        
        #取引先(select2用)
        self.fields['partner'].widget.attrs['style'] = 'width:200px; height:40px;'
        self.fields['partner'].widget.attrs['id'] = 'partner_select'
        self.fields['partner'].queryset = self.fields['partner'].queryset.order_by('order')  #select2をオーダー順にする
        self.fields['partner'].widget.attrs['tabindex'] = 1
        
        #取引区分
        self.fields['trade_division_id'].widget.attrs['style'] = 'width:140px; height:40px;'
        self.fields['trade_division_id'].widget.attrs['tabindex'] = 2
        self.fields['trade_division_id'].widget.attrs['id'] = 'trade_division_id_select'
        
        
        #項目(select2用)
        self.fields['account_title'].widget.attrs['style'] = 'width:200px; height:40px;'
        self.fields['account_title'].widget.attrs['id'] = 'account_title_select'
        self.fields['account_title'].queryset = self.fields['account_title'].queryset.order_by('order')  #select2をオーダー順にする
        self.fields['account_title'].widget.attrs['tabindex'] = 3
        
        #支払方法
        self.fields['payment_method_id'].widget.attrs['id'] = 'payment_method_id'
        self.fields['payment_method_id'].widget.attrs['style'] = 'width:120px; height:40px;'
        self.fields['payment_method_id'].widget.attrs['tabindex'] = 4
        
        #振込・振替元銀行(select2化)
        self.fields['source_bank'].widget.attrs['id'] = 'payment_source_bank'
        self.fields['source_bank'].widget.attrs['style'] = 'width:160px; height:40px;'
        self.fields['source_bank'].queryset = self.fields['source_bank'].queryset.order_by('order')  #select2をオーダー順にする
        self.fields['source_bank'].widget.attrs['tabindex'] = 5
        
        #振込・振替元銀行支店(select2化)
        self.fields['source_bank_branch'].widget.attrs['id'] = 'payment_source_bank_branch'
        self.fields['source_bank_branch'].widget.attrs['style'] = 'width:200px; height:40px;'
        self.fields['source_bank_branch'].queryset = self.fields['source_bank_branch'].queryset.order_by('order')  #select2をオーダー順にする
        self.fields['source_bank_branch'].widget.attrs['tabindex'] = 6
        
        
        #請求金額
        self.fields['billing_amount'].widget.attrs['id'] = 'billing_amount'
        self.fields['billing_amount'].widget.attrs['onchange'] = "setAmount();"
        self.fields['billing_amount'].widget.attrs['tabindex'] = 7
        
        #概算
        self.fields['rough_estimate'].widget.attrs['id'] = 'rough_estimate'
        self.fields['rough_estimate'].widget.attrs['tabindex'] = 8
       
        #支払金額
        #self.fields['payment_amount'].label = '支払金額（請求と異なる場合のみ入力）'
        #self.fields['payment_amount'].widget.attrs['id'] = 'payment_amount'
        #self.fields['payment_amount'].widget.attrs['onchange'] = "setCommission();"
        #self.fields['payment_amount'].widget.attrs['tabindex'] = 8
        
        #手数料
        #self.fields['commission'].label = '手数料（発生した場合のみ入力）'
        #self.fields['commission'].widget.attrs['id'] = 'commission'
        #self.fields['commission'].widget.attrs['tabindex'] = 9
                
        #支払予定日(datepicker)
        self.fields['payment_due_date'].widget = forms.DateInput(attrs={'class':'datepicker_2', 'id': 'payment_due_date_picker'})
        self.fields['payment_due_date'].widget.attrs['style'] = 'width:120px; height:40px;'
        self.fields['payment_due_date'].widget.attrs['tabindex'] = 9
        
        #支払日(datepicker)
        #self.fields['payment_date'].widget = forms.DateInput(attrs={'class':'datepicker_3', 'id': 'payment_date_picker'})
        #self.fields['payment_date'].widget.attrs['style'] = 'width:120px; height:40px;'
        #self.fields['payment_date'].widget.attrs['tabindex'] =  11
        
        #備考
        #self.fields['note'].widget.attrs['tabindex'] = 12
        
        #upd180418 フォーム揃える
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = 'submit_survey'
        
        self.helper.layout = Layout(
            Div(
                 Div('billing_year_month'),
                 Div('partner'),
                 Div('trade_division_id'),
                 Div('account_title'),
                 Div('payment_method_id', css_class='col-md-3', style='margin-left:-15px;' ),
                 Div('source_bank', css_class='col-md-3', style='margin-left:20px;' ),
                 Div('source_bank_branch' ),
                 Div('billing_amount'),
                 Div('rough_estimate'),
                 Div('commission'),
                 Div('payment_due_date'),
                 ButtonHolder(
                   Submit('submit', '登録', css_class='button white')
                 ),
                  css_class='row col-xs-9',
                 
                ),
            
        )

        #Div('pay_month_flag_12',css_class='checkbox-inline'),
        
class Cash_BookForm(forms.ModelForm):
    """現金出納帳のフォーム"""
    class Meta:
        model = Cash_Book
        fields = ('settlement_date', 'receipt_date', 'description_partner', 'description_content', 'account_title', 'staff', 
                  'purchase_order_code', 'reduced_tax_flag', 'incomes', 'expences', )
        
    def __init__(self, *args, **kwargs):
        super(Cash_BookForm, self).__init__(*args, **kwargs) # Call to ModelForm constructor
        
        #請求日(datepicker)
        #self.fields['settlement_date'].widget.attrs['tabindex'] = 0
        self.fields['settlement_date'].widget = forms.DateInput(attrs={'class':'datepicker', 'id': 'settlement_date_picker'})
        self.fields['settlement_date'].widget.attrs['style'] = 'width:100px; height:35px;'
        
        #領収日(datepicker)
        #self.fields['receipt_date'].widget.attrs['tabindex'] = 1
        self.fields['receipt_date'].widget = forms.DateInput(attrs={'class':'datepicker', 'id': 'receipt_date'})
        self.fields['receipt_date'].widget.attrs['style'] = 'width:100px; height:35px;'
        
        #適用（取引先）
        self.fields['description_partner'].widget.attrs['id'] = 'description_partner'
        self.fields['description_partner'].widget.attrs['style'] = 'width:430px; height:35px;'
        self.fields['description_partner'].widget.attrs['tabindex'] = 2
        
        #適用（取引内容）
        self.fields['description_content'].widget.attrs['id'] = 'description_content'
        self.fields['description_content'].widget.attrs['style'] = 'width:430px; height:35px;'
        self.fields['description_content'].widget.attrs['onchange'] = "predictAccountTitle();"
        self.fields['description_content'].widget.attrs['tabindex'] = 3
        
        #勘定科目
        self.fields['account_title'].widget.attrs['id'] = 'account_title'
        self.fields['account_title'].widget.attrs['style'] = 'width:430px; height:35px;'
        self.fields['account_title'].widget.attrs['tabindex'] = 4
        
        #社員
        self.fields['staff'].widget.attrs['style'] = 'width:150px; height:40px;'
        self.fields['staff'].widget.attrs['tabindex'] = 5
        self.fields['staff'].widget.attrs['id'] = 'staff'
        
        #注文コード
        self.fields['purchase_order_code'].widget.attrs['style'] = 'width:150px; height:40px;'
        self.fields['purchase_order_code'].widget.attrs['tabindex'] = 6
        self.fields['purchase_order_code'].widget.attrs['id'] = 'purchase_order_code'
        
        #add190824
        #軽減税率
        self.fields['reduced_tax_flag'].widget.attrs['style'] = 'width:150px; height:40px;'
        self.fields['reduced_tax_flag'].widget.attrs['tabindex'] = 7
        self.fields['reduced_tax_flag'].widget.attrs['id'] = 'reduced_tax_flag'
        
        #収入金額
        self.fields['incomes'].widget.attrs['id'] = 'incomes'
        self.fields['incomes'].widget.attrs['style'] = 'width:120px; height:35px;'
        self.fields['incomes'].widget.attrs['tabindex'] = 8
        
        #支払金額
        self.fields['expences'].widget.attrs['id'] = 'expences'
        self.fields['expences'].widget.attrs['style'] = 'width:120px; height:35px;'
        self.fields['expences'].widget.attrs['tabindex'] = 9
       

class Cash_Book_WeeklyForm(forms.ModelForm):
    """現金出納帳週末データのフォーム"""
    class Meta:
        model = Cash_Book_Weekly
        fields = ('computation_date', 'balance_president', 'balance_staff', 'balance', )
        
    def __init__(self, *args, **kwargs):
        super(Cash_Book_WeeklyForm, self).__init__(*args, **kwargs) # Call to ModelForm constructor
        
        #集計日(datepicker)
        self.fields['computation_date'].widget = forms.DateInput(attrs={'class':'datepicker', 'id': 'computation_date'})
        self.fields['computation_date'].widget.attrs['style'] = 'width:100px; height:35px;'
        self.fields['computation_date'].widget.attrs['tabindex'] = 0
        
        #残高（社長）
        self.fields['balance_president'].widget.attrs['tabindex'] = 1
        self.fields['balance_president'].widget.attrs['id'] = 'balance_president'
        self.fields['balance_president'].widget.attrs['style'] = 'width:100px;text-align:right;'
        self.fields['balance_president'].widget.attrs['onchange'] = "setTotalBalance();"
        
        #残高（社員）
        self.fields['balance_staff'].widget.attrs['tabindex'] = 2
        self.fields['balance_staff'].widget.attrs['id'] = 'balance_staff'
        self.fields['balance_staff'].widget.attrs['style'] = 'width:100px;text-align:right;'
        self.fields['balance_staff'].widget.attrs['onchange'] = "setTotalBalance();"
        
        #総残高
        self.fields['balance'].widget.attrs['tabindex'] = 3
        self.fields['balance'].widget.attrs['id'] = 'balance'
        self.fields['balance'].widget.attrs['style'] = 'width:100px;text-align:right;'

class Cash_Flow_HeaderForm(forms.ModelForm):
    """資金繰り表見出しのフォーム"""
    class Meta:
        model = Cash_Flow_Header
        fields = ('cash_flow_date','expected_expense', 'actual_expense', 'expected_income', 'actual_income',
                  'expected_hokuetsu', 'actual_hokuetsu', 'expected_sanshin_tsukanome', 'actual_sanshin_tsukanome', 
                  'expected_sanshin_main', 'actual_sanshin_main', 'expected_cash_president', 'actual_cash_president', 
                  'expected_cash_company', 'actual_cash_company')
        
    def __init__(self, *args, **kwargs):
        super(Cash_Flow_HeaderForm, self).__init__(*args, **kwargs) # Call to ModelForm constructor
        
        #日付
        self.fields['cash_flow_date'].widget.attrs['tabindex'] = 1
        self.fields['cash_flow_date'].widget.attrs['style'] = 'width:150px; height:40px;'
        self.fields['cash_flow_date'].widget.attrs['readonly'] = True  #読み取り専用とする
        
        #支出（予定）
        self.fields['expected_expense'].widget.attrs['tabindex'] = 2
        self.fields['expected_expense'].widget.attrs['style'] = 'width:150px; height:40px;'
        #支出（実際）
        self.fields['actual_expense'].widget.attrs['tabindex'] = 3
        self.fields['actual_expense'].widget.attrs['style'] = 'width:150px; height:40px;'
        #収入（予定）
        self.fields['expected_income'].widget.attrs['tabindex'] = 4
        self.fields['expected_income'].widget.attrs['style'] = 'width:150px; height:40px;'
        #収入（実際）
        self.fields['actual_income'].widget.attrs['tabindex'] = 5
        self.fields['actual_income'].widget.attrs['style'] = 'width:150px; height:40px;'
        #北越（予定）
        self.fields['expected_hokuetsu'].widget.attrs['tabindex'] = 6
        self.fields['expected_hokuetsu'].widget.attrs['style'] = 'width:150px; height:40px;'
        #北越（実際）
        self.fields['actual_hokuetsu'].widget.attrs['tabindex'] = 7
        self.fields['actual_hokuetsu'].widget.attrs['style'] = 'width:150px; height:40px;'
        #三信塚野目（予定）
        self.fields['expected_sanshin_tsukanome'].widget.attrs['tabindex'] = 8
        self.fields['expected_sanshin_tsukanome'].widget.attrs['style'] = 'width:150px; height:40px;'
        #三信塚野目（実際）
        self.fields['actual_sanshin_tsukanome'].widget.attrs['tabindex'] = 9
        self.fields['actual_sanshin_tsukanome'].widget.attrs['style'] = 'width:150px; height:40px;'
        #三信本店（予定）
        self.fields['expected_sanshin_main'].widget.attrs['tabindex'] = 10
        self.fields['expected_sanshin_main'].widget.attrs['style'] = 'width:150px; height:40px;'
        #三信本店（実際）
        self.fields['actual_sanshin_main'].widget.attrs['tabindex'] = 11
        self.fields['actual_sanshin_main'].widget.attrs['style'] = 'width:150px; height:40px;'
        #現金社長（予定）
        self.fields['expected_cash_president'].widget.attrs['tabindex'] = 12
        self.fields['expected_cash_president'].widget.attrs['style'] = 'width:150px; height:40px;'
        #現金社長（実際）
        self.fields['actual_cash_president'].widget.attrs['tabindex'] = 13
        self.fields['actual_cash_president'].widget.attrs['style'] = 'width:150px; height:40px;'
        #現金会社（予定）
        self.fields['expected_cash_company'].widget.attrs['tabindex'] = 14
        self.fields['expected_cash_company'].widget.attrs['style'] = 'width:150px; height:40px;'
        #現金会社（実際）
        self.fields['actual_cash_company'].widget.attrs['tabindex'] = 15
        self.fields['actual_cash_company'].widget.attrs['style'] = 'width:150px; height:40px;'
        
        #self.fields['bank'].widget.attrs['id'] = 'select2_1'
        #self.fields['bank'].widget.attrs['style'] = 'width:150px; height:40px;'
        #self.fields['bank'].queryset = self.fields['bank'].queryset.order_by('order')  #select2をオーダー順にする
        #self.fields['name'].widget.attrs['style'] = 'width:450px; height:40px;'

class Balance_SheetForm(forms.ModelForm):
    """貸借表のフォーム"""
    
    #accrual_date = forms.DateField(label='日付', input_formats=['%Y-%m'])
    
    class Meta:
        model = Balance_Sheet
        fields = ('accrual_date', 'borrow_lend_id', 'amount','bank_id', 
            'description')
    
    def __init__(self, *args, **kwargs):
        super(Balance_SheetForm, self).__init__(*args, **kwargs) # Call to ModelForm constructor
        
        
        #発生日(datepicker)
        self.fields['accrual_date'].widget.attrs['tabindex'] = 0
        self.fields['accrual_date'].widget = forms.DateInput(attrs={'class':'datepicker_1', 'id': 'accrual_date_picker'})
        self.fields['accrual_date'].widget.attrs['style'] = 'width:100px; height:40px;'
        
        #貸借区分
        self.fields['borrow_lend_id'].widget.attrs['style'] = 'width:140px; height:40px;'
        self.fields['borrow_lend_id'].widget.attrs['tabindex'] = 1
        self.fields['borrow_lend_id'].widget.attrs['id'] = 'borrow_lend_id_select'
        
        #金額
        self.fields['amount'].widget.attrs['id'] = 'amount'
        #self.fields['amount'].widget.attrs['onchange'] = "setAmount();"
        self.fields['amount'].widget.attrs['tabindex'] = 2
        
        #銀行ID
        self.fields['bank_id'].widget.attrs['id'] = 'amount'
        self.fields['bank_id'].widget.attrs['tabindex'] = 3
        
        #勘定科目ID
        #self.fields['account_id'].widget.attrs['id'] = 'amount'
        #self.fields['account_id'].widget.attrs['tabindex'] = 4        
        
        #摘要
        self.fields['description'].widget.attrs['id'] = 'amount'
        self.fields['description'].widget.attrs['tabindex'] = 5
        
        
        
        #取引先(select2用)
        #self.fields['partner'].widget.attrs['style'] = 'width:200px; height:40px;'
        #self.fields['partner'].widget.attrs['id'] = 'partner_select'
        #self.fields['partner'].queryset = self.fields['partner'].queryset.order_by('order')  #select2をオーダー順にする
        #self.fields['partner'].widget.attrs['tabindex'] = 1
        
        #取引区分
        #self.fields['trade_division_id'].widget.attrs['style'] = 'width:140px; height:40px;'
        #self.fields['trade_division_id'].widget.attrs['tabindex'] = 2
        #self.fields['trade_division_id'].widget.attrs['id'] = 'trade_division_id_select'
        
        
        #項目(select2用)
        #self.fields['account_title'].widget.attrs['style'] = 'width:200px; height:40px;'
        #self.fields['account_title'].widget.attrs['id'] = 'account_title_select'
        #self.fields['account_title'].queryset = self.fields['account_title'].queryset.order_by('order')  #select2をオーダー順にする
        #self.fields['account_title'].widget.attrs['tabindex'] = 3
        
        #支払方法
        #self.fields['payment_method_id'].widget.attrs['id'] = 'payment_method_id'
        #self.fields['payment_method_id'].widget.attrs['style'] = 'width:120px; height:40px;'
        #self.fields['payment_method_id'].widget.attrs['tabindex'] = 4
        
        #振込・振替元銀行(select2化)
        #self.fields['source_bank'].widget.attrs['id'] = 'payment_source_bank'
        #self.fields['source_bank'].widget.attrs['style'] = 'width:160px; height:40px;'
        #self.fields['source_bank'].queryset = self.fields['source_bank'].queryset.order_by('order')  #select2をオーダー順にする
        #self.fields['source_bank'].widget.attrs['tabindex'] = 5
        
        #振込・振替元銀行支店(select2化)
        #self.fields['source_bank_branch'].widget.attrs['id'] = 'payment_source_bank_branch'
        #self.fields['source_bank_branch'].widget.attrs['style'] = 'width:200px; height:40px;'
        #self.fields['source_bank_branch'].queryset = self.fields['source_bank_branch'].queryset.order_by('order')  #select2をオーダー順にする
        #self.fields['source_bank_branch'].widget.attrs['tabindex'] = 6
        
        
        #請求金額
        #self.fields['billing_amount'].widget.attrs['id'] = 'billing_amount'
        #self.fields['billing_amount'].widget.attrs['onchange'] = "setAmount();"
        #self.fields['billing_amount'].widget.attrs['tabindex'] = 7
        
        #概算
        #self.fields['rough_estimate'].widget.attrs['id'] = 'rough_estimate'
        #self.fields['rough_estimate'].widget.attrs['tabindex'] = 8
       
                
        #self.fields['payment_due_date'].widget = forms.DateInput(attrs={'class':'datepicker_2', 'id': 'payment_due_date_picker'})
        #self.fields['payment_due_date'].widget.attrs['style'] = 'width:120px; height:40px;'
        #self.fields['payment_due_date'].widget.attrs['tabindex'] = 9
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = 'submit_survey'
        
        self.helper.layout = Layout(
            Div(
                 Div('accrual_date'),
                 Div('borrow_lend_id'),
                 Div('amount'),
                 Div('bank_id'),
                 #Div('account_id'),
                 Div('description'),
                 
                 ButtonHolder(
                   Submit('submit', '登録', css_class='button white')
                 ),
                  css_class='row col-xs-9',
                 
                ),
            
        )




#ノーマルなサンプル
#class XXXForm(ModelForm):
#    """◯◯◯のフォーム"""
#    class Meta:
#        model = XXX
#        fields = ('??','??', )
#    def __init__(self, *args, **kwargs):
#        super(XXXForm, self).__init__(*args, **kwargs) # Call to ModelForm constructor
#        self.fields['???'].widget.attrs['style'] = 'width:150px; height:40px;'
#        self.fields['???'].widget.attrs['style'] = 'width:450px; height:40px;'
