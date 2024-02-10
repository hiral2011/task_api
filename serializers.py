from django.forms import ValidationError
from rest_framework import serializers
from api.models import *
from rest_framework.authtoken.models import Token
# from rest_framework_timedelta.fields import TimedeltaField
from api.create_token import create_token



class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('mobile_number','country_code')
        # extra_kwargs = {'first_name': {'required': True},'email': {'required': True},'password': {'required': True},'mobile_number': {'required': True}}
        extra_kwargs = {"mobile_number": {'required': True,"error_messages": {"blank": "Mobile Number is required field."}},"country_code": {'required': True,"error_messages": {"blank": "country_code is required field."}}}
    def validate(self, data): 
        if not data['mobile_number'].isdigit():
            message = {"numeric": "Mobile number field must have numeric values."}
            raise serializers.ValidationError(message)
        return data

class OTPLoginSerializer(serializers.Serializer):
    mobile_number = serializers.CharField(required=True)
    otp = serializers.CharField(required=True)

class OTPLoginSocialSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)
    otp = serializers.CharField(required=True)

class MobileconfirmSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('mobile_number',)
        extra_kwargs = {"mobile_number": {'required': True,"error_messages": {"blank": "Mobile Number is required field."}},"country_code": {'required': True,"error_messages": {"blank": "country_code is required field."}}}
    def validate(self, data): 
        if not data['mobile_number'].isdigit():
            message = {"numeric": "Mobile number field must have numeric values."}
            raise serializers.ValidationError(message)
        return data

class ProfileUpdateSerializer(serializers.ModelSerializer):
    def validate(self, data):
        if len(data['first_name']) <2 or len(data['first_name']) >=30:
            message = {"first_name": "Please enter a valid name between the 2 & 50 character range."}
            raise serializers.ValidationError(message)
        if not all((char.isalpha() or char==' ') for char in data['first_name']):
            message = {"albhabets": "The name field must contain alphabets only."}
            raise serializers.ValidationError(message)
        return data
    
    class Meta:
        model = User
        fields = ("user_id","first_name","last_name","mobile_number","country_code","email","password", "user_image")
        extra_kwargs = {"password": {'write_only': True,'required': True,"error_messages": {"blank": "Password is required field."}},}

class ProfileSocialUpdateSerializer(serializers.ModelSerializer):
    def validate(self, data):
        if len(data['first_name']) <2 or len(data['first_name']) >=30:
            message = {"first_name": "Please enter a valid name between the 2 & 50 character range."}
            raise serializers.ValidationError(message)
        if not all((char.isalpha() or char==' ') for char in data['first_name']):
            message = {"albhabets": "The name field must contain alphabets only."}
            raise serializers.ValidationError(message)
        return data

    class Meta:
        model = User
        fields = ("user_id","first_name","last_name","mobile_number","country_code","password","is_social_login","social_id","social_type","profile_image",'gender','is_mobile_verified','is_email_verified','user_image')
        extra_kwargs = {"password": {'write_only': True,'required': True,"error_messages": {"blank": "Password is required field."}},"mobile_number": {'required': True,"error_messages": {"blank": "Mobile Number is required field."}},"country_code": {'required': True,"error_messages": {"blank": "country_code is required field."}}}

class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('mobile_number','country_code','password')

class SocialLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email','password')
class ProfileSerializer(serializers.ModelSerializer):
    #token =  serializers.SerializerMethodField()
    
    # def get_token(self,data):
    #     return create_token(data)
    
    class Meta:
        model = User
    fields = ("user_id","email","first_name","last_name","device_info","profile_image","user_image","is_social_login","is_profile_completed","social_id","social_type","profile_image","mobile_number","country_code",'gender','is_mobile_verified','is_email_verified')


class ProfileTokenSerializer(serializers.ModelSerializer):
    token =  serializers.SerializerMethodField()
    
    def get_token(self,data):
        return create_token(data)
    
    class Meta:
        model = User
        fields = ("user_id","email","first_name","last_name","token","device_info","profile_image","user_image","is_social_login","is_profile_completed","social_id","social_type","profile_image","mobile_number","country_code",'gender','is_mobile_verified','is_email_verified')

class Add_Family_Serializer(serializers.ModelSerializer):
  
    class Meta:
        model = Location
        fields = "__all__"
        extra_kwargs = {"mobile_number": {'required': True,"error_messages": {"blank": "Mobile Number is required field."}},"country_code": {'required': True,"error_messages": {"blank": "country_code is required field."}}}
    
class Family_Serializer(serializers.ModelSerializer):
   class Meta:
        model = Family
        fields = "__all__"
        depth = 1
        
class Location_Serializer(serializers.ModelSerializer):
    pincode = serializers.SerializerMethodField()

    def get_pincode(self, data):
        try:
            print("=========================",type(data))
            print(data.city_id.pincode)

            return data.city_id.pincode
        except:
            return None
    class Meta:
        model = Location
        fields =  ['location_id','location_name','family_id','address','state_id','city_id','latitude','longitude','active','is_deleted', 'created_by', 'pincode']
  
class Country_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = "__all__"

class State_Serializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = "__all__"

class City_Serializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = "__all__"
        depth = 1
class Service_provider_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Service_provider
        fields =  ['service_provider_id','service_provider_name','mobile_number','service_type','family_id','active','location_id','email_id','alternative_mobile_number','tag','is_deleted','created_at','updated_at','deleted_at','created_by','updated_by','deleted_by']
        depth = 1

class Appliances_Serializer(serializers.ModelSerializer):
    #location_id = serializers.PrimaryKeyRelatedField(queryset=Location.objects.get(location_id=id), source='location')
    #location_id = serializers.SerializerMethodField()
    #location_id = Location_Serializer(many=True, read_only=True)
    # def get_location(self, obj):
    #      qs = Location.objects.get(location_id = obj)
    #      return qs
    # def get_location(self,obj):
    #     qs = Location.objects.filter(location_id = obj)
    #     return Location_Serializer(qs).data
    class Meta:
        model = Appliances
        #fields = '__all__'
        fields =  ['appliance_id','service_provider_id','family_id','location_id','appliance_type','bought_from','appliance_name','mobile_number','alternativ_mobile_number','price','invoice_number','invoice_date','billing_email','billing_name','billing_mobile_number','warranty_last_date','product_image','warranty_pdf','guarantee_pdf','is_amc_service_available','company_name','contact_person_name','amc_phone_number','support_email','amc_service_address','service_time_period','service_provider_id','appliance_note','upload_invoice_pdf_img','active','is_deleted','created_at','updated_at','deleted_at','created_by','updated_by','deleted_by']
        depth = 1
class Task_serializers(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"

class Role_serializers(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = "__all__"

class Payment_serializers(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription_Plan
        fields = "__all__"

class User_Subscription_serializers(serializers.ModelSerializer):
    class Meta:
        model = User_Subscription
        fields = "__all__"

class Permissions_serializers(serializers.ModelSerializer):
    class Meta:
        model = Permissions
        fields = "__all__"

class FCMserializers(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"

# class ExampleSerializer(serializers.ModelSerializer):
#     duration = TimedeltaField()


# class SMSSerializer(serializers.Serializer):
#     api_key = serializers.CharField()
#     message = serializers.CharField()
#     recipients = serializers.ListField()