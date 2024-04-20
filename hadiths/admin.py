from django.contrib import admin
from django.db.models import Sum
from .models import User, ProfileHadithSource

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'get_total_hadiths_read')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # Annotate the queryset with the sum of Hadiths read by each user across all sources
        queryset = queryset.annotate(
            total_hadiths_read=Sum('profilehadithsource__hadiths_read_number')
        )
        return queryset

    def get_total_hadiths_read(self, obj):
        return obj.total_hadiths_read or 0
    get_total_hadiths_read.short_description = 'Total Hadiths Read'

admin.site.register(User, UserAdmin)
