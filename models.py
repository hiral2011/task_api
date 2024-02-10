
from django.db import models

# Create your models here.
from django.db import models
import uuid
from random import randint

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import PermissionsMixin 

GST = (("5","5"), ("12","12"), ("18","18"), ("28","28"))
DeductTyoe = (('Daily','Daily'),('Weekly','Weekly'),('Monthly','Monthly'),('Quarterly','Quarterly'),('Yearly','Yearly'))
# InsuranceType = (('General_Insurance','General_Insurance'),('Life_Insurance','Life_Insurance'))

class User(AbstractUser):
    # username = models.CharField(max_length=255,null=True,blank=True,default=0)
    user_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=255,null=True,blank=True)
    last_name = models.CharField(max_length=255,null=True,blank=True)
    # family_id = models.UUIDField('Family', default=uuid.uuid4, editable=False)
    mobile_number = models.CharField(max_length=12, null=True)
    full_name = models.CharField(max_length=255,null=True,blank=True)
    email = models.EmailField(max_length=255,unique=True,null=True)
    social_id = models.CharField(max_length=255,null=True,blank=True)
    profile_image  = models.TextField(null = True,blank=True)
    user_image = models.ImageField(upload_to='avatar', unique=False,null = True)
    social_type =models.CharField(max_length=255,null=True,blank=True)
    # fcm_token =models.CharField(max_length=255,null=False,blank=False)
    device_info =models.CharField(max_length=255,null=True,blank=True)
    date_of_birth = models.DateField(null=True,blank=True)
    gender  = models.CharField(max_length=7,null=True,blank=True)
    counter = models.IntegerField(default=0, blank=True)
    relation = models.CharField(max_length=255,null=True,blank=True,default='self')
    alternative_mobile_number = models.CharField(max_length=255,null=True,blank=True)
    alternative_email = models.EmailField(null=True,blank=True)
    is_email_verified = models.BooleanField(default=False)
    is_mobile_verified = models.BooleanField(default=False)
    is_social_login = models.BooleanField(default=False,null = True,blank=True)
    is_deleted = models.BooleanField(default=False)
    is_profile_completed = models.BooleanField(default=False,null = True,blank=True)
    reference_id = models.UUIDField(max_length=255,unique=True,default = uuid.uuid4,)
    token_id = models.CharField(max_length=255,null=True,blank=True)
    ref_code = models.CharField(max_length=255,null=True,blank=True)
    country_code = models.CharField(max_length=20,null=True,default="+91")
    created_at=models.DateTimeField(auto_now_add=True,null=True)
    updated_at=models.DateTimeField(auto_now_add=True,null=True)
    deleted_at = models.DateTimeField(auto_now_add=True,null=True)
    created_by=models.ForeignKey("User",related_name='created_by_user',on_delete=models.CASCADE,null=True)
    updated_by=models.ForeignKey("User",related_name='updated_by_user',on_delete=models.CASCADE,null=True)
    deleted_by = models.ForeignKey("User",related_name='deleted_by_user',on_delete=models.CASCADE,null=True)
  
    # USERNAME_FIELD = 'mobile_number'

    def save(self, *args, **kwargs):
        if not self.username:
            is_unique = False
            while not is_unique:
                id = randint(10000000, 20000000)  # 19 digits: 1, random 18 digits
                if not User.objects.filter(user_id=id).exists():
                    is_unique = True
            self.username = id
        super(User, self).save()
        
    def __str__(self):
        return str(self.mobile_number)



 
class Family(models.Model):
    family_id = models.AutoField(primary_key=True)
    user_id = models.ManyToManyField(User,related_name="families", null=True, blank=True)
    # role_id = models.ForeignKey("Role",on_delete=models.CASCADE,null=True)
    family_head = models.OneToOneField(User, null=True, on_delete=models.CASCADE,related_name='family_head_user_family')
    # user_permission = models.ForeignKey("Permissions",on_delete=models.CASCADE,null=True)
    relation = models.CharField(max_length=250,null=True,blank=True)
   

    def __str__(self):
        return f"{self.family_id}"



