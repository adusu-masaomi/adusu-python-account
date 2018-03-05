from django.contrib import admin

from account.models import Partner

# Register your models here.
#admin.site.register(Partner)


class PartnerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'bank_name', 'branch_name', 'account_number',)  # 一覧に出したい項目
    list_display_links = ('id', 'name',)  # 修正リンクでクリックできる項目
admin.site.register(Partner, PartnerAdmin)
