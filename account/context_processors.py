#主にグローバル変数用として利用する
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