from django.contrib import admin
from django.urls import path
from api.views import *
from api.views import RegisterViewSet,LogInViewSet,MobileOTPViewSet,SociallogInViewSet,forgetpassword,updatepassword,SubscriptionPlanViewSet,ProfileViewset, VerifyMobileRegView,ApplianceAPI,VerifyMobileView#ConfirmmobileView,
from rest_framework import routers
from rest_framework.routers import DefaultRouter
from . import views
from api.views import *

router = DefaultRouter()

router.register(r'register', RegisterViewSet, basename='register'),
router.register(r'verify-mobile-otp-reg', VerifyMobileRegView, basename='verify-mobile-otp-reg'),
router.register(r'mobile-otp', MobileOTPViewSet, basename='mobile-otp'),
router.register(r'profile', ProfileViewset, basename='profile'),
#router.register(r'mobile-otp-confirm', ConfirmmobileView, basename='mobile-otp-confirm'),
router.register(r'login', LogInViewSet, basename='login'),
router.register(r'social-login', SociallogInViewSet, basename='social-login'),
router.register(r'forgetpassword',forgetpassword,basename='forgetpassword')
router.register(r'verify-mobile-otp', VerifyMobileView, basename='verify-mobile-otp'),
router.register(r'forget-password-confirm',updatepassword,basename='forget-password-confirm')
router.register(r'change-family-head', ChangeFamilyHead, basename='change-family-head'),
router.register(r'subscriptionplan', SubscriptionPlanViewSet, basename='subscription-plan'),
router.register(r'payment', PaymentAPI, basename='payment')
router.register(r'handle_payment_success', handle_payment_successAPI, basename='handle_payment_successAPI')
router.register(r'location', LocationAPI, basename='location')
router.register(r'service_provider', Service_ProviderAPI, basename='service_provider')
router.register(r'appliance', ApplianceAPI, basename='appliance')
router.register(r'Subscription_Plan', Subscription_PlanAPI, basename='Subscription_Plan')
router.register(r'add-family-member', AddFamilyMember, basename='add-family-member')
router.register(r'task', TaskAPI, basename='task')
router.register(r'countries', CountryAPI, basename='countries')
router.register(r'states', StateAPI, basename='states')
router.register(r'cities', CityAPI, basename='cities')
# router.register(r'user', UserAPI, basename='user')
# router.register(r'file-upload',ExampleView, basename='file-upload')
# router.register(r'Permission', PermissionAPI, basename='Permission')
# router.register(r'Role', RoleAPI, basename='Role')
#router.register(r'User_Subscription',User_SubscriptionAPI, basename='User_Subscription')




urlpatterns = router.urls

urlpatterns +=[
    #path('add_member/' , views.add_member),    #add memeber user api
    #path('pay/', start_payment, name="payment"),
    #path('updateParent/<id>/' , views.updateParent),    #update parent user
    #path('send_otp/' , views.send_otp),    #send otp
    #path('Verify_OTP/' , views.Verify_OTP),    #verify otp
    path('util-relation/', views.util_relation),  # util by get
    path('util-service-type/', views.util_service_type),  # util by get
    path('util-applience-type/', views.util_applience_type),  # util by get
    #path('state/findById/<id>/', views.findById),     # get city by state id  # city-state api
    path('Pincode/', views.Pincode),     # location from pincode
    path('logout/', views.logout),    
    #path('findByFamilyIdlocation/<id>/', views.findByFamilyIdlocation),     # get location by family id  #location api
    path('fcm/<id>/', views.fcm),
    # path('forgot_password/', views.forgot_password), 
    # path('change_password/', views.change_password), 
    # path('pay/', views.start_payment, name="payment"),
    # path('payment/success/', views.handle_payment_success, name="payment_success")
    #path('service_provider/findByFamilyId/<id>/', views.findByFamilyId),     # get service_provider by family id  #service_provider api
]



# {
#     appliance : 0
#     service :1
#     location :1
# }