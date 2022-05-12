#主にグローバル変数用として利用する
#template側でsettings.pyの定数を使いたい場合に記述する

from django.conf import settings

def empty_mark_info(request):
    return {
        'EMPTY_MARK': settings.EMPTY_MARK
    }
def payment_method_transfer_info(request):
    return {
        'ID_PAYMENT_METHOD_TRANSFER': settings.ID_PAYMENT_METHOD_TRANSFER
    }
def payment_method_withdrawal_info(request):
    return {
        'ID_PAYMENT_METHOD_WITHDRAWAL': settings.ID_PAYMENT_METHOD_WITHDRAWAL
    }
def staff_president_info(request):
    return {
        'ID_STAFF_PRESIDENT': settings.ID_STAFF_PRESIDENT
    }
#add200131
def bank_sanshin_info(request):
    return {
        'ID_BANK_SANSHIN': settings.ID_BANK_SANSHIN
    }
    
def bank_branch_sanshin_main_info(request):
    return {
        'ID_BANK_BRANCH_SANSHIN_MAIN': settings.ID_BANK_BRANCH_SANSHIN_MAIN
    }
def bank_branch_sanshin_tsukanome_info(request):
    return {
        'ID_BANK_BRANCH_SANSHIN_TSUKANOME': settings.ID_BANK_BRANCH_SANSHIN_TSUKANOME
    }
#addend
