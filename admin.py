from django.contrib import admin

# Register your models here.
from api.models import *
# Register your models here.
admin.site.register(User)
admin.site.register(Family)
admin.site.register(OTPs)
admin.site.register(SmsAudit)
admin.site.register(Country)
admin.site.register(State)
admin.site.register(City)
admin.site.register(Location)
admin.site.register(Service_provider)
admin.site.register(Appliances)
admin.site.register(Scheduler)
admin.site.register(Task)
admin.site.register(Role)
admin.site.register(Payment)
admin.site.register(Subscription_Plan)
admin.site.register(User_Subscription)
admin.site.register(Permissions)
admin.site.register(Order)
