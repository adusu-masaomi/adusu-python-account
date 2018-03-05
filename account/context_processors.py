#主にグローバル変数用として利用する
from django.conf import settings

def empty_mark_info(request):
    return {
        'EMPTY_MARK': settings.EMPTY_MARK
    }