from django.contrib import admin
from accounts.models import User, Quiz, Pred, Transaction, DynamicCoins, DynamicLinks, Banners, CoinsPayment
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.utils.translation import gettext, gettext_lazy as _
from accounts.forms import UserForm
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# Register your models here.


# class UserAdmin(admin.ModelAdmin):
#     list_display = ('email','coins','contact_number','otp','spin_left','ref_code')
# admin.site.register(User, UserAdmin)

class UserAdmin(BaseUserAdmin):

    add_form = UserForm

    # Fields to display in the change list
    list_display = ('email','coins','contact_number','otp','spin_left','scratch','ref_code','full_name')
    
    # Fields to search by in the search bar
    search_fields = ('username', 'email', 'first_name', 'last_name')

    # Fields to show when creating a new user in the admin panel
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('full_name', 'email', 'password1', 'password2'),
        }),
    )

    # Fields to show when editing a user in the admin panel
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        (_('Personal Info'), {'fields': ('full_name','picture')}),
        (_('Details'),{'fields':('coins','contact_number','otp','spin_left','scratch','ref_code')}),
        (_('Timings'),{'fields':('last_login',)})
    )
admin.site.register(User, UserAdmin)


class QuizAdmin(admin.ModelAdmin):
    model = Quiz
    list_display = ('user','quiz_1','quiz_2','quiz_3','quiz_4','quiz_5')
admin.site.register(Quiz, QuizAdmin)


class PredAdmin(admin.ModelAdmin):
    model = Pred
    list_display = ('user','pred_1','pred_2','pred_3','pred_4','pred_5')
admin.site.register(Pred, PredAdmin)


class TransactionAdmin(admin.ModelAdmin):
    model = Transaction
    list_display = ('user','contact_number','amount','payment_type','status','created_on','updated_on')
admin.site.register(Transaction, TransactionAdmin)


class DynamicCoinsAdmin(admin.ModelAdmin):
    model = DynamicCoins
    list_display = ('name','coins','time_in_seconds')
admin.site.register(DynamicCoins,DynamicCoinsAdmin)


class DynamicLinksAdmin(admin.ModelAdmin):
    model = DynamicLinks
    list_display = ('name','link')
admin.site.register(DynamicLinks, DynamicLinksAdmin)


class BannersAdmin(admin.ModelAdmin):
    model = Banners
    list_display = ('name','link','picture')
admin.site.register(Banners, BannersAdmin)

class CoinsPaymentAdmin(admin.ModelAdmin):
    model = CoinsPayment
    list_display = ('coins','funds')
admin.site.register(CoinsPayment, CoinsPaymentAdmin)