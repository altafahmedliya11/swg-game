from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter


router = DefaultRouter()

router.register('register', UserRegistrationView, basename="registration")
router.register('user/details', UserDetailsView, basename="user")
router.register('quiz/update', QuizView, basename="quiz")
router.register('pred/update', PredView, basename="pred")
router.register('quiz/reset', QuizResetView, basename="quiz-reset")
router.register('otp/verify', VerifyOTPView, basename='verify-otp')
router.register('resetpassword', ResetPassword, basename="reset-password")
router.register('coins/add', UserDetailsView, basename='add-coins')
router.register('user', LastLoginView, basename='last-login')
router.register('user/profile', ProfileUpdate, basename='update-profile')
router.register('spin-scratch/add', SpinScratchUpdate, basename='add-spin-scratch')
router.register('payment',PaymentView, basename = 'make-payment')
router.register('dynamic/coins',DynamicCoinsView, basename='dynamic-coins')
router.register('dynamic/links',DynamicLinksView, basename='dynamic-links')
router.register('dynamic/funds',CoinsPaymentView, basename='dynamic-links')
router.register('banners',BannersView, basename='Banners')
router.register('transactions',TransactionView, basename = 'show-payment')




urlpatterns = [
    path('api/', include(router.urls)),
    path('api/sendotp/', SendOtp.as_view(),name='sendotp'),
]



################################################################################

# 1. Should i convert the coins into money value or you will
# 2. Is there a maximum value of the coins to be added at a time
# 3. Which paymethod are we going to implement?
# 4. I will be need the credentials to share the otp