class OTPs(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    otp = models.CharField(max_length=15, null=True)
    created = models.DateTimeField(auto_now_add=True, null=True)
    
    # def __str__(self):
    #     return self.user.first_name

class SmsAudit(models.Model):
    sms_audit_id = models.AutoField(primary_key=True)
    fast2sms_account_id = models.CharField(max_length=255, null=True)
    fast2sms_sms_id = models.CharField(max_length=255,null=True)
    status = models.CharField(max_length=255)
    detail = models.TextField()
    body = models.TextField()
    purpose = models.TextField()
    from_number = models.CharField(max_length=25, null=True)
    to_number = models.CharField(max_length=255, null=True)
    fast2sms_date = models.DateTimeField()
    

    def __str__(self):
        return f"{self.sms_audit_id}"

class Country(models.Model):
    country_id = models.AutoField(primary_key=True)
    country_name = models.CharField(max_length=255,null=True,blank=True)
    country_code = models.CharField(max_length=100,unique=True)
    
    
    def __str__(self):
        return self.country_name

class State(models.Model):
    state_id = models.AutoField(primary_key=True)
    country_id = models.ForeignKey('Country',on_delete=models.CASCADE)
    state_name = models.CharField(max_length=255,null=True,blank=True)
    
    
    def __str__(self):
        return self.state_name

class City(models.Model):
    city_id = models.AutoField(primary_key=True)
    country_id = models.ForeignKey(Country,on_delete=models.CASCADE)
    state_id = models.ForeignKey(State,on_delete=models.CASCADE)
    city_name = models.CharField(max_length=255,null=True,blank=True)
    area_name = models.CharField(max_length=255,null=True,blank=True)
    pincode = models.CharField(max_length=50,unique=True,null=True,blank=True)
    
    def __str__(self):
        return self.city_name

class Location(models.Model):
    location_id = models.AutoField(primary_key=True)
    location_name = models.CharField(max_length=255,null=True)
    family_id = models.ForeignKey(Family,on_delete=models.CASCADE,null=True)
    address = models.CharField(max_length=255,null=True)
    state_id = models.ForeignKey(State,on_delete=models.CASCADE,null=True)
    city_id = models.ForeignKey(City,on_delete=models.CASCADE,null=True)
    latitude = models.CharField(max_length=255,null=True)
    longitude = models.CharField(max_length=255,null=True)
    longitude = models.CharField(max_length=255,null=True)
    active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_by=models.ForeignKey("User",related_name='location_created_by_user',on_delete=models.CASCADE,null=True)
    updated_by=models.ForeignKey("User",related_name='location_updated_by_user',on_delete=models.CASCADE,null=True)
    deleted_by = models.ForeignKey("User",related_name='location_deleted_by_user',on_delete=models.CASCADE,null=True)
    
    def __str__(self):
        return self.location_name


class Service_provider(models.Model):
    service_provider_id = models.AutoField(primary_key=True)
    service_provider_name = models.CharField(max_length=255,null=True,blank=True)
    mobile_number = models.CharField(max_length=12,unique=True)
    country_code = models.CharField(max_length=20,null=True,default="+91")
    service_type = models.CharField(max_length=255,null=True,blank=True)
    family_id = models.ForeignKey(Family,on_delete=models.CASCADE,null=True)
    active = models.BooleanField(default=True)
    location_id = models.ForeignKey(Location,on_delete=models.CASCADE,null=True)
    email_id = models.EmailField(unique=True)
    alternative_mobile_number = models.CharField(max_length=12,null=True)
    tag = models.CharField(max_length=255,null=True,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True,null=True,blank=True)
    updated_at=models.DateTimeField(auto_now_add=True,null=True,blank=True)
    deleted_at = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    created_by=models.ForeignKey("User",related_name='created_by_user_service_provider',on_delete=models.CASCADE,null=True)
    updated_by=models.ForeignKey("User",related_name='updated_by_user_service_provider',on_delete=models.CASCADE,null=True)
    deleted_by = models.ForeignKey("User",related_name='deleted_by_user_service_provider',on_delete=models.CASCADE,null=True)
    
    def __str__(self):
        return self.service_provider_name

class Appliances(models.Model):
    appliance_id = models.AutoField(primary_key=True)
    family_id = models.ForeignKey('Family',on_delete=models.CASCADE,null=True)
    location_id = models.ForeignKey('Location',on_delete=models.CASCADE,null=True)
    appliance_type = models.CharField(max_length=255,null=True,blank=True)
    bought_from = models.CharField(max_length=255,null=True,blank=True)
    appliance_name = models.CharField(max_length=255,null=True,blank=True)
    mobile_number = models.CharField(max_length=12,null = True)
    country_code = models.CharField(max_length=20,null=True,default="+91")
    alternativ_mobile_number = models.CharField(max_length=255,null=True)
    price = models.FloatField()
    invoice_number = models.CharField(max_length=255,null=True)
    invoice_date = models.DateTimeField(auto_now_add=True)
    billing_email = models.EmailField(null=True, blank=True)
    billing_name = models.CharField(max_length=255,null=True)
    billing_mobile_number = models.CharField(max_length=12)
    warranty_last_date = models.CharField(max_length=255,null=True)
    product_image = models.FileField(default="product/default.png",null=True)
    warranty_pdf = models.FileField(default="product/default.png",null=True)
    guarantee_pdf = models.FileField(default="product/default.png",null=True)
    is_amc_service_available = models.BooleanField(null = True)
    company_name = models.CharField(max_length=255,null=True)
    contact_person_name = models.CharField(max_length=255,null=True)
    amc_phone_number = models.CharField(max_length=255,null=True)
    support_email = models.CharField(max_length=255,null=True)
    amc_service_address = models.CharField(max_length=255,null=True)
    service_time_period = models.CharField(max_length=255,null=True)
    service_provider_id = models.ForeignKey("Service_provider",on_delete=models.CASCADE,null=True)
    appliance_note = models.CharField(max_length=255,null=True)
    upload_invoice_pdf_img = models.FileField(default="product/default.png",null=True)
    active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True,null=True)
    updated_at=models.DateTimeField(auto_now_add=True,null=True)
    deleted_at = models.DateTimeField(auto_now_add=True,null=True)
    created_by=models.ForeignKey("User",related_name='created_by_user_appliance',on_delete=models.CASCADE,null=True)
    updated_by=models.ForeignKey("User",related_name='updated_by_user_appliance',on_delete=models.CASCADE,null=True)
    deleted_by = models.ForeignKey("User",related_name='deleted_by_user_appliance',on_delete=models.CASCADE,null=True)
    
    # def __str__(self):
    #     return self.appliance_name

