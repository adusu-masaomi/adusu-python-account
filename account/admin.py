from django.contrib import admin

from account.models import Partner

#add220826
from django.contrib.auth import get_user_model

# Register your models here.
#admin.site.register(Partner)


class PartnerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'bank_name', 'branch_name', 'account_number',)  # 一覧に出したい項目
    list_display_links = ('id', 'name',)  # 修正リンクでクリックできる項目
admin.site.register(Partner, PartnerAdmin)

#add220826
#admin.site.unregister(get_user_model())
admin.site.register(get_user_model())