class Scheduler(models.Model):
    scheduler_id = models.AutoField(primary_key=True)
    scheduler_time = models.CharField(null = True,blank=True,max_length=255)
    scheduler_title = models.CharField(null = True,blank=True,max_length=255)
    scheduler_body = models.CharField(null = True,blank=True,max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return f"{self.scheduler_id}"

class Task(models.Model):
    task_id = models.AutoField(primary_key=True)
    task_name = models.CharField(max_length=255,null=True)
    assagned_member_id = models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    family_id = models.ForeignKey(Family,on_delete=models.CASCADE,null=True)
    #scheduler_id = models.ForeignKey(Scheduler,on_delete=models.CASCADE,null=True)
    service_provider_id = models.ForeignKey(Service_provider,on_delete=models.CASCADE,null=True)
    start_datetime = models.DateTimeField(auto_now_add=True)
    end_datetime = models.DateTimeField(auto_now_add=False,null=True)
    task_description = models.CharField(max_length=255,null=True)
    location_id = models.ForeignKey(Location,on_delete=models.CASCADE,null=True)
    task_attechments = models.FileField(null = True)
    active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True,null=True)
    updated_at=models.DateTimeField(auto_now_add=True,null=True)
    deleted_at = models.DateTimeField(auto_now_add=True,null=True)
    created_by=models.ForeignKey("User",related_name='created_by_user_task',on_delete=models.CASCADE,null=True)
    updated_by=models.ForeignKey("User",related_name='updated_by_user_task',on_delete=models.CASCADE,null=True)
    deleted_by = models.ForeignKey("User",related_name='deleted_by_user_task',on_delete=models.CASCADE,null=True)
    
    def __str__(self):
        return self.task_name



    

class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    amount = models.FloatField(default=False)
    charge_id_or_reference_id = models.CharField(max_length=100,null=True)
    user_id = models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    payment_status = models.BooleanField()
    

    def __str__(self):
       return f"{self.payment_id}"

class Order(models.Model):
    data = models.JSONField(null=True)
    order_amount = models.FloatField(default=0)

    # def __str__(self):
    #     return self.data


class Subscription_Plan(models.Model):
    subscription_plan_id = models.AutoField(primary_key=True)
    duration_days = models.IntegerField(null=True)
    subscription_plan_name =  models.CharField(max_length=255,null=True)
    price = models.FloatField()
    max_num_of_location = models.CharField(max_length=12,null=True)
    max_num_of_appliance = models.CharField(max_length=12,null=True)
    max_num_of_services = models.CharField(max_length=12,null=True)
    max_num_of_family_member = models.CharField(max_length=12,null=True)
    

    def __str__(self):
        return self.subscription_plan_name


class User_Subscription(models.Model):
    user_subscription_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    subscription_plan_id = models.ForeignKey(Subscription_Plan,on_delete=models.CASCADE,null=True)
    family_id = models.ForeignKey(Family,on_delete=models.CASCADE,null=True)
    price = models.FloatField()
    payment_id = models.ForeignKey(Payment,on_delete=models.CASCADE,null=True)
    expiry_date = models.DateTimeField(auto_now_add=False,null=True)
    start_date = models.DateTimeField(auto_now_add=False,null=True)
    max_num_of_location = models.CharField(max_length=12,null=True)
    max_num_of_appliance = models.CharField(max_length=12,null=True)
    max_num_of_services = models.CharField(max_length=12,null=True)
    max_num_of_family_member = models.CharField(max_length=12,null=True)
    
    
    def __str__(self):
        return f"{self.user_subscription_id}"

class Role(models.Model):
    role_id = models.AutoField(primary_key=True)
    role_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    # user_permission = models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True,null=True)
    updated_at=models.DateTimeField(auto_now_add=True,null=True)
    # deleted_at = models.DateTimeField(auto_now_add=True,null=True)
    # created_by=models.ForeignKey("User",related_name='created_by_user_role',on_delete=models.CASCADE,null=True)
    # updated_by=models.ForeignKey("User",related_name='updated_by_user_role',on_delete=models.CASCADE,null=True)
    # deleted_by = models.ForeignKey("User",related_name='deleted_by_user_role',on_delete=models.CASCADE,null=True)

    def __str__(self):
       return self.role_name
       
class Permissions(models.Model):
    permission_id = models.AutoField(primary_key=True)
    permission= models.JSONField()
    role = models.ForeignKey(Role,on_delete=models.CASCADE,null=True) # member 
    user_id = models.ForeignKey(User,on_delete=models.CASCADE, blank=True, null=True) #hiral
    family_id = models.ForeignKey(Family, on_delete=models.CASCADE,null=True) # abc


    def __str__(self):
        return f"{self.permission_id}"

class Schedule(models.Model):
    task = models.ForeignKey(Task,related_name='Task_Schedule',null=True,blank=True,on_delete=models.CASCADE)
    time = models.TimeField(null = True,blank=True,max_length=255)
    title = models.CharField(null = True,blank=True,max_length=255)
    body = models.CharField(null = True,blank=True,max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
class NotificationHistory(models.Model):
    user = models.ForeignKey(User,related_name='end_user',null=True,blank=True,on_delete=models.CASCADE)
    task = models.ForeignKey(Task,related_name='task_history',null=True,blank=True,on_delete=models.CASCADE)
    message = models.TextField(null =True )
    type = models.CharField(null=True,blank=True,max_length=255)
    mode = models.CharField(null=True,blank=True,max_length=255)
    click = models.CharField(null=True,blank=True,max_length=255)
    is_delivered = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True,null=True)
# from rest_framework import permissions

# class RolePermission(permissions.BasePermission):
#     def has_permission(self, request, view):
#         # Get the user's role
#         user_role = request.user.role
#         # Check if the user is allowed to access the resource
#         allowed_roles = view.get_allowed_roles()
#         return user_role in allowed_roles

#  {
#     appliance :0 
#     service :1
#     location :1
# }