import json
# from django.forms import ValidationError
from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from api.serializers import * #RegistrationSerializer, OTPLoginSerializer,ProfileUpdateSerializer #
from api.create_token import *
from api.models import *
from fcm_django.models import FCMDevice
from rest_framework.decorators import api_view,action 
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets,status
from rest_framework.response import Response

from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.authtoken.models import Token

from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from task_karo import settings

from task_karo.settings import RAZORPAY_API_KEY, RAZORPAY_API_SECRET

from .helpers import send_otp_to_phone
from  .models import User
from decouple import config
from rest_framework.views import APIView
import boto3 
from botocore.exceptions import NoCredentialsError
from firebase_admin.messaging import Message, Notification
from django.contrib.auth.hashers import make_password
from .mypaginations import MyLimitOffsetpagination
import random
import math
import requests
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)
from rest_framework import generics
import razorpay
from datetime import datetime 
from datetime import timedelta
import pytz
import requests, json, base64, pyotp #
import re
API_KEY = 'kBvuJbGq_D7uL' #
from datetime import date, timedelta #
from django.contrib.auth import authenticate #
from django.db.models import Q
# Create your views here.
   
class generateKey:
    @staticmethod
    def returnValue(mobile_number):
        return str(mobile_number) + str(datetime.date(datetime.now())) + "Some Random Secret Key"


class RegisterViewSet(viewsets.ModelViewSet):# Done
    queryset = User.objects.all()
    serializer_class = RegistrationSerializer
    http_method_names = ['post']

    def create(self, request, format=None):
        apikey =request.GET.get('apikey','test')
        if apikey.strip() == API_KEY.strip():
            #request = request
            mobile_number = request.data.get("mobile_number",None)
            country_code = request.data.get("country_code",None)
            ref_code=request.data.get("ref_code",None)
            if ref_code:
                print("+++++++++++++++++")
                
                user= User.objects.get(mobile_number = mobile_number,country_code=country_code,is_active = False)
                user.counter = user.counter + 1
                user.save()
                keygen = generateKey()
                key = base64.b32encode(keygen.returnValue(mobile_number).encode())
                OTP = pyotp.HOTP(key, digits = 4)
                otp = OTP.at(1)
                otp = '1234'
                user = OTPs.objects.create(user=user, otp=otp)
                data = {
                    'mobile_number':mobile_number,
                    'country_code': country_code,
                    'ref_code':ref_code
                }
                return Response({"status":1,"message":"OTP has been sent successfully on your mobile number.",'data':data})
                # except:
                #     pass
            try:
                user= User.objects.get(mobile_number = mobile_number,country_code=country_code,is_active = False).delete()
            except:
            
                
                serializer = RegistrationSerializer(data =request.data )
                
                if serializer.is_valid():
                    #print("<><><><><><><><><><><><><><><><><><><><><><><><><><><><>")
                    try:
                        user = User.objects.get(mobile_number = mobile_number,country_code=country_code,is_active = True)
                        return Response({"status":0,"message":"user already exists"},status = status.HTTP_406_NOT_ACCEPTABLE)
                    except:    
                        user = User.objects.create(mobile_number = mobile_number,country_code=country_code,ref_code=ref_code,is_active = False)
                        try:
                            otp = OTPs.objects.filter(user=user).delete()
                        except:
                            pass
                        user.counter = user.counter + 1
                        user.save()
                        keygen = generateKey()
                        key = base64.b32encode(keygen.returnValue(mobile_number).encode())
                        OTP = pyotp.HOTP(key, digits = 4)
                        otp = OTP.at(1)
                        otp = '1234'
                        user = OTPs.objects.create(user=user, otp=otp)
                        data = {
                            'mobile_number':mobile_number,
                            'country_code': country_code,
                            'ref_code':ref_code
                        }
                        return Response({"status":1,"message":"OTP has been sent successfully on your mobile number.",'data':data})
                else:
                    print(serializer.errors)
                    if "mobile_number" in serializer.errors:
                        return Response({"status":0,"message":serializer.errors['mobile_number'][0] },status = status.HTTP_406_NOT_ACCEPTABLE)
                    else:
                        return Response({"status":0,"message":"errors.","data":serializer.errors},status = status.HTTP_406_NOT_ACCEPTABLE)
        else:
            return Response({"status":0,"message":"invalid API key."},status = status.HTTP_401_UNAUTHORIZED)
    

class VerifyMobileRegView(viewsets.ModelViewSet): # Done
    queryset = User.objects.all()
    #permission_classes = (permissions.AllowAny,)
    serializer_class = OTPLoginSerializer
    http_method_names = ['post']
    def get_user(self,mobile_number,country_code):
        try:
            user = User.objects.get(mobile_number=mobile_number,country_code = country_code)
            return user
        except Exception as e:
            print(e)
            return 0
    admin_permission = {
        "appliance" :1 ,
        "service" :1,
        "location" :1,
        "service_provider":1,
        "task":1
    }
    def create(self, request, *args, **kwargs):
        apikey = request.GET.get('apikey','test')
        if apikey.strip() == API_KEY.strip():
            mobile_number = request.data.get("mobile_number",None)
            otp = request.data.get("otp",None)
            country_code = request.data.get("country_code",None)
            user = self.get_user(mobile_number,country_code)
            
            print("+++++++++++++++++++++",user)
            ref_code= request.data.get("ref_code",None)
            print("+++++++++++++++++++++",ref_code)
            if mobile_number and otp:
                print("+++++++++MObile and OTP++++++++++++",mobile_number)
                if not mobile_number.isdigit():
                    print("mobile number is not digit")
                    return Response({"status":0,"message":"mobile number field must have numeric values."},status = status.HTTP_406_NOT_ACCEPTABLE)
                if otp.isdigit():
                    print("otp is digit")
                    try:
                        #user = User.objects.get(mobile_number=mobile_number,country_code=country_code)
                        print("+++++++++MObile and OTP++++++++++++",user)
                        try:
                            uotp = OTPs.objects.get(user=user)
                            if int(uotp.otp) == int(otp):
                                user.is_active = True
                                user.is_mobile_verified = True
                                token = create_token(user)
                                user.save()
                                print("+++++++++user save++++++++++++",user)
                                if ref_code==None:
                                    print("ref_code is none Master registration")
                                    family=Family.objects.create(family_head=user,relation="self")
                                    print("^^^^^^^^^^^^^^^^^^^^^",family)
                                    permission = Permissions.objects.create(permission=self.admin_permission,role_id=1,user_id=user,family_id=family)
                                else :
                                    family=Family.objects.get(family_id=ref_code)
                                    permission = Permissions.objects.create(permission=self.admin_permission,role_id=2,user_id=user,family_id=family)
                                    family.user_id.add(user)
                                data = {
                                    'mobile_number':user.mobile_number,
                                    'token':token,
                                }
                                print("+++++++++data++++++++++++",data)
                                try:
                                    otp = OTPs.objects.filter(user=user).delete()
                                    print("+++++++++otp delete++++++++++++",otp)
                                except:
                                    pass
                                return Response({"status":1,"message":"user mobile verify successfully.","data":data})
                            else:
                                data = {
                                    'mobile_number': mobile_number,
                                    'otp': otp,
                                    'error': "OTP mismatch"
                                }
                                print("+++++++++data++++++++++++",data)
                                return Response({"status":0,"message":"you have entered incorrect OTP.","data":data},status = status.HTTP_406_NOT_ACCEPTABLE)

                        except OTPs.DoesNotExist:
                            data = {
                                'mobile_number': mobile_number,
                                'error': "it looks like we haven't sent you an OTP."
                                }
                            return Response({"status":0,"message":"it looks like we haven't sent you an OTP.","data":data},status = status.HTTP_406_NOT_ACCEPTABLE)

                    except User.DoesNotExist:
                        data = {
                            'mobile_number': mobile_number,
                            'error': "the user is not registered with us."
                            }
                        return Response({"status":0,"message":"the user is not registered with us.","data":data},status = status.HTTP_406_NOT_ACCEPTABLE)
                else:
                    data = {
                        'mobile_number': mobile_number,
                        'otp': otp,
                        'error': "please enter OTP in numeric."
                    }
                    return Response({"status":0,"message":"please enter OTP in numeric.","data":data},status = status.HTTP_406_NOT_ACCEPTABLE)
            else:
                if not mobile_number:
                    return Response({"status":0,"message":"please ensure mobile_number is required field"},status = status.HTTP_406_NOT_ACCEPTABLE)
                else:
                    return Response({"status":0,"message":"please ensure otp is required field"},status = status.HTTP_406_NOT_ACCEPTABLE)

        else:
            return Response({"status":0,"message":"invalid API key."},status = status.HTTP_401_UNAUTHORIZED)

class VerifyMobileView(viewsets.ModelViewSet): # Done
    queryset = User.objects.all()
    #permission_classes = (permissions.AllowAny,)
    serializer_class = OTPLoginSerializer
    http_method_names = ['post']
    def get_user(self,mobile_number,country_code):
        try:
            user = User.objects.get(mobile_number=mobile_number,country_code = country_code)
            return user
        except Exception as e:
            print(e)
            return 0
    admin_permission = {
        "appliance" :1 ,
        "service" :1,
        "location" :1,
        "service_provider":1,
        "task":1
    }   
    def create(self, request, *args, **kwargs):
        apikey =request.GET.get('apikey','test')
        if apikey.strip() == API_KEY.strip():
            mobile_number = request.data.get("mobile_number",None)
            otp = request.data.get("otp",None)
            country_code = request.data.get("country_code",None)
            ref_code= request.data.get("ref_code",None)
            user = self.get_user(mobile_number,country_code)
            if mobile_number and otp:
                if not mobile_number.isdigit():
                    return Response({"status":0,"message":"mobile number field must have numeric values."},status = status.HTTP_406_NOT_ACCEPTABLE)
                if otp.isdigit():
                    try:
                        #user = User.objects.get(mobile_number=mobile_number)
                        try:
                            uotp = OTPs.objects.get(user=user)
                            if int(uotp.otp) == int(otp):
                                user.is_active = True
                                user.is_mobile_verified = True
                                token = create_token(user)
                                user.save()
                                if ref_code==None:
                                    family=Family.objects.create(family_head=user,relation="self")
                                    permission = Permissions.objects.create(permission=self.admin_permission,role_id=1,user_id=user,family_id=family)
                                else :
                                    family=Family.objects.get(family_id=ref_code)
                                    permission = Permissions.objects.create(permission=self.admin_permission,role_id=2,user_id=user,family_id=family)
                                    family.user_id.add(user)
                                data = {
                                    'mobile_number':user.mobile_number,
                                    'token':token,
                                }
                                serializer = ProfileTokenSerializer(user)
                                try:
                                    otp = OTPs.objects.filter(user=user).delete()
                                except:
                                    pass
                                return Response({"status":1,"message":"user mobile verify successfully.","data":serializer.data})
                            else:
                                data = {
                                    'mobile_number': mobile_number,
                                    'otp': otp,
                                    'error': "OTP mismatch"
                                }
                                return Response({"status":0,"message":"you have entered incorrect OTP.","data":data},status = status.HTTP_406_NOT_ACCEPTABLE)

                        except OTPs.DoesNotExist:
                            data = {
                                'mobile_number': mobile_number,
                                'error': "it looks like we haven't sent you an OTP."
                                }
                            return Response({"status":0,"message":"it looks like we haven't sent you an OTP.","data":data},status = status.HTTP_406_NOT_ACCEPTABLE)

                    except User.DoesNotExist:
                        data = {
                            'mobile_number': mobile_number,
                            'error': "the user is not registered with us."
                            }
                        return Response({"status":0,"message":"the user is not registered with us.","data":data},status = status.HTTP_406_NOT_ACCEPTABLE)
                else:
                    data = {
                        'mobile_number': mobile_number,
                        'otp': otp,
                        'error': "please enter OTP in numeric."
                    }
                    return Response({"status":0,"message":"please enter OTP in numeric.","data":data},status = status.HTTP_406_NOT_ACCEPTABLE)
            else:
                if not mobile_number:
                    return Response({"status":0,"message":"please ensure mobile_number is required field"},status = status.HTTP_406_NOT_ACCEPTABLE)
                else:
                    return Response({"status":0,"message":"please ensure OTP is required field"},status = status.HTTP_406_NOT_ACCEPTABLE)

        else:
            return Response({"status":0,"message":"invalid API key."},status = status.HTTP_401_UNAUTHORIZED)

class ProfileViewset(viewsets.ModelViewSet):#Done
    queryset = User.objects.all()
    #serializer_class = ProfileUpdateSerializer
    http_method_names = ['get','post','put','delete']
    lookup_body_field = 'user_id'

    def list(self,request):
        apikey =request.GET.get('apikey','test')
        if apikey.strip() == API_KEY.strip():
            token = request.META.get("HTTP_AUTHORIZATION")
            user = decrypt_token(token)
            
            if user:
                serializer = ProfileSerializer(user)
                return Response({"status":1,"message":"user profile.","data":serializer.data},status = status.HTTP_200_OK)
            else:
                return Response({"status":0,"message":"invalid credentials"},status = status.HTTP_406_NOT_ACCEPTABLE)
        else:
            return Response({"status":0,"message":"invalid API key."},status = status.HTTP_401_UNAUTHORIZED)

    @action(methods=['put'], detail=False)
    def update_user(self,request, *args, **kwargs):
        apikey =request.GET.get('apikey','test')
        password =request.GET.get('password')
        if apikey.strip() == API_KEY.strip():
            token = request.META.get("HTTP_AUTHORIZATION")
            user = decrypt_token(token)
            if user:
                serializer = ProfileUpdateSerializer(user,data=request.data)
                if serializer.is_valid():
                    
                    password = make_password(request.data['password'])
                    serializer.save(password=password)
                    
                    return Response({"status":1,"message":"user profile updated successfully .","data":serializer.data})
                else:
                    if "albhabets" in serializer.errors:
                        return Response({"status":0,"message":serializer.errors['albhabets'][0]},status = status.HTTP_406_NOT_ACCEPTABLE)
                    if "first_name" in serializer.errors:
                        return Response({"status":0,"message":serializer.errors['first_name'][0]},status = status.HTTP_406_NOT_ACCEPTABLE)
                    if "last_name" in serializer.errors:
                        return Response({"status":0,"message":serializer.errors['last_name'][0]},status = status.HTTP_406_NOT_ACCEPTABLE)
            else:
                return Response({"status":0,"message":"invalid credentials"},status = status.HTTP_406_NOT_ACCEPTABLE)
        else:
            return Response({"status":0,"message":"invalid API key."},status = status.HTTP_401_UNAUTHORIZED)
    
        
    @action(methods=['put'], detail=False)
    def update_user_social(self,request, *args, **kwargs):
        apikey =request.GET.get('apikey','test')
        password =request.GET.get('password')

        if apikey.strip() == API_KEY.strip():
            token = request.META.get("HTTP_AUTHORIZATION")
            user = decrypt_token(token)
            if user:
                serializer = ProfileSocialUpdateSerializer(user,data=request.data)
                if serializer.is_valid():
                    user.counter = user.counter + 1
                    user.save()
                    keygen = generateKey()
                    key = base64.b32encode(keygen.returnValue(user.email).encode())
                    OTP = pyotp.HOTP(key, digits = 4)
                    otp = OTP.at(1)
                    otp = '1234'
                    user = OTPs.objects.create(user=user, otp=otp)
                    password = make_password(request.data['password'])
                    serializer.save(password=password)
                    # data = {
                    #     'mobile_number':mobile_number,
                    #     'country_code': country_code,
                    # }
                    return Response({"status":1,"message":"user profile updated OTP has been sent successfully on your mobile number.",'data':serializer.data},status = status.HTTP_200_OK)
            else:
                return Response({"status":0,"message":"user does not exist"},status = status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({"status":0,"message":"invalid API key."},status = status.HTTP_401_UNAUTHORIZED)
        
    @action(methods=['put'], detail=False)
    def update_user_profile(self,request, *args, **kwargs):
        apikey =request.GET.get('apikey','test')
        # password =request.GET.get('password')
        if apikey.strip() == API_KEY.strip():
            token = request.META.get("HTTP_AUTHORIZATION")
            user = decrypt_token(token)
            if user:
                serializer = ProfileTokenSerializer(user,data=request.data,partial=True)
                print(serializer)
                if serializer.is_valid():
                    
                    # password = make_password(request.data['password'])
                    # serializer.save(password=password)
                    serializer.save()
                    return Response({"status":1,"message":"user profile updated successfully .","data":serializer.data},status = status.HTTP_200_OK)
                else:
                    if "albhabets" in serializer.errors:
                        return Response({"status":0,"message":serializer.errors['albhabets'][0]},status = status.HTTP_406_NOT_ACCEPTABLE)
                    return Response({"status":0,"message":"errors.","data":serializer.errors},status = status.HTTP_406_NOT_ACCEPTABLE)
            else:
                return Response({"status":0,"message":"invalid credentials"},status = status.HTTP_406_NOT_ACCEPTABLE)
        else:
            return Response({"status":0,"message":"invalid API key."},status = status.HTTP_401_UNAUTHORIZED)
        
    @action(methods=['delete'], detail=False)
    def destroy_user(self,request, *args, **kwargs):
        token = request.META.get("HTTP_AUTHORIZATION")
        user = decrypt_token(token)
        print("$$$$$$$$$$$$$$$$$$$$$$$$$$",user)
        apikey =self.request.GET.get('apikey','test')
        if apikey.strip() == API_KEY.strip():
            family = Family.objects.filter(Q(user_id__in=[user])|Q(family_head=user)).values_list('user_id','family_head','relation').distinct().first()
            print("%%%%%%family%%%%%%%%",family)
            print("$$$$$$$$$$$$user.user_id$$$$$$$$$$$$$$",user.user_id)
            print("777777777777777",family[1])
            if user.user_id == family[1]:
                #Setting user inactive
                
                return Response({"status":0,"message":"family head can not delete first you change family head."})
                
                #devices = FCMDevice.objects.filter(user = user).delete()
                
            else:
                user.is_active=False
                user.save()
                return Response({"status":1,"message":"user deleted successfully."},status = status.HTTP_406_NOT_ACCEPTABLE)
        else:
            return Response({"status":0,"message":"invalid API key."},status = status.HTTP_401_UNAUTHORIZED)

class LogInViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = LoginSerializer
    http_method_names = ['post']

    def get_user(self,mobile_number,country_code):
        try:
            user = User.objects.get(mobile_number=mobile_number, country_code=country_code)
            return user
        except Exception as e:
            print(e)
            return 0
    def create(self,request):
        apikey =request.GET.get('apikey','test')
        udid =request.GET.get('udid',0)
        if apikey.strip() == API_KEY.strip():
            mobile_number = request.data['mobile_number']
            country_code = request.data['country_code']
            password = request.data['password']

            device_info = request.data.get('device_info',None)
            firebase_key = request.data.get('firebase_key',None)
            os = request.data.get('os',None)

            print(password)
            user = self.get_user(mobile_number,country_code)
            if user:
                if user.is_active:
                    if(FCMDevice.objects.filter(registration_id=firebase_key,type=os).exists()==True):
                        for item in FCMDevice.objects.filter(registration_id=firebase_key,type=os):
                            item.delete()
                    FCMDevice.objects.create(registration_id=firebase_key,type=os,user=user,device_id = device_info)
                    auth_status = authenticate(mobile_number=user.mobile_number,country_code=user.country_code,username = user.username,password=password)
                    if auth_status:
                        serializer = ProfileTokenSerializer(user)
                        return Response({"status":1,"message":"logged in successfully.","data":serializer.data})
                    else:
                        return Response({"status":0,"message":"invalid credentials"},status=status.HTTP_401_UNAUTHORIZED)
                else:
                    return Response({"status":0,"message":"user does not exist"},status = status.HTTP_401_UNAUTHORIZED)
            else:
                return Response({"status":0,"message":"user does not exist"},status = status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({"status":0,"message":"invalid API key."},status = status.HTTP_401_UNAUTHORIZED)
        

@api_view(['Get'])
def logout(request):
    token = request.META.get("HTTP_AUTHORIZATION")
    user = decrypt_token(token)
    if user:
        devices = FCMDevice.objects.filter(user=user).delete()
        # print(devices)
        return Response({"status": 1, "message": "successfully logged out"})

    else:
        return Response({"status": 0, "message": "invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

class MobileOTPViewSet(viewsets.ModelViewSet):#?????
    queryset = User.objects.all()
    serializer_class = RegistrationSerializer
    http_method_names = ['post']
    def create(self, request, format=None):
        apikey =request.GET.get('apikey','test')
        if apikey.strip() == API_KEY.strip():
            country_code = request.data.get("country_code",None)
            mobile_number =request.data.get("mobile_number",None)
            token = request.META.get("HTTP_AUTHORIZATION")
            user = decrypt_token(token)
            if user:
                if mobile_number:
                    if not mobile_number.isdigit():
                        message =  "mobile number field must have numeric values."
                        return Response({"status":0,"message":message},status = status.HTTP_406_NOT_ACCEPTABLE)
                    elif not country_code:
                        return Response({"status":0,"message":"country code is required field."},status = status.HTTP_406_NOT_ACCEPTABLE)

                    try:
                        otp = OTPs.objects.filter(user=user).delete()
                    except:
                        pass
                    user.counter = user.counter + 1
                    user.save()

                    keygen = generateKey()
                    key = base64.b32encode(keygen.returnValue(user.username).encode())
                    OTP = pyotp.HOTP(key, digits = 4)
                    otp = OTP.at(1)
                    print("+++++++++++++++++++++++++++++++++++++++++++++++++++",otp)
                    otp = '1234'
                    
                    user_otp = OTPs.objects.create(user=user, otp=otp)
                    data = {
                    #'name':user.first_name,
                    'mobile':mobile_number,
                    }
                    return Response({"status":1,"message":"OTP has been sent successfully on your mobile.",'data':data})
                else:
                    return Response({"status":0,"message":"please enter a valid mobile number id."},status = status.HTTP_406_NOT_ACCEPTABLE)
            else:
                return Response({"status":0,"message":"invalid credentials"},status = status.HTTP_406_NOT_ACCEPTABLE)     
        else:
            return Response({"status":0,"message":"invalid API key."},status = status.HTTP_401_UNAUTHORIZED) 
        

class SociallogInViewSet(viewsets.ModelViewSet):# Done 
    queryset = User.objects.all()
    serializer_class = LoginSerializer
    http_method_names = ['post']
    def get_user(self,email):
        try:
            user = User.objects.get(email=email)
            return user
        except:
            return 0
    def create(self,request):
        apikey =request.GET.get('apikey','test')
        #udid =request.GET.get('udid',0)
       
        if apikey.strip() == API_KEY.strip():
            email = request.data['email']
            first_name = request.data['first_name']
            last_name = request.data['last_name']
            #device_info = request.data['device_info',None]
            social_provider = request.data['social_type']
            social_provider_id = request.data['social_id']
            #profile_url = request.data['profile_url']
            ref=request.data.get("ref_code",None)
            user = self.get_user(email)

            device_info = request.data.get('device_info',None)
            firebase_key = request.data.get('firebase_key',None)
            os = request.data.get('os',None)
            ref_code= request.data.get("ref_code",None)
            if user:
                if user.is_active and user.is_social_login:
                    # #print('if')
                    # #token = create_token(user)
                    if(FCMDevice.objects.filter(registration_id=firebase_key,type=os).exists()==True):
                        for item in FCMDevice.objects.filter(registration_id=firebase_key,type=os):
                            item.delete()    
                    FCMDevice.objects.create(registration_id=firebase_key,type=os,user=user,device_id = device_info)
                    serializer = ProfileTokenSerializer(user)
                    return Response({"status":1,"message":"logged in successfully.","data":serializer.data})
                elif user.is_active and not user.is_social_login:

                    return Response({"status":0,"message":"you are already registed with us, please login with email id & password."},status = status.HTTP_406_NOT_ACCEPTABLE)
                else:
                    if user:
                        user.delete()
                    print('else')
                    user = User.objects.create(email=email,ref_code=ref, first_name=first_name,last_name=last_name, is_social_login=True, social_type=social_provider, social_id=social_provider_id, is_active = True,is_email_verified=True)
                    #token = create_token(user)
                    # if user.profile_url:
                    #     profile_url = user.profile_url
                    # else:
                    #     profile_url = user.avatar.url
                    if(FCMDevice.objects.filter(registration_id=firebase_key,type=os).exists()==True):
                        for item in FCMDevice.objects.filter(registration_id=firebase_key,type=os):
                            item.delete()    
                    FCMDevice.objects.create(registration_id=firebase_key,type=os,user=user,device_id = device_info)
                    
                    if ref_code==None:
                        family=Family.objects.create(family_head=user,relation="self")
                        permission = Permissions.objects.create(permission=self.admin_permission,role_id=1,user_id=user,family_id=family)
                    else :
                        family=Family.objects.get(family_id=ref_code)
                        permission = Permissions.objects.create(permission=self.admin_permission,role_id=2,user_id=user,family_id=family)
                        family.user_id.add(user)
                    
                    serializer = ProfileTokenSerializer(user)
                    return Response({"status":1,"message":"logged in successfully.","data":serializer.data})
                        #return Response({"status":0,"message":"Invalid Details"})
            else:
                print('if else')
                user = User.objects.create(email=email,ref_code=ref, first_name=first_name,last_name=last_name, is_social_login=True, social_type=social_provider, social_id=social_provider_id, is_active = True,is_email_verified=True)
                #token = create_token(user)
                # if user.profile_url:
                #     profile_url = user.profile_url
                # else:
                #     profile_url = user.avatar.url
                
                if(FCMDevice.objects.filter(registration_id=firebase_key,type=os).exists()==True):
                    for item in FCMDevice.objects.filter(registration_id=firebase_key,type=os):
                        item.delete()    
                FCMDevice.objects.create(registration_id=firebase_key,type=os,user=user,device_id = device_info)
                serializer = ProfileTokenSerializer(user)
                
                return Response({"status":1,"message":"logged in successfully.","data":serializer.data})
        else:
            return Response({"status":0,"message":"invalid API key."},status = status.HTTP_401_UNAUTHORIZED)
    
class forgetpassword(viewsets.ModelViewSet):
    queryset = User.objects.all()
    http_method_names = ['post']
    def get_user(self,mobile_number,country_code):
        try:
            user = User.objects.get(mobile_number=mobile_number,country_code = country_code)
            return user
        except:
            return 0
    def create(self,request):
        apikey =request.GET.get('apikey','test')
        udid =request.GET.get('udid',0)
        country_code = request.data.get("country_code",None)
        if apikey.strip() == API_KEY.strip():
            mobile_number = request.data.get('mobile_number',None)
            country_code = request.data.get("country_code",None)
            user = self.get_user(mobile_number,country_code)
            if mobile_number:
                if not country_code:
                    return Response({"status":0,"message":"please enter a valid country code."},status = status.HTTP_406_NOT_ACCEPTABLE)
            
            if user:
                
                try:
                    otp = OTPs.objects.filter(user=user).delete()
                except:
                    pass
                user.counter = user.counter + 1
                user.save()

                keygen = generateKey()
                key = base64.b32encode(keygen.returnValue(user.username).encode())
                OTP = pyotp.HOTP(key, digits = 4)
                otp = OTP.at(user.counter)
                otp = '1234'
                otp_user = OTPs.objects.create(user=user, otp=otp)
                serializer = ProfileTokenSerializer(user)
                return Response({"status":1,"message":"a password recovery OTP has been sent to your registered mobile No.","data":serializer.data})
            else:
                return Response({"status":0,"message":"please enter a valid mobile number."},status = status.HTTP_406_NOT_ACCEPTABLE)
        else:
            return Response({"status":0,"message":"invalid API key."},status = status.HTTP_401_UNAUTHORIZED)   


class updatepassword(viewsets.ModelViewSet):
    queryset = User.objects.all()
    http_method_names = ['post']
    def get_user(self,mobile_number,country_code):
        try:
            user = User.objects.get(mobile_number=mobile_number, country_code=country_code)
            return user
        except Exception as e:
            print(e)
            return 0
    
    def create(self,request):
        apikey =request.GET.get('apikey','test')
        if apikey.strip() == API_KEY.strip():
            token = request.META.get("HTTP_AUTHORIZATION")
            user = decrypt_token(token) 
            # mobile_number = request.data.get('mobile_number',None)
            # country_code = request.data.get('country_code',None)
            # #email = request.data.get('email',None)
            # otp = request.data.get('otp',None)
            #print("<><><><<><><><><><><><><><><><><><><><><><><><><><><><<><>",otp)
            password = request.data.get('password',None)
            # user = self.get_user(mobile_number)
            # if mobile_number:
            #     try:
            #         user =  User.objects.get(mobile_number=mobile_number,country_code=country_code)
            #         #login_type = 'email'
            #     except:
            #         return Response({"status":0,"message":"Please enter a valid Mobile No."},status = status.HTTP_406_NOT_ACCEPTABLE)
            
            # # if user:
            # #     try:
            #         uotp = OTPs.objects.get(user=user)
            #         print("<><><><<><><><><><><><><><><><><><><><><><><><><><><><<><>",uotp)
            #     except:
            #         return Response({"status":2,"message":"Please enter a valid otp."},status = status.HTTP_406_NOT_ACCEPTABLE)  
                # if otp:
                #     if int(uotp.otp) == int(otp):                               
                #         print("<><><><<><><><><><><><><><><><><><><><><><><><><><><><<><>",int(uotp.otp))
            #if user.check_password(old_password):
            user.set_password(password)
            user.save()
            serializer = ProfileTokenSerializer(user)
            return Response({"status":1,"message":"your password update successfully.","data":serializer.data})
        else:
            return Response({"status":0,"message":"invalid OTP."},status = status.HTTP_406_NOT_ACCEPTABLE)
#     else:
#         return Response({"status":0,"message":"Please enter a valid otp."},status = status.HTTP_406_NOT_ACCEPTABLE)        
# else:
#     return Response({"status":0,"message":"User doesn't exists."},status = status.HTTP_406_NOT_ACCEPTABLE)
# else:
# return Response({"status":0,"message":"Invalid API Key."},status = status.HTTP_401_UNAUTHORIZED)    
# 

# CHANGE FAMILY HEAD API
class ChangeFamilyHead(viewsets.ModelViewSet):
    queryset = Family.objects.all()
    serializer_class = Family_Serializer
    http_method_names = ['post']
    # create family head with put
    def create(self,request, *args, **kwargs):
        apikey =request.GET.get('apikey','test')
        if apikey.strip() == API_KEY.strip():
            token = request.META.get("HTTP_AUTHORIZATION")
            user = decrypt_token(token)
            user_id = request.data.get('user_id')
            new_user= User.objects.get(user_id = user_id)
            try:
                family = Family.objects.get(Q(family_head=user))
            except:
                return Response({"status":0,"message":"only family head can."})
                
            print("______________FAMILY__________________",family)
           # obj=Family.user_id.get(user_id=family.user_id).exists()
            if new_user in family.user_id.all():
                #print("&&&&&&&&&&&&&&&&&&&&&&&&&".user_id)
                print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&",new_user)  
                family.family_head = new_user
                family.save()
                return Response({"status":1,"message":"family head updated successfully."})
           
               
            else:
                return Response({"status":0,"message":"user must be family head to perform this operation"},status = status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({"status":0,"message":"invalid API key."},status = status.HTTP_401_UNAUTHORIZED)

           
    # # update  user with put
    # def update(self,request, pk):
    #     token = request.META.get("HTTP_AUTHORIZATION")
    #     user = decrypt_token(token)  
    #     print("user",user)
    #     if user:
    #         try:
    #             user = User.objects.get(user_id = pk)
    #             serializer = User_Serializer(user,data = request.data)
    #             if serializer.is_valid():
    #                 serializer.save()
    #                 user = User.objects.get(user_id = pk)
    #                 token = create_token(user=user)
    #                 data=serializer.data
    #                 data['token'] = token
    #                 return Response({'data' : data,
    #                                 "status_code": 200,
    #                                 "response_error": False,
    #                                 'status_message': "User data updated successfully!"},status=status.HTTP_200_OK)
                
    #             else:
    #                 return Response({'status' : 400 ,'message' : serializer.errors},status=status.HTTP_400_BAD_REQUEST)
    #         except:
    #             return Response({"status":404,"message":"user not found"},status=status.HTTP_404_NOT_FOUND)
    #     else:
    #         return Response({"status":401,"message":"User does not exist"},status = status.HTTP_401_UNAUTHORIZED)

      
   
    # #  user find by id get
    # def retrieve(self, request, pk=None):
    #     token = request.META.get("HTTP_AUTHORIZATION")
    #     user = decrypt_token(token)  
    #     if user:
    #         if id is not None:
    #             try:
    #                 user = User.objects.get(user_id=pk)
    #             except:
    #                 return Response({"status":401,"message":"User does not exist"},status = status.HTTP_401_UNAUTHORIZED)
    #         # else:    
    #             serializer = User_Serializer(user)
    #             return Response({"data":serializer.data},status=status.HTTP_200_OK)
    #     else:
    #         return Response({"status":401,"message":"User does not exist"},status = status.HTTP_401_UNAUTHORIZED)    
    
    # # delete user 
    # def destroy(self,request,pk):
    #     token = request.META.get("HTTP_AUTHORIZATION")
    #     user = decrypt_token(token)  
    #     if user:
    #         try:
    #             user = User.objects.get(user_id = pk)
    #             user.is_active = False
    #             user.delete()
    #             return Response({'status' : 204,'msg':'data deleted'},status=status.HTTP_204_NO_CONTENT)
    #         except Exception as e:
    #             print(e)
    #             return Response({"status":401,"message":"User does not exist"},status = status.HTTP_401_UNAUTHORIZED)
    #     else:
    #         return Response({"status":401,"message":"User does not exist"},status = status.HTTP_401_UNAUTHORIZED)
     
    # @action(methods=['post'], detail=False)
    # def login(self, request):
    #     mobile_number = request.data.get("mobile_number")
    #     print(mobile_number)
    #     password = request.data.get("password")
    #     print(password)

    #     if mobile_number=="":
    #         return Response({'status': 406,'msg' : 'mobile number and password both are required'},status=status.HTTP_406_NOT_ACCEPTABLE)
    #     # elif mobile_number=="":
    #     #     return Response({'status': 406,'msg' : 'mobile_number is required'},status=status.HTTP_406_NOT_ACCEPTABLE)
    #     if mobile_validater(mobile_number):
    #         return Response({'status' : 406 ,'message' :"mobile number take only numbers"},status=status.HTTP_406_NOT_ACCEPTABLE)
    #     try:
    #         if mobile_number:
    #             try:
    #                 user = User.objects.get(mobile_number=mobile_number)
    #             except:
    #                 return Response({"status":401,"message":"User does not exist"},status = status.HTTP_401_UNAUTHORIZED)
    #             if user.mobile_number == mobile_number:
    #                 if user.check_password(password):   
    #                     token = create_token(user=user)
    #                     return Response({"data": mobile_number,'status' : 200,'msg':'login success','token':token},status=status.HTTP_200_OK)
    #                 else:
    #                     return Response({'status':406,'massage':'password  is required'},status=status.HTTP_406_NOT_ACCEPTABLE)
    #             else:
    #                 return Response({'status':406,'massage':'mobile_number mismatched'},status=status.HTTP_406_NOT_ACCEPTABLE)
    #         else:
    #             return Response({'status':406,'massage':'password mismatched'},status=status.HTTP_406_NOT_ACCEPTABLE)
    #     except:
    #         return Response({"status":401,"message":"User does not exist"},status = status.HTTP_401_UNAUTHORIZED)
     

    # # Forgot Password API: 
    # @action(methods=['post'], detail=False)
    # def forgot_password(self,request):
    #     # token = request.META.get("HTTP_AUTHORIZATION")
    #     # user = decrypt_token(token)  
    #     # if user:
    #         mobile_number = request.data.get("mobile_number")
    #         new_password = request.data.get("new_password")

    #         if mobile_validater(mobile_number):
    #             return Response({'status' : 406 ,'message' :"mobile number take only numbers"},status=status.HTTP_406_NOT_ACCEPTABLE)
    #         if validate_password(new_password):  
    #             print("Valid password")
    #         else:  
    #             print("Invalid password")  
    #             return Response({'status' : 406 ,'message' :"password must be length should be at least 8 to 12 ,one numeral,one uppercase,one lowercase,one of the symbols $@#"},status=status.HTTP_406_NOT_ACCEPTABLE)
    #         if mobile_number=="":
    #             return Response({'status': 400,'msg' : 'mobile_number is required'},status=status.HTTP_400_BAD_REQUEST)
    #         if mobile_number:
    #             try:
    #                 user = User.objects.get(mobile_number=mobile_number)
    #                 if user.mobile_number==mobile_number:
    #                     digits = [i for i in range(0, 10)]
    #                     random_str = ""
    #                     for i in range(6):
    #                         index = math.floor(random.random() * 10)
    #                         random_str += str(digits[index])
    #                     # opt = OTPs.objcts.create(OTPs :random_str)
    #                     # otp.save()
    #                     # user_model = User.objects.get(mobile_number=mobile_number)
    #                     otp = OTPs.objects.create(user=user,otp=random_str)
    #                     otp.save()
    #                     # return Response({'status': 200,'otp' : random_str,"message":"your otp fot reset password"},status=status.HTTP_200_OK)
    #                 else:
    #                     pass
    #             except:
    #                 return Response({"status":401,"message":"User does not exist"},status = status.HTTP_401_UNAUTHORIZED)
    #             if user.mobile_number == mobile_number:
    #                 user.set_password(new_password)
    #                 token = create_token(user=user)
    #                 user.save()
    #                 return Response({"data": mobile_number,'status' : 200,'msg':'login success','otp' : random_str,'token':token,},status=status.HTTP_200_OK)
    #             else:
    #                 return Response({"status":401,"message":"User does not exist"},status = status.HTTP_401_UNAUTHORIZED)
    #         else:
    #             return Response({'status' : 200,'msg':'login success'},status=status.HTTP_200_OK)

class AddFamilyMember(viewsets.ModelViewSet):
    queryset = User.objects.all()
    http_method_names = ['get','post','put','delete']
    
    def create(self,request):
        token = request.META.get("HTTP_AUTHORIZATION")
        user = decrypt_token(token) 
        print("+++++++++++++++++user+++++++++++++++++++",user)
        apikey =request.GET.get('apikey','test')
        if apikey.strip() == API_KEY.strip():
            mobile_number = request.data.get('mobile_number',None)
            country_code = request.data.get('country_code',None)
            relation = request.data.get('relation')
            if mobile_number:
                try:
                    user =  User.objects.get(mobile_number=mobile_number,country_code=country_code)
                    return Response({"status":0,"message":"user already exists."},status = status.HTTP_406_NOT_ACCEPTABLE)
                except:
                    pass
            if user:
                new_user = User.objects.create(mobile_number=mobile_number,country_code=country_code,relation=relation,is_active=False)
                family=Family.objects.get(family_head=user)
                family.user_id.add(new_user)
                family.save()
                return Response({'status': 1, "message": "family member created successfully"},status=status.HTTP_200_OK)        
            else:
                return Response({"status":0,"message":"user doesn't exists."},status = status.HTTP_406_NOT_ACCEPTABLE)
        else:
            return Response({"status":0,"message":"invalid API key."},status = status.HTTP_401_UNAUTHORIZED)

# Get All Family Member List
    def list(self,request): # Done
        apikey =request.GET.get('apikey','test')
        if apikey.strip() == API_KEY.strip():
            token = request.META.get("HTTP_AUTHORIZATION")
            user = decrypt_token(token) 
            print("_--__--__",user) 
            if user:
                print("_______________________________________________",user)
                #try:
                family = Family.objects.filter(Q(family_head=user)|Q(user_id__in = (user,))).distinct()
                print("<><><><<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>") 
                if not family :
                    return Response({"status":0,"message":"no data found"},status=status.HTTP_404_NOT_FOUND)
                else:
                    pass
                #except:
                #    return Response({"status":0,"message":"No data Found"},status=status.HTTP_404_NOT_FOUND)

                serializer = Family_Serializer(family,many = True)
                # print(serializer)
                return Response({'data': serializer.data,
                                "status": 1,
                                "message":"all family member data fetched successfully",
                                "response_error": False
                                },status=status.HTTP_200_OK)
            else:
                return Response({"status":0,"message":"user does not exist"},status = status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({"status":0,"message":"invalid API key."},status = status.HTTP_401_UNAUTHORIZED) 

    
    def destroy(self,request,pk=None):
        token = request.META.get("HTTP_AUTHORIZATION")
        user = decrypt_token(token) 
        print("+++++++++++++++++remove-user+++++++++++++++++++",user)
        apikey =request.GET.get('apikey','test')
        if apikey.strip() == API_KEY.strip():
            try:
               new_user = User.objects.get(pk = pk)
               print(new_user)
            except:
                return Response({"status":0,"message":"user doesn't exists."},status = status.HTTP_406_NOT_ACCEPTABLE)

            if new_user == user:
                return Response({"status":0,"message":"You are not allowed to remove your own account."},status = status.HTTP_406_NOT_ACCEPTABLE)
            if user:
                try:
                    family = Family.objects.get(user_id__in=[new_user])
                except:
                    return Response({"status":0,"message":"user doesn't exists."},status = status.HTTP_406_NOT_ACCEPTABLE)
                family.user_id.remove(new_user)
                family.save()
                new_user.save()
                return Response({'status': 1, "message": "family member removed successfully"},status=status.HTTP_204_NO_CONTENT)        
            else:
                return Response({"status":0,"message":"user doesn't exists."},status = status.HTTP_406_NOT_ACCEPTABLE)
        else:
            return Response({"status":0,"message":"invalid api key."},status = status.HTTP_401_UNAUTHORIZED)



    # def list(self,request):
    #     apikey =request.GET.get('apikey','test')
    #     if apikey.strip() == API_KEY.strip():
    #         token = request.META.get("HTTP_AUTHORIZATION")
    #         user = decrypt_token(token)
    #         family = Family.objects.get(Q(user_id__in=[user])|Q(family_head=user))
    #         if user:
    #             # if family:
    #                 try:
                    
    #                     #family=Family.objects.get(family_head=user)
    #                     print("****************************",family)
    #                     #appliance = Appliances.objects.all()
    #                     serializer = Family_Serializer(family, many=True)
    #                     print(serializer)
    #                     return Response({'data': serializer.data,
    #                                     "status_code": 1,
    #                                     "status_message":"All Family Member data fetched successfully",
    #                                     "response_error": False
    #                                     },status=status.HTTP_200_OK)
    #                 except:
    #                     return Response({"status":0,"message":"No data Found"},status=status.HTTP_404_NOT_FOUND)
    #             # else:
    #             #     return Response({"status":0,"message":"No data Found"},status=status.HTTP_404_NOT_FOUND)
    #         # else:
    #         #     return Response({"status":401,"message":"User does not exist"},status = status.HTTP_401_UNAUTHORIZED)
    #     else:
    #         return Response({"status":0,"message":"Invalid API Key."},status = status.HTTP_401_UNAUTHORIZED)
        
# @api_view(['POST'])
# def send_otp(request):
#     mobile_number =request.data["mobile_number"]
#     if mobile_validater(mobile_number):
#         return Response({'status' : 406 ,'message' :"mobile number take only numbers"},status=status.HTTP_406_NOT_ACCEPTABLE)
#     if mobile_number=="":
#         return Response({"status":406,"message":"mobile number is required"},status=status.HTTP_406_NOT_ACCEPTABLE)
#     # print(mobile_number)
#     # email = request.data["email"]
#     if mobile_number==mobile_number:
#         digits = [i for i in range(0, 10)]
#         random_str = ""
#         for i in range(4):
#             index = math.floor(random.random() * 10)
#             random_str += str(digits[index])
#         # opt = OTPs.objcts.create(OTPs :random_str)
#         # otp.save()
#         # user_model = User.objects.get(mobile_number=mobile_number)

#         url = "https://www.fast2sms.com/dev/bulkV2"
        
#         payload = "message={} is the Verification code to log in your Task-Karo account. DO NOT share this code&language=english&route=q&numbers={} ".format(random_str,mobile_number)
#         headers = {
#             'authorization': "kA1TXCPzK2BH7JtmqineSV5FxboZ8EMch4gIwfR9Wl6rpvYus3LqRkKJFhbm8WdXZQBN2xu7wcT9IU0H",
#             'Content-Type': "application/x-www-form-urlencoded",
#             'Cache-Control': "no-cache",
#             }

#         response = requests.request("POST", url, data=payload, headers=headers)

#         print(response.text)

#         otp = OTPs.objects.create(otp=random_str)
#         otp.save()
#         return Response({'status': 200,'otp' : random_str},status=status.HTTP_200_OK)
    
     

# @api_view(['POST'])
# def Verify_OTP(request):
#     mobile_number =request.data["mobile_number"]
#     # print("hi",type(mobile_number))
#     otp = request.data["otp_no"]
#     if mobile_validater(mobile_number):
#         return Response({'status' : 406 ,'message' :"mobile number take only numbers"},status=status.HTTP_406_NOT_ACCEPTABLE)
#     if mobile_number=="":
#     # if mobile_number:
#         # print("HI")
#         return Response({'status': 203,'msg' : 'mobile number is required'},status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
#     if mobile_number==mobile_number:
#         try:
#             otp = OTPs.objects.get(otp=otp)
#         except:
#             return Response({'status': 203 ,'msg' : 'invalid otp'},status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
#         if otp.otp == otp.otp:
#             Create_time = otp.created
#             # print(Create_time)
#             Expiry_time = timedelta(minutes=2)
#             # print(Expiry_time)
#             Current_time = datetime.now().replace(tzinfo=pytz.utc) 
#             # print(Current_time)
#             if Create_time + Expiry_time < Current_time :
#                 return Response({'status':408,'massage':'otp expired'},status=status.HTTP_408_REQUEST_TIMEOUT)
#             else:
#                 # is_active = True
#                 return Response({'status': 200,'msg' : 'otp verified'},status=status.HTTP_200_OK)
#         else:
#             return Response({'status': 203,'msg' : 'invalid otp'},status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION00)
      

# Parent User Update : updateProfile/id PUT (USER API)
# @api_view(['PUT'])
# def updateParent(request,id):
#     token = request.META.get("HTTP_AUTHORIZATION")
#     user = decrypt_token(token)  
#     if user:
#         try:
#             user = User.objects.get(user_id = id)
#         except:
#             return Response({'status':404,'massage':'user not found'},status=status.HTTP_404_NOT_FOUND)

#         serializer = User_Serializer(user,data = request.data)
#         if serializer.is_valid():
#             serializer.save()
#             user = User.objects.get(user_id = id)
#             token = create_token(user=user)
#             return Response({'data' : serializer.data,
#             "status_code": 200,
#             "response_error": False,
#             'status_message': "User data updated successfully!",
#             'token':token},status=status.HTTP_200_OK)
#         else:
#             return Response({'status':404,'massage':'user not found'},status=status.HTTP_404_NOT_FOUND)
#     else:
#         return Response({"status":401,"message":"User does not exist"},status = status.HTTP_401_UNAUTHORIZED)

# file upload (post) (USER API)
class ExampleView(viewsets.ViewSet):
    def create(self,request):
        token = request.META.get("HTTP_AUTHORIZATION")
        user = decrypt_token(token)  
        if user:
            user_image = request.FILES.get('user_image')
            # print(user_image)
            if not user_image:
                return Response({"data": {},
                "status": 0,
                "message": "please send attachment to upload.",
                "response_error": True
                },status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
            s3 = boto3.client('s3', aws_access_key_id=config('AWS_ACCESS_KEY_ID'),
                            aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY'))
            try:
                s3.upload_fileobj(user_image,config('AWS_STORAGE_BUCKET_NAME'), f'media/{user_image.name}',ExtraArgs={'ACL':'public-read'})
                response = f"https://{config('AWS_STORAGE_BUCKET_NAME')}.s3.{config('AWS_S3_REGION_NAME')}.amazonaws.com/media/{user_image.name}"
                return Response({'data':response,       
                                "status": 1,
                                "message": "document uploaded",
                                "response_error": True},status=200)
            except :
                return Response({'status':0,'status':'seems our server is having problem to serve you new access token. try to login again.'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"status":0,"message":"user does not exist"},status = status.HTTP_401_UNAUTHORIZED)

# util by get (User Relation API)
@api_view(['GET'])
def util_relation(request):
    # token = request.META.get("HTTP_AUTHORIZATION")
    # user = decrypt_token(token)  
    # if user:
        util = {
            "user-relation": [
                {
                "relation": "self",
                'id': 1,
                },
                {
                "relation": "Brother",
                'id': 2,
                },
                {
                "relation": "Sister",
                'id': 3,
                },
                {
                "relation": "Father",
                'id': 4,
                },
                {
                "relation": "Mother",
                'id': 5,
                },
                {
                "relation": "Cousin",
                'id': 6,
                },
                {
                "relation": "Grand Father",
                'id': 7,
                },
                {
                "relation": "Grand Mother",
                'id': 8,
                },
                {
                "relation": "Uncle",
                'id': 9,
                },
                {
                "relation": "Aunty",
                'id': 10,
                },
                {
                "relation": "Niece",
                'id': 11,
                },
                {
                "relation": "Nephew",
                'id': 12,
                },
                {
                "relation": "Others",
                'id': 13,
                },
            ],
            
        },
        version =request.GET.get('version',0)
        platform =request.GET.get('platform',0)
        if version == "1.0" and platform == "ios" or version == "1.0.0" and platform == "android" :
            return Response({'data':util,"version/platform": True,'status':1,'message':'util types data fetched successfully',"response_error": False},status=200)


# util by get (Service Type Utils API)
@api_view(['GET'])
def util_service_type(request):
    # token = request.META.get("HTTP_AUTHORIZATION")
    # user = decrypt_token(token)  
    # if user:
        util = {
            "service_provider_type": [
                {
                "service_type": "Carpenter",
                'id': 1,
                },
                {
                "service_type": "Plumber",
                'id': 2,
                },
                {
                "service_type": "Wifi Provider",
                'id': 3,
                },
                {
                "service_type": "Cable",
                'id': 4,
                },
                {
                "service_type": "Security",
                'id': 5,
                },
                {
                "service_type": "Driver",
                'id': 6,
                },
                {
                "service_type": "Maid",
                'id': 7,
                },
                {
                "service_type": "Electrician",
                'id': 8,
                },
                {
                "service_type": "Construction or Civil Worker",
                'id': 9,
                },
                {
                "service_type": "Helper",
                'id': 10,
                },
                {
                "service_type": "Gardener",
                'id': 11,
                },
                {
                "service_type": "Cleaner",
                'id': 12,
                },
                {
                "service_type": "Waiter",
                'id': 13,
                },
                {
                "service_type": "AC Service",
                'id': 14,
                },
                {
                "service_type": "AC Provider",
                'id': 15,
                },
                {
                "service_type": "Shopkeeper",
                'id': 16,
                },
                {
                "service_type": "Watchman",
                'id': 17,
                },
                {
                "service_type": "Worker",
                'id': 18,
                },
                {
                "service_type": "Security Guard",
                'id': 19,
                },
                {
                "service_type": "Others",
                'id': 20,
                },
            ],
        },
        version =request.GET.get('version',0)
        platform =request.GET.get('platform',0)
        if version == "1.0" and platform == "ios" or version == "1.0.0" and platform == "android" :
            return Response({'data':util,"version/platform": True,'status':1,'message':'util types data fetched successfully',"response_error": False},status=200)

# util by get (Applience Type Utils API)
@api_view(['GET'])
def util_applience_type(request):
    # token = request.META.get("HTTP_AUTHORIZATION")
    # user = decrypt_token(token)  
    # if user:
        util = {
            "Appliences_type": [
                {
                "Applience": "Carpenter",
                'id': 1,
                },
                {
                "Applience":"Refridgerator",
                'id': 2,
                },
                {
                "Applience": "Water Cooler",
                'id': 3,
                },
                {
                "Applience": "Ice Maker",
                'id': 4,
                },
                {
                "Applience": "Kitchen Stove",
                'id': 5,
                },
                {
                "Applience": "Rice Cooker",
                'id': 6,
                },
                {
                "Applience": "Roti maker",
                'id': 7,
                },
                {
                "Applience": "Steamer Oven",
                'id': 8,
                },
                {
                "Applience": "Microwaves",
                'id': 9,
                },
                {
                "Applience": "Washing Machine",
                'id': 10,
                },
                {
                "Applience": "Clothes Dryer",
                'id': 11,
                },
                {
                "Applience": "Drying Cabinet",
                'id': 12,
                },
                {
                "Applience": "Dish washer",
                'id': 13,
                },
                {
                "Applience": "Air Conditioner",
                'id': 14,
                },
                {
                "Applience": "Radiator",
                'id': 15,
                },
                {
                "Applience": "Water Heater",
                'id': 16,
                },
                {
                "Applience": "Coffee Maker",
                'id': 17,
                },
                {
                "Applience": "Blender",
                'id': 18,
                },
                {
                "Applience": "Mixer",
                'id': 19,
                },
                {
                "Applience": "Toaster",
                'id': 20,
                },
                {
                "Applience": "Crock Pot",
                'id': 21,
                },
                {
                "Applience":"Water Purifier",
                'id': 22,
                },
                {
                "Applience": "Kitchen Hoods",
                'id': 23,
                },
                {
                "Applience": "Food Processor",
                'id': 24,
                },
                {
                "Applience": "Deep Dryer",
                'id': 25,
                },
                {
                "Applience": "Air Fryers",
                'id': 26,
                },
                {
                "Applience": "Food Dehydrators",
                'id': 27,
                },
                {
                "Applience": "iron",
                'id': 28,
                },
                {
                "Applience": "Electrics drill",
                'id': 29,
                },
                {
                "Applience": "Kettle",
                'id': 30,
                },
                {
                "Applience": "Vaccum Cleaner",
                'id': 31,
                },
                {
                "Applience": "Electrics Fan",
                'id': 32,
                },
                {
                "Applience": "Television",
                'id': 33,
                },
                {
                "Applience": "Lamp",
                'id': 34,
                },
                {
                "Applience": "Light Bulb",
                'id': 35,
                },
                {
                "Applience": "Lantern",
                'id': 36,
                },
                {
                "Applience": "Torch",
                'id': 37,
                },
                {
                "Applience": "Eveporative Cooler",
                'id': 38,
                },
                {
                "Applience": "Humidifier",
                'id': 39,
                },
                {
                "Applience": "Air Purifier",
                'id': 40,
                },
                {
                "Applience": "Waffle Iron",
                'id': 41,
                },
                {
                "Applience":"Oven",
                'id': 42,
                },
                {
                "Applience": "Juicer",
                'id': 43,
                },
                {
                "Applience": "Ice Cream Maker",
                'id': 44,
                },
                {
                "Applience": "Cooler",
                'id': 45,
                },
                {
                "Applience": "Heater",
                'id': 46,
                },
                {
                "Applience": "Fan",
                'id': 47,
                },
                {
                "Applience": "Telephone",
                'id': 48,
                },
                {
                "Applience": "Computer",
                'id': 49,
                },
                {
                "Applience": "Laptop",
                'id': 50,
                },
                {
                "Applience": "Mobile",
                'id': 51,
                },
            ],
            
        },
        version =request.GET.get('version',0)
        platform =request.GET.get('platform',0)
        if version == "1.0" and platform == "ios" or version == "1.0.0" and platform == "android" :
            return Response({'data':util,"version/platform": True,'status':1,'message':'util types data fetched successfully',"response_error": False},status=200)



            

# LOCATION API
class LocationAPI(viewsets.ModelViewSet):# Done
    queryset = Location.objects.all()
    serializer_class = Location_Serializer
    http_method_names = ['get','post','put','delete']
    lookup_body_field = 'pk'

    # create location with post
    def create(self,request):
        apikey =request.GET.get('apikey','test')
        if apikey.strip() == API_KEY.strip():
            token = request.META.get("HTTP_AUTHORIZATION")
            user = decrypt_token(token)
            #new_user= User.objects.get(user_id = user.user_id)
            print("_--__--__",user)
            if len(request.data.keys()) < 1:
                return Response({"status":0, "message":"empty request body"}, status=status.HTTP_406_NOT_ACCEPTABLE)
            try:

                family = Family.objects.get(user_id__in=[user])
                #family=Family.objects.get(user=new_user)
                print("++++++++++++++++++++++++++++++++++++++++++",family)
            except:
                family = Family.objects.get(family_head=user)
            if user:
                try:
                    serializer = Location_Serializer(data = request.data)
                    #print("+++++++++++++++++++++++++_____++++++++",serializer)
                    location_name = request.data.get('location_name', None)
                    address = request.data.get('address')
                    if len(location_name) <= 10 and len(address) <= 10 :
                        return Response({"status":0,"message":"location_name and address must be more then atlist 10 charecter"},status=status.HTTP_406_NOT_ACCEPTABLE)

                    if not serializer.is_valid():
                        if 'state_id' in serializer.errors:
                            return Response({'status': 0 ,'message' : serializer.errors['state_id'][0]},status=status.HTTP_406_NOT_ACCEPTABLE)  
                        if 'city_id' in serializer.errors:
                            return Response({'status': 0 ,'message' : serializer.errors['city_id'][0]},status=status.HTTP_406_NOT_ACCEPTABLE)
                        
                        return Response({'status': 0 ,'message' : serializer},status=status.HTTP_406_NOT_ACCEPTABLE)

                    else: 
                        new_loc = serializer.save(family_id=family, created_by=user)
                        
                        serializer= Location_Serializer(new_loc)
                        print("_______________________________________________",serializer.data)
                        return Response({'data' : serializer.data,
                                        'status': 1, 
                                        'message' :"location data created successfully!", "response_error": False},status=status.HTTP_201_CREATED)
                except Exception as e :
                    print(e)
                    return Response({'error': e})
            else:
                return Response({"status":0,"message":"user does not exist"},status = status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({"status":0,"message":"invalid API key."},status = status.HTTP_401_UNAUTHORIZED)
        

    # all location by get
    def list(self,request): # Done
        apikey =request.GET.get('apikey','test')
        if apikey.strip() == API_KEY.strip():
            token = request.META.get("HTTP_AUTHORIZATION")
            user = decrypt_token(token) 
            print("_--__--__",user) 
            if user:
                print("_______________________________________________",user)
                try:
                    loc = Location.objects.filter(Q(family_id__user_id__in=[user])|Q(family_id__family_head=user)).exclude(is_deleted=True).distinct()
                    #family = Family.objects.get(family_id__user_id__in=[loc)
                    print("<><><><<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>",loc)
                    if not loc:
                        return Response({"status":0,"message":"no data found"},status=status.HTTP_404_NOT_FOUND)
                    else:
                        serializer = Location_Serializer(loc,many = True)

                        return Response({'data':serializer.data,
                                        "status": 1,
                                        "message": "location data fetched successfully",
                                        "response_error": False},status=status.HTTP_200_OK)
                except Exception as e:
                    print(e)
                    return Response({"status":0,"message":str(e)},status = status.HTTP_400_BAD_REQUEST)
                    pass
                    # return Response({"status":0,"message":"No data Found"},status=status.HTTP_404_NOT_FOUND)


            else:
                return Response({"status":0,"message":"user does not exist"},status = status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({"status":0,"message":"invalid API key."},status = status.HTTP_401_UNAUTHORIZED)   
        

# update location with put
    def update(self,request,pk): 
        apikey =request.GET.get('apikey','test')
        if apikey.strip() == API_KEY.strip():
            token = request.META.get("HTTP_AUTHORIZATION")
            user = decrypt_token(token)  
            if user:
                    try: 
                        location = Location.objects.get(pk=pk)
                    except:
                        return Response({'status': 0 ,'message' : 'Location does not exists'},status=status.HTTP_406_NOT_ACCEPTABLE)
                    if location.created_by == user:
                        serializer = Location_Serializer(instance=location,data=request.data,partial=True)
                        if serializer.is_valid():

                            updated_loc = serializer.save()
                            serializer = Location_Serializer(updated_loc)
                            return Response({'data':serializer.data ,'status': 1 ,'message' : 'Location data Updated Successfully'},status=status.HTTP_200_OK)
                        else:

                            if 'state_id' in serializer.errors:
                                return Response({'status': 0 ,'message' : serializer.errors['state_id'][0]},status=status.HTTP_406_NOT_ACCEPTABLE)  
                            if 'city_id' in serializer.errors:
                                return Response({'status': 0 ,'message' : serializer.errors['city_id'][0]},status=status.HTTP_406_NOT_ACCEPTABLE)  

                            return Response({'status': 0 ,'message' : serializer},status=status.HTTP_406_NOT_ACCEPTABLE)

                    return Response({'status':0, 'message':'You are not allowed to perform the action'}, status=status.HTTP_401_UNAUTHORIZED)
              
            else:
                return Response({"status":0,"message":"user does not exist"},status = status.HTTP_401_UNAUTHORIZED)  
        else:
            return Response({"status":0,"message":"invalid API key."},status = status.HTTP_401_UNAUTHORIZED)
        

# # location by id get
#     def retrieve(self, request, pk):
#         apikey =request.GET.get('apikey','test')
#         if apikey.strip() == API_KEY.strip():
#             token = request.META.get("HTTP_AUTHORIZATION")
#             user = decrypt_token(token)  
#             if user:
#                 if pk is not None:
#                     location = Location.objects.get(pk=pk)
#                     location=Location.objects.filter(Q(family_id__user_id__in=[user])|Q(family_id__family_head=user))
#                     serializer = Location_Serializer(location)
#                     return Response({'data':serializer.data,"status": 1,
#                                     "status": "Location data By Id Fetch Successfully",
#                                     "Response_error": False},status=status.HTTP_200_OK)

#                 else:
#                     location = Location.objects.filter(Q(family_id__user_id__in=[user])|Q(family_id__family_head=user))
#                     serializer = Location_Serializer(location,many = True)
                    
#                     #return Response(serializer.data)
#                     #return Response({"status":1,"message":"Location data By Id Fetch Successfully","data":serializer.data})
#             else:
#                 return Response({"status":0,"message":"User does not exist"},status = status.HTTP_401_UNAUTHORIZED)
#         else:
#             return Response({"status":0,"message":"Invalid API Key."},status = status.HTTP_401_UNAUTHORIZED)

#location  delete
    def destroy(self,request,pk):
        apikey =request.GET.get('apikey','test')
        if apikey.strip() == API_KEY.strip():
            token = request.META.get("HTTP_AUTHORIZATION")
            user = decrypt_token(token)  
            # loc = Location.objects.filter(Q(family_id__user_id__in=[user])|Q(family_id__family_head=user))
            if user:
                try:
                    location = Location.objects.get(pk = pk, created_by=user)
                except Exception as e:
                    return Response({"status":0, "message":"You are not allowed for the action"})
                location.is_deleted = True
                location.save()
                return Response({'status': 0,'massage': 'data deleted'},status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"status":0,"message":"user does not exist"},status = status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({"status":0,"message":"invalid API key."},status = status.HTTP_401_UNAUTHORIZED)
        
#location from pincode
@api_view(["POST"])
def Pincode(request,id=None):
    apikey =request.GET.get('apikey','test')
    if apikey.strip() == API_KEY.strip():
        token = request.META.get("HTTP_AUTHORIZATION")
        user = decrypt_token(token)  
        if user:
            pincode = request.data['pincode']
            if pincode:
            #     return Response({"status":406,"message":"pincode is required"},status = status.HTTP_406_NOT_ACCEPTABLE) 
                #serializer = City_Serializer
                # if serializer.data:
                    try:
                        #family = Family.objects.get(Q(user_id__in=[user])|Q(family_head=user))
                        #print("++++++++++++++++++++++++++++++++++++++++++",family)
                        loc = City.objects.filter(pincode=pincode)
                        print("++++++++++++++++++++++++++++++++++++++++++",loc)
                        serializer = City_Serializer(loc, many = True)
                        # print(serializer)
                        #print("<><><><<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>",serializer.data)     
                        if serializer.data:                                                                                                                                                                
                            return Response({'data': serializer.data,
                                            "status": 1,
                                            "message": "city data fetched successfully",
                                            "response_error":False},status=status.HTTP_200_OK)
                        else:
                            return Response({'data': serializer.data,
                                            "status": 0,
                                            "message": "No data found",
                                            "response_error":False},status=status.HTTP_204_NO_CONTENT)
                    except:
                        return Response({'data': {},'status':0,'message':serializer.errors,
                        "response_error": True},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"status":0,"message":"pincode lenght is not more then 10"},status=status.HTTP_406_NOT_ACCEPTABLE)
                    
        else:
            return Response({"status":0,"message":"user does not exist"},status = status.HTTP_401_UNAUTHORIZED)  
    else:
        return Response({"status":0,"message":"invalid API key."},status = status.HTTP_401_UNAUTHORIZED)

#   "password": "jeera@123",
#         "mobile_number":"6598324759",
#         "gender":"female",
#         "email": "jeera@gmail.com",
#         "first_name": "jeera",
#         "last_name": "patel"      
# get locatoion by family id (LOCATION API)

@api_view(['GET'])
def findByFamilyIdlocation(request,id):
    apikey =request.GET.get('apikey','test')
    if apikey.strip() == API_KEY.strip():
        token = request.META.get("HTTP_AUTHORIZATION")
        user = decrypt_token(token) 
        family = Family.objects.filter(user_id__in=[user]).last()
        print(family) 
        if user:
            try:
                loc = Location.objects.filter(family_id=family)
                serializer = Location_Serializer(loc,many = True)
                if serializer.data:
                    return Response({'data': serializer.data,
                                    "status": 1,
                                    "message": "city data fetched successfully",
                                    "response_error":False},status=status.HTTP_201_CREATED)
                else:
                    return Response({"status":0,"message":"no location data found"},status = status.HTTP_404_NOT_FOUND)
            except:
                return Response({'data': {},'status':0,'massage':serializer.errors,"response_error": True},status=404)
        else:
            return Response({"status":0,"message":"user does not exist"},status = status.HTTP_401_UNAUTHORIZED) 
    else:
        return Response({"status":0,"message":"invalid API key."},status = status.HTTP_401_UNAUTHORIZED)
    
# COUNTRY API
class CountryAPI(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = Country_Serializer
    http_method_names = ['get']

# get COUNTRY 
    def list(self,request):
        apikey =request.GET.get('apikey','test')
        if apikey.strip() == API_KEY.strip():
            token = request.META.get("HTTP_AUTHORIZATION")
            user = decrypt_token(token)  
            if user:
                try:
                    country = Country.objects.all()
                    serializer = Country_Serializer(country,many = True)
                    print(serializer)
                    return Response({"data":serializer.data,
                                    "status": 1,
                                    "message": "country data fetched successfully",
                                    "response_error":False},status=status.HTTP_201_CREATED)
                except:
                    return Response({"status":0,"message":"no country data found"},status = status.HTTP_404_NOT_FOUND)
            else:
                return Response({"status":0,"message":"user does not exist"},status = status.HTTP_401_UNAUTHORIZED) 
        else:
            return Response({"status":0,"message":"invalid API key."},status = status.HTTP_401_UNAUTHORIZED)

#STATE API 
class  StateAPI(viewsets.ModelViewSet):
    queryset = State.objects.all()
    serializer_class = State_Serializer
    http_method_names = ['get']
# Get State 
    def list(self,request):
        apikey =request.GET.get('apikey','test')
        if apikey.strip() == API_KEY.strip():
            token = request.META.get("HTTP_AUTHORIZATION")
            user = decrypt_token(token)  
            if user:
                try:
                    state = State.objects.all()
                    serializer = State_Serializer(state,many = True)
                    print(serializer)
                    return Response({'data': serializer.data,
                                "status": 1,
                                "message": "city records fetched successfully",
                                "response_error":False},status=status.HTTP_201_CREATED)
                except:
                    return Response({"status":0,"message":"no state data found"},status = status.HTTP_404_NOT_FOUND)
            else:
                return Response({"status":0,"message":"user does not exist"},status = status.HTTP_401_UNAUTHORIZED) 
        else:
            return Response({"status":0,"message":"invalid API key."},status = status.HTTP_401_UNAUTHORIZED)

class CityAPI(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = City_Serializer
    http_method_names = ['get']
#Get City by State Id
    def list(self,request,id=None):
        apikey =request.GET.get('apikey','test')
        if apikey.strip() == API_KEY.strip():
            token = request.META.get("HTTP_AUTHORIZATION")
            user = decrypt_token(token)  
            if user:
                try:
                    cities = City.objects.filter(state_id=id)
                    # print(cities)
                    serializer = City_Serializer(cities,many = True)
                    list = []
                    
                    # print(serializer)
                    if serializer.data:
                        return Response({'data': serializer.data,
                                    "status": 1,
                                    "message": "city records fetched successfully",
                                    "response_error":False},status=status.HTTP_201_CREATED)
                    else:
                        return Response({'error':serializer.errors})
                except Exception as e:
                        print(e)
                        return Response({'status' : 0 , 'message' : serializer.errors},status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
            else:
                return Response({"status":0,"message":"user does not exist"},status = status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({"status":0,"message":"invalid API key."},status = status.HTTP_401_UNAUTHORIZED) 

# #CITY API 
# class CityAPI(viewsets.ModelViewSet):
#     queryset = City.objects.all()
#     serializer_class = City_Serializer
#     http_method_names = ['get']


# # get state 
#     def list(self,request):
#         token = request.META.get("HTTP_AUTHORIZATION")
#         user = decrypt_token(token)  
#         if user:
#                 city = City.objects.all()
#                 serializer = City_Serializer(city,many = True)
#                 print(serializer)
#                 return Response(serializer.data)
#         else:
#             return Response({"status":404,"message":"no city data found"},status = status.HTTP_404_NOT_FOUND)
 
# Service_provider API
class Service_ProviderAPI(viewsets.ModelViewSet):
    queryset = Service_provider.objects.all()
    serializer_class = Service_provider_Serializer
    http_method_names = ['get','post','put','delete']

#add Service_provider by post
    def create(self,request):
        apikey =request.GET.get('apikey','test')
        if apikey.strip() == API_KEY.strip():
            token = request.META.get("HTTP_AUTHORIZATION")
            user = decrypt_token(token)
            location_id = request.data.get('location_id')
            #family = Family.objects.filter(user_id__in=[user]).last()
            family= Family.objects.filter(Q(family_head=user) | Q(user_id__in=[user])).distinct().first()
            # family2= Family.objects.get(user_id__in=[user]) 
            
            #location = Location.objects.filter(family_id__user_id__in=[user])
            location_id = Location.objects.get(location_id=location_id)
            print(location_id)

            if user:
                try:
                    serializer = Service_provider_Serializer(data = request.data)
                    if not serializer.is_valid():
                        if "mobile_number" in serializer.errors:
                            return Response({'status' : 0 ,'message' : serializer.errors['mobile_number'][0]},status=status.HTTP_406_NOT_ACCEPTABLE)
                        if "email_id" in serializer.errors:
                            return Response({'status' : 0 ,'message' : serializer.errors['email_id'][0]},status=status.HTTP_406_NOT_ACCEPTABLE)
                            
                        print(serializer.errors)
                        return Response({'status' : 0 ,'message' :serializer.errors},status=400)
                        
                        
                    else:
                        new_Service_provider = serializer.save(family_id=family,location_id=location_id, created_by=user)
                        serializer = Service_provider_Serializer(new_Service_provider) 
                        return Response({'data' : serializer.data ,
                                        "status": 1,
                                        "message": "service provider data created successfully",
                                        "response_error": False},status=status.HTTP_201_CREATED)
                except Exception as e:
                    print(e)
                    return Response({'status' : 0 , 'message' : serializer.errors},status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
            else:
                return Response({"status":0,"message":"user does not exist"},status = status.HTTP_401_UNAUTHORIZED)  
        else:
            return Response({"status":0,"message":"invalid API key."},status = status.HTTP_401_UNAUTHORIZED)   
    
    def list(self,request): # Done 
        apikey =request.GET.get('apikey','test')
        if apikey.strip() == API_KEY.strip():
            token = request.META.get("HTTP_AUTHORIZATION")
            user = decrypt_token(token) 
            print("_--__--__",user) 
            if user:
                print("_______________________________________________",user)
                try:
                    #service_provider = Service_provider.objects.all()
                    service_provider = Service_provider.objects.filter(Q(family_id__user_id__in=[user])|Q(family_id__family_head=user)).distinct()
                    # service_provider = Service_provider.objects.filter(created_by = user)
                    serializer = Service_provider_Serializer(service_provider,many = True)
                    print(serializer)
                    if not service_provider:
                        return Response({"status":0,"message":"no service provider data found"},status=status.HTTP_404_NOT_FOUND)
                    else:
                        pass
                except:
                    return Response({"status":0,"message":"no data found"},status=status.HTTP_404_NOT_FOUND)

                serializer = Service_provider_Serializer(service_provider,many = True)
                # print(serializer)
                return Response({'data': serializer.data,
                                    "status":1,
                                    "message":"service rovider data fetched successfully",
                                },status=status.HTTP_200_OK)

            else:
                return Response({"status":0,"message":"user does not exist"},status = status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({"status":0,"message":"invalid API key."},status = status.HTTP_401_UNAUTHORIZED)
        
# update Service_provider with put
    def update(self,request,pk):
        apikey =request.GET.get('apikey','test')
        if apikey.strip() == API_KEY.strip():
            token = request.META.get("HTTP_AUTHORIZATION")
            user = decrypt_token(token)  
            if user:
                try:
                    service_provider = Service_provider.objects.get(pk = pk, created_by = user)
                    serializer = Service_provider_Serializer(instance=service_provider,data=request.data,partial=True)
                    if serializer.is_valid():
                        serializer.save(updated_by=user)
                        return Response({'data':serializer.data ,
                                        "status": 1,
                                        "message":"service provider data updated successfully",
                                        "response_error": False
                                        },status=status.HTTP_200_OK)

                    if "mobile_number" in serializer.errors:
                            return Response({'status' : 0 ,'message' : serializer.errors['mobile_number'][0]},status=status.HTTP_406_NOT_ACCEPTABLE)
                    if "email_id" in serializer.errors:
                            return Response({'status' : 0 ,'message' : serializer.errors['email_id'][0]},status=status.HTTP_406_NOT_ACCEPTABLE)

                    return Response({'data':{},'status': 0 , 'errors' : serializer.errors},status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
                except Service_provider.DoesNotExist:
                    return Response({'status': 0, 'message':"Service provide with given id is not found"}, status=status.HTTP_406_NOT_ACCEPTABLE)
                except Exception as e:
                    print(e)
                    return Response({'status' : 0 , 'message' : serializer.errors},status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
            else:
                return Response({"status":0,"message":"user does not exist"},status = status.HTTP_401_UNAUTHORIZED) 
        else:
            return Response({"status":0,"message":"invalid API key."},status = status.HTTP_401_UNAUTHORIZED) 


# Service_provider find  by id get
    def retrieve(self, request, pk):
        apikey =request.GET.get('apikey','test')
        if apikey.strip() == API_KEY.strip():
            token = request.META.get("HTTP_AUTHORIZATION")
            user = decrypt_token(token)  
            if user:
                try:
                    if pk is not None:
                        service_provider = Service_provider.objects.get(pk=pk, created_by=user)
                        serializer = Service_provider_Serializer(service_provider)
                        return Response({'data': serializer.data,   
                                        "status": 1,
                                        "message": "service provider data fetched successfully",
                                        "response_error": False
                                        },status=status.HTTP_200_OK)

                    service_provider = Service_provider.objects.all()
                    serializer = Service_provider_Serializer(service_provider,many = True)
                    return Response(serializer.data)

                except Service_provider.DoesNotExist:
                    return Response({'status': 0, 'message':"Service provide with given id is not found"}, status=status.HTTP_406_NOT_ACCEPTABLE)
                except Exception as e:
                    print(e)
                    return Response({'status' : 0 , 'message' 'invalid id': serializer.errors},status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
            else:
                return Response({"status":0,"message":"user does not exist"},status = status.HTTP_401_UNAUTHORIZED)  
        else:
            return Response({"status":0,"message":"invalid API key."},status = status.HTTP_401_UNAUTHORIZED)

# Service_provider  delete
    def destroy(self,request,pk):
        apikey =request.GET.get('apikey','test')
        if apikey.strip() == API_KEY.strip():
            token = request.META.get("HTTP_AUTHORIZATION")
            user = decrypt_token(token)  
            if user:
                try:
                    service_provider = Service_provider.objects.get(pk = pk, created_by=user)
                    if service_provider.created_by == user:
                        service_provider.delete()
                        return Response({'status':1,'message':'data deleted'},status=status.HTTP_204_NO_CONTENT)
                    else:
                        return Response({'status':0,'message':'You are not allowed to delete this task'},status=status.HTTP_401_UNAUTHORIZED)
                    
                except Service_provider.DoesNotExist:
                    return Response({"status":0, "message":"You are not authorized to perform the action"}, status=status.HTTP_406_NOT_ACCEPTABLE)                    
                    
                except Exception as e:
                    print(e)
                    return Response({'status' : 0 , 'message' : 'invalid id'},status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
            else:
                return Response({"status":0,"message":"user does not exist"},status = status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({"status":0,"message":"invalid API key."},status = status.HTTP_401_UNAUTHORIZED)  

# Appliance API
class ApplianceAPI(viewsets.ModelViewSet):
    queryset = Appliances.objects.all()
    serializer_class = Appliances_Serializer
    http_method_names = ['get','post','put','delete']

#add Appliance by post
    def create(self,request):
        apikey =request.GET.get('apikey','test')
        if apikey.strip() == API_KEY.strip():
            token = request.META.get("HTTP_AUTHORIZATION")
            user = decrypt_token(token)
            service_provider_id = request.data.get('service_provider_id')
            location_id = request.data.get('location_id')
            #family = Family.objects.filter(user_id__in=[user]).last()
            if len(request.data.keys()) < 1:
                return Response({'status':0, "message":"There is no data in request body"}, status=status.HTTP_406_NOT_ACCEPTABLE)
            try:
                family = Family.objects.filter(Q(user_id__in=[user])|Q(family_head=user)).distinct().first()
                print("################################",family)
            except:
                return Response({'status':0, "message":"Family associted with the user is not found"}, status=status.HTTP_406_NOT_ACCEPTABLE)
            try:
                service_provider = Service_provider.objects.get(service_provider_id=service_provider_id)
            except:
                return Response({'status':0, "message":"Service Provider with given id does not exist"}, status=status.HTTP_406_NOT_ACCEPTABLE)
            try:
                location = Location.objects.get(location_id=location_id)
            except:
                return Response({'status':0, "message":"Location with given id does not exist"}, status=status.HTTP_406_NOT_ACCEPTABLE)
    
            if user:
                # try:
                serializer = Appliances_Serializer(data = request.data)
                #print(serializer)
                if not serializer.is_valid():
                    if "mobile_number" in serializer.errors:
                                return Response({'status' : 0 ,'message' : serializer.errors['mobile_number'][0]},status=status.HTTP_406_NOT_ACCEPTABLE)
                    if "email_id" in serializer.errors:
                                return Response({'status' : 0 ,'message' : serializer.errors['email_id'][0]},status=status.HTTP_406_NOT_ACCEPTABLE)
                    print(serializer.errors)
                    return Response({'status' : 0 ,'message' : serializer.errors},status=status.HTTP_406_NOT_ACCEPTABLE)
                    
                else:
                    new_appliance = serializer.save(family_id=family, location_id=location, service_provider_id=service_provider, created_by=user)
                    print("$$$$$$$$$new_appliance$$$$$$$$$$$",new_appliance)
                    serializer = Appliances_Serializer(new_appliance) 
                    # new_Service_provider = serializer.save(family_id=family)
                    # serializer = Service_provider_Serializer(new_Service_provider) 
                    return Response({'data' : serializer.data,
                                    "status": 1,
                                    "message": "appliance data created successfully",
                                    "response_error": False},status=status.HTTP_201_CREATED)
            else:
                return Response({"status":0,"message":"user does not exist"},status = status.HTTP_401_UNAUTHORIZED) 
        else:
            return Response({"status":0,"message":"invalid API key."},status = status.HTTP_401_UNAUTHORIZED)

# all appliance by get
    def list(self,request):
        apikey =request.GET.get('apikey','test')
        if apikey.strip() == API_KEY.strip():
            token = request.META.get("HTTP_AUTHORIZATION")
            user = decrypt_token(token)  
            if user:
                try:
                    appliance = Appliances.objects.filter(Q(family_id__family_head=user) | Q(family_id__user_id__in=[user])).exclude(is_deleted=True).distinct()
                    # appliance = Appliances.objects.filter(created_by=user)
                    # family=Family.objects.get(family_head=user)
                    print("****************************",appliance)
                    #appliance = Appliances.objects.all()
                    if not appliance:
                        return Response({"status":0,"message":"no data found"},status=status.HTTP_404_NOT_FOUND)
                    else:
                        pass
                except:
                    return Response({"status":0,"message":"no data found"},status=status.HTTP_404_NOT_FOUND)

                serializer = Appliances_Serializer(appliance,many = True)
                print(serializer)

                return Response({'data': serializer.data,
                                    "status": 1,
                                    "message":"appliance data fetched successfully",
                                    "response_error": False
                                    },status=status.HTTP_200_OK)

            else:
                return Response({"status":0,"message":"user does not exist"},status = status.HTTP_401_UNAUTHORIZED)     
        else:
            return Response({"status":0,"message":"invalid API key."},status = status.HTTP_401_UNAUTHORIZED)

# update appliance with put
    def update(self,request,pk):
        apikey =request.GET.get('apikey','test')
        if apikey.strip() == API_KEY.strip():
            token = request.META.get("HTTP_AUTHORIZATION")
            user = decrypt_token(token)  
            service_provider_id = request.data.get('service_provider_id')
            location_id = request.data.get('location_id')
            if len(request.data.keys()) < 1:
                return Response({'status':0, "message":"There is no data in request body"}, status=status.HTTP_406_NOT_ACCEPTABLE)
            
            if user:
                try:
                    appliance = Appliances.objects.get(pk = pk, created_by=user)
                    serializer = Appliances_Serializer(instance=appliance,data=request.data,partial=True)
                    
                    if serializer.is_valid():
                        serializer.save(updated_by=user)
                        return Response({'data':serializer.data ,
                                        "status": 1,
                                        "message":"Appliance data Updated Successfully",
                                        "Response_error": False
                                        },status=status.HTTP_200_OK)
                    if "mobile_number" in serializer.errors:
                            return Response({'status' : 0 ,'message' : serializer.errors['mobile_number'][0]},status=status.HTTP_406_NOT_ACCEPTABLE)
                    if "email_id" in serializer.errors:
                            return Response({'status' : 0 ,'message' : serializer.errors['email_id'][0]},status=status.HTTP_406_NOT_ACCEPTABLE)

                    return Response({'data':{},'status': 0 , 'Errors' : serializer.errors},status=status.HTTP_400_BAD_REQUEST)
                
                except Location.DoesNotExist:
                    return Response({'status':0, "message": "Location with given id is not found"})
                
                except Service_provider.DoesNotExist:
                    return Response({'status':0, "message": "Service Provider with given id is not found"})

                except Exception as e:
                    print(e)
                    return Response({'status' : 0 , 'message': 'The Aplliances does not belong to you'},status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response({"status":0,"message":"User does not exist"},status = status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({"status":0,"message":"Invalid API Key."},status = status.HTTP_401_UNAUTHORIZED)
        
# find by id  appliance with get
    def retrieve(self, request, pk):
        apikey =request.GET.get('apikey','test')
        if apikey.strip() == API_KEY.strip():
            token = request.META.get("HTTP_AUTHORIZATION")
            user = decrypt_token(token)  
            if user:
                try:
                    if pk is not None:
                        appliance = Appliances.objects.get(pk=pk, created_by=user)
                        serializer = Appliances_Serializer(appliance)
                        return Response({'data': serializer.data,   
                                        "status": 1,
                                        "message": "appliance data by id fetched successfully",
                                        "response_error": False
                                        },status=status.HTTP_200_OK)
                
                    appliance = Appliances.objects.all()
                    serializer = Appliances_Serializer(appliance,many = True)
                    return Response({'status':0, 'data':serializer.data}, status= status.HTTP_200_OK)
                
                except Appliances.DoesNotExist:
                    return Response({'status':0, "message": "Appliances does not exist"}, status=status.HTTP_406_NOT_ACCEPTABLE)
                except Exception as e:
                    print(e)
                    return Response({'status' : 0 , 'message' : 'Internal Server Error'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response({"status":0,"message":"User does not exist"},status = status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({"status":0,"message":"Invalid API Key."},status = status.HTTP_401_UNAUTHORIZED)

# appliance  delete
    def destroy(self,request,pk):
        token = request.META.get("HTTP_AUTHORIZATION")
        user = decrypt_token(token)  
        if user:
            try:
                appliance = Appliances.objects.get(pk = pk, created_by=user)
                print(appliance)
                appliance.is_deleted = True
                appliance.active = False
                appliance.save()
                return Response({'status':0,'message':'data deleted'},status=status.HTTP_204_NO_CONTENT)
            
            except Appliances.DoesNotExist:
                    return Response({'status':0, "message": "Appliances does not exist"}, status=status.HTTP_406_NOT_ACCEPTABLE)
            except Exception as e:
                print(e)
                return Response({'status' : 0 , 'message' : 'Invalid id'},status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION) 
        else:
            return Response({"status":0,"message":"User does not exist"},status = status.HTTP_401_UNAUTHORIZED)
# TASK API
class TaskAPI(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = Task_serializers
    http_method_names = ['get','post','put','delete']
    lookup_body_field = 'pk'
    
# create task with post
    def create(self,request):
        token = request.META.get("HTTP_AUTHORIZATION")
        user = decrypt_token(token)
        service_provider_id = request.data.get('service_provider_id')
        location_id = request.data.get('location_id')
        family=Family.objects.filter(Q(user_id__in=[user])|Q(family_head=user)).distinct().last()
        print("################################",family)
        #location = Location.objects.filter(family_id__user_id__in=[user]).last()
        # service_provider = Service_provider.objects.get(service_provider_id=service_provider_id)
        # location_id = Location.objects.get(location_id=location_id)
        if user:
            # try:
            serializer = Task_serializers(data = request.data)
            #print(serializer)
            if not serializer.is_valid():
                print(serializer.errors)
                return Response({'status' : 406 ,'message' : serializer.errors},status=status.HTTP_406_NOT_ACCEPTABLE)
                
            else:
                task = serializer.save(family_id=family)
                print("$$$$$$$$$new_appliance$$$$$$$$$$$",task)
                serializer = Task_serializers(task) 
                # new_Service_provider = serializer.save(family_id=family)
                # serializer = Service_provider_Serializer(new_Service_provider) 
                return Response({'data' : serializer.data,
                                "status": 1,
                                "message": "Task Created successfully",
                                "Response_error": False},status=status.HTTP_201_CREATED)
        else:
            return Response({"status":0,"message":"User does not exist"},status = status.HTTP_401_UNAUTHORIZED)

# All Task Listing
    def list(self,request):
        apikey =request.GET.get('apikey','test')
        if apikey.strip() == API_KEY.strip():
            token = request.META.get("HTTP_AUTHORIZATION")
            user = decrypt_token(token)  
            if user:
                try:
                    task = Task.objects.filter(family_id__family_head=user).exclude(is_deleted=True).distinct()
                    family=Family.objects.get(Q(family_id__user_id__in=[user])|Q(family_id__family_head=user))
                    print("****************************",task)
                    if not task:
                        return Response({"status":0,"message":"No data Found"},status=status.HTTP_404_NOT_FOUND)
                    else:
                        pass
                except:
                    return Response({"status":0,"message":"No data Found"},status=status.HTTP_404_NOT_FOUND)

                serializer = Task_serializers(task,many = True)
                print(serializer)

                return Response({'data': serializer.data,
                                    "status":1,
                                    "message":"task all data fetched successfully",
                                    "response_error": False
                                    },status=status.HTTP_200_OK)

            else:
                return Response({"status":0,"message":"user does not exist"},status = status.HTTP_401_UNAUTHORIZED)     
        else:
            return Response({"status":0,"message":"invalid API key."},status = status.HTTP_401_UNAUTHORIZED)

# Update Task API
    def update(self,request,pk):
        apikey =request.GET.get('apikey','test')
        if apikey.strip() == API_KEY.strip():
            token = request.META.get("HTTP_AUTHORIZATION")
            user = decrypt_token(token)  
            if user:
                try:
                    task = Task.objects.get(pk = pk)
                    serializer = Task_serializers(instance=task,data=request.data,partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        return Response({"data":serializer.data ,
                                        "status":1,
                                        "message":"task data updated successfully",
                                        "response_error": False
                                        },status=status.HTTP_200_OK)
                    return Response({'data':{},'status': 0 , 'errors' : serializer.errors},status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    print(e)
                    return Response({'status' : 0 , 'message' :serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"status":0,"message":"user does not exist"},status = status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({"status":0,"message":"invalid API key."},status = status.HTTP_401_UNAUTHORIZED)
        
# Find Task By Id 
    # def retrieve(self, request, pk):
    #     apikey =request.GET.get('apikey','test')
    #     if apikey.strip() == API_KEY.strip():
    #         token = request.META.get("HTTP_AUTHORIZATION")
    #         user = decrypt_token(token)  
    #         if user:
    #             try:
    #                 if pk is not None:
    #                     appliance = Appliances.objects.get(pk=pk)
    #                     serializer = Appliances_Serializer(appliance)
    #                     return Response({'data': serializer.data,   
    #                                     "status": 1,
    #                                     "message": "Task data By Id fetched successfully",
    #                                     "response_error": False
    #                                     },status=status.HTTP_200_OK)
                
    #                 appliance = Appliances.objects.all()
    #                 serializer = Appliances_Serializer(appliance,many = True)
    #                 return Response(serializer.data)
    #             except Exception as e:
    #                 print(e)
    #                 return Response({'status' : 0 , 'message' :serializer.errors},status=status.HTTP_400_BAD_REQUEST)
    #         else:
    #             return Response({"status":0,"message":"User does not exist"},status = status.HTTP_401_UNAUTHORIZED)
    #     else:
    #         return Response({"status":0,"message":"Invalid API Key."},status = status.HTTP_401_UNAUTHORIZED)

# Delete Task  
    def destroy(self,request,pk):
        apikey =request.GET.get('apikey','test')
        if apikey.strip() == API_KEY.strip():
            token = request.META.get("HTTP_AUTHORIZATION")
            user = decrypt_token(token)  
            if user:
                try:
                    task = Task.objects.get(pk = pk)
                    # appliance.is_active = False
                    # appliance.delete()
                    # return Response({'status':0,'message':'data deleted'},status=status.HTTP_204_NO_CONTENT)
                    # task = Task.objects.get(pk = pk)
                    # print("@@@@@@@@@@@@@@@@@@@@@@@@",task)
                    # #task.is_deleted = True
                    if task.created_by == user:
                        task.is_deleted = True
                        task.save()
                        #task.delete()
                        #task.is_deleted = True
                        return Response({'status':1,'message':'task data deleted'},status=status.HTTP_204_NO_CONTENT)
                    else:
                        return Response({'status':0,'message':'you are not allowed to delete this task'},status=status.HTTP_401_UNAUTHORIZED)
                except Exception as e:
                    print(e)
                    return Response({'status' : 0 , 'message' : 'invalid id'},status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION) 
            else:
                return Response({"status":0,"message":"user does not exist"},status = status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({"status":0,"message":"Invalid API key."},status = status.HTTP_401_UNAUTHORIZED)
        

    # queryset = Task.objects.all()
    # serializer_class = Task_serializers
    # http_method_names = ['get','post','put','delete']

    # #add task by post
    # def create(self,request):
    #     token = request.META.get("HTTP_AUTHORIZATION")
    #     user = decrypt_token(token)  
    #     family = Family.objects.filter(user_id__in=[user]).last()
    #     print(family)
    #     # service_provider = Service_provider.objects.filter(family_id__user_id__in=[user]).last()
    #     # print(service_provider)
    #     if user:
    #         serializer = Task_serializers(data=request.data)
    #         if not serializer.is_valid():
    #                 print(serializer.errors)
    #                 return Response({'status' : 400 ,'message' :serializer.errors},status=status.HTTP_400_BAD_REQUEST)
                
                
    #         else:
    #             new_task = serializer.save(family_id=family,service_provider_id=service_provider)
    #             task = Task.objects.get(task_id = new_task.task_id) 
    #             return Response({'data' : serializer.data ,
    #                             "status_code": 200,
    #                             "status_message": "Task data fetched successfully",
    #                             "response_error": False},status=status.HTTP_200_OK)

    
     # all TASK by get
    def list(self,request):
        token = request.META.get("HTTP_AUTHORIZATION")
        user = decrypt_token(token)  
        if user:
            try:
                task = Task.objects.all()
                serializer = Task_serializers(task,many = True)
                print(serializer)
                return Response({'data': serializer.data,
                                "status": 1,
                                "message":"task data fetched successfully",
                                "response_error": False
                                },status=status.HTTP_200_OK)

            except:
                return Response({'data': {},'status':0,'message':serializer.errors},status=status.HTTP_400_BAD_REQUEST)         
        else:
            return Response({"status":0,"message":"user does not exist"},status = status.HTTP_401_UNAUTHORIZED)
    
    # update task with put
    def update(self,request,pk): 
        token = request.META.get("HTTP_AUTHORIZATION")
        user = decrypt_token(token)  
        if user:
            try:
                task = Task.objects.get(pk = pk)
                serializer = Task_serializers(instance=task,data=request.data,partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({'data':serializer.data ,
                                    "status": 1,
                                    "message":"task data updated successfully",
                                    "response_error": False
                                    })
                return Response({'data':{},'status': 0 ,'massage':serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                print(e)
                return Response({'status' : 0 , 'message' :serializer.errors},status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"status":0,"message":"user does not exist"},status = status.HTTP_401_UNAUTHORIZED)
    # task by id get
    def retrieve(self, request, pk):
        token = request.META.get("HTTP_AUTHORIZATION")
        user = decrypt_token(token)  
        if user:
            try:
                if pk is not None:
                    task = Task.objects.get(pk=pk)
                    serializer = Task_serializers(task)
                    return Response({'data': serializer.data,   
                                    "status": 1,
                                    "message": "task data fetched successfully",
                                    "response_error": False
                                    },status=status.HTTP_200_OK)

                task = Task_serializers.objects.all()
                serializer = Task_serializers(task,many = True)
                return Response(serializer.data)
            except Exception as e:
                print(e)
                return Response({'status' : 0 , 'message' : serializer.errors},status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"status":0,"message":"User does not exist"},status = status.HTTP_401_UNAUTHORIZED)
    
    # task  delete
    def destroy(self,request,pk):
        token = request.META.get("HTTP_AUTHORIZATION")
        user = decrypt_token(token)  
        if user:
            try:
                task = Task.objects.get(pk = pk)
                task.is_active = False
                task.delete()
                return Response({'status':0,'message':'data deleted'},status=status.HTTP_204_NO_CONTENT)
            except Exception as e:
                print(e)
                return Response({'status' : 0 , 'message' : 'invalid id'},status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"status":0,"message":"user does not exist"},status = status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
def fcm(request,id):
 
    if id is not None:
        # print('i m in if')
        # try:
            # print('i m in second try')
            device = FCMDevice.objects.get(user_id=id,type="android")
            
            # print('i m in device')
            print(device)
            status = device.send_message(Message
                                        (notification=Notification(title ="title" ,
                                            body="body of notification" ,
                                            image="url",)))
            # print(type(status))   
            # print('i m in status')
            print(status)
            return Response({'status' : str(status) , 'device' : str(device)})
        # except Exception as e:
        #     print(e)
        #     return Response({'status' : 500 , 'message' : 'invalid id'})

#SUBSCRIPTION API
class Subscription_PlanAPI(viewsets.ModelViewSet):
    queryset =  Subscription_Plan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    http_method_names = ['get','post','put','delete']
        

    # all SUBSCRIPTION by get
    def list(self,request):
        try:
            subscription = Subscription_Plan.objects.all()
            serializer = SubscriptionPlanSerializer(subscription,many = True)
            print(serializer)
            return Response({'data': serializer.data,
                            "status": 1,
                            "message":"subscription plan data fetched successfully",
                            "response_error": False
                            },status=status.HTTP_200_OK)

        except:
            return Response({'data': {},'status':0,'message':serializer.errors},status=status.HTTP_400_BAD_REQUEST)     

class SubscriptionPlanViewSet(viewsets.ModelViewSet):
    queryset = Subscription_Plan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    http_method_names = ['get']
    
    def list(self, request):
        apikey =request.GET.get('apikey','test')
        if apikey.strip() == API_KEY.strip():
            token = request.META.get("HTTP_AUTHORIZATION")
            user = decrypt_token(token)
            qs = Subscription_Plan.objects.all()
            print("==========================",qs)
            if qs:
                serializer = self.serializer_class(qs,many = True)
                return Response({"status":1,"message":"subscription plan list are:","data":serializer.data})
            else:
                return Response({"status":0,"message":"no data found"},status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"status":0,"message":"invalid API key."},status = status.HTTP_401_UNAUTHORIZED)

    # update SUBSCRIPTION by put
    def update(self,request,pk): 
        try:
            subscription = Subscription_Plan.objects.get(subscription_plan_id = pk)
            serializer = SubscriptionPlanSerializer(instance=subscription,data=request.data,partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'data':serializer.data ,
                                "status": 1,
                                "message":"task data updated successfully",
                                "response_error": False
                                },status=status.HTTP_200_OK)
            return Response({'data':{},'status': 0 , 'message' : serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({'status' : 0 , 'message' : serializer.errors},status=status.HTTP_404_NOT_FOUND)
                
    
    # find by id  SUBSCRIPTION with get
    def retrieve(self, request, pk):
        try:
            if pk is not None:
                subscription = Subscription_Plan.objects.get(pk=pk)
                serializer = SubscriptionPlanSerializer(subscription)
                return Response({'data': serializer.data,   
                                "status": 1,
                                "message": "appliance data fetched successfully",
                                "response_error": False
                                },status=status.HTTP_200_OK)
        
            subscription = Subscription_Plan.objects.all()
            serializer = SubscriptionPlanSerializer(subscription,many = True)
            return Response(serializer.data)
        except Exception as e:
            print(e)
            return Response({'status' : 0 , 'message' : serializer.errors},status=status.HTTP_404_NOT_FOUND)


class PaymentAPI(viewsets.ModelViewSet):
    queryset =  Payment.objects.all()
    serializer_class = Payment_serializers
    http_method_names = ['get']

    #all payment with get
    def list(self,request):
        token = request.META.get("HTTP_AUTHORIZATION")
        user = decrypt_token(token)
        if user :
            try:
                # payment = Payment.objects.filter(user_id=user)
                payment = Payment.objects.all()
                serializer = Payment_serializers(payment,many=True)
                return Response( serializer.data)
            except:
                return Response({"status":0,"message":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status":0,"message":serializer.errors},status=status.HTTP_400_BAD_REQUEST)


            
    #payment with put
    def retrieve(self,request,pk = None):
        subscription = Subscription_Plan.objects.get(subscription_plan_id=pk)
        # request.data is coming from frontend
        # amount = request.data['amount']
        amount = subscription.price
        # setup razorpay client this is the client to whome user is paying money that's you
        client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))
        print("client")

        # create razorpay order
        # the amount will come in 'paise' that means if we pass 50 amount will become
        # 0.5 rupees that means 50 paise so we have to convert it in rupees. So, we will 
        # mumtiply it by 100 so it will be 50 rupees.
        payment = client.order.create({"amount": int(amount) * 100, 
                                    "currency": "INR", 
                                    "payment_capture": "1"})
        # print(payment)

        # we are saving an order with isPaid=False because we've just initialized the order
        # we haven't received the money we will handle the payment succes in next 
        # function
        order = Order.objects.create(
                                    order_amount=amount, 
                                    data = payment)

        # serializer = Payment_serializers(order)

        """order response will be 
        {'id': 17, 
        'order_date': '23 January 2021 03:28 PM', 
        'order_product': '**product name from frontend**', 
        'order_amount': '**product amount from frontend**', 
        'order_payment_id': 'order_G3NhfSWWh5UfjQ', # it will be unique everytime
        'isPaid': False}"""

        data = {
            "payment": payment,
            "subscription plan":subscription.subscription_plan_name,
            "amount": amount
        }
        #return Response(data)
        return Response({"status":1,"message":"PaymentID generated :","data":data})
# @api_view(['POST'])
class handle_payment_successAPI(viewsets.ModelViewSet):
    queryset =  Payment.objects.all()
    serializer_class = Payment_serializers
    http_method_names = ['get','post','put','delete']


    def create(self, request):
        token = request.META.get("HTTP_AUTHORIZATION")
        user = decrypt_token(token)
        if user : 
            serializer = Payment_serializers(data = request.data)
            if not serializer.is_valid():
                    print(serializer.errors)
                    return Response({'status' : 0,'message' :serializer.errors},status=status.HTTP_400_BAD_REQUEST)

            else:
                new_payment = serializer.save(user_id=user)
                return Response({'data' : serializer.data,
                "status": 1,
                "message": "payment added successfully",
                "response_error": False},status=status.HTTP_200_OK)
    

#ROLE API
class RoleAPI(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = Role_serializers
    http_method_names = ['get','post','put','delete']

    #create permission by post
    def create(self, request):
        token = request.META.get("HTTP_AUTHORIZATION")
        user = decrypt_token(token)
        family = Family.objects.filter(user_id__in=[user]).last()
        print(family)
       

        if user : 
            serializer = Role_serializers(data = request.data)

            if not serializer.is_valid():
                    print(serializer.errors)
                    return Response({'status' : 0, 'message' :serializer.errors},status=status.HTTP_400_BAD_REQUEST)

            else:
                new_Role = serializer.save()
                role = Role.objects.get(role_id = new_Role.role_id) 
                return Response({'data' : serializer.data,
                "status": 1,
                "message": "permission data fetched fuccessfully",
                "response_error": False},status=status.HTTP_200_OK)
        else:
            return Response({"status":0,"message":serializer.errors},status=status.HTTP_400_BAD_REQUEST)


#User_Subscription API
class User_SubscriptionAPI(viewsets.ModelViewSet):
    queryset = User_Subscription.objects.all()
    serializer_class = User_Subscription_serializers
    http_method_names = ['get','post','put','delete']

    #create permission by post
    def create(self, request):
        token = request.META.get("HTTP_AUTHORIZATION")
        user = decrypt_token(token)
        print(user)
        family = Family.objects.filter(user_id__in=[user]).last()
        print("family",family)
        payment_id = Payment.objects.filter(user_id=user).last()
        print("payment",payment_id)
        # subscription_plan = Subscription_Plan.objects.filter(subscription_plan_id=subscription_plan).last()
        # print("subscription_plan_id",subscription_plan)


        if user : 
            serializer = User_Subscription_serializers(data = request.data)

            if not serializer.is_valid():
                    print(serializer.errors)
                    return Response({'status' : 0, 'message' :serializer.errors},status=status.HTTP_400_BAD_REQUEST)

            else:
                new_subscription = serializer.save(user_id=user,family_id=family,payment_id=payment_id)
                subscription = User_Subscription.objects.get(user_subscription_id = new_subscription.user_subscription_id) 
                return Response({'data' : serializer.data,
                "status": 1,
                "message": "subscription data fetched successfully",
                "response_error": False},status=status.HTTP_200_OK)
        else:
            return Response({"status":0,"message":serializer.errors},status=status.HTTP_400_BAD_REQUEST)

# PERMISSION API
class PermissionAPI(viewsets.ModelViewSet):
    queryset = Permissions.objects.all()
    serializer_class = Permissions_serializers
    http_method_names = ['get','post','put','delete']

    #create permission by post
    def create(self, request):
        token = request.META.get("HTTP_AUTHORIZATION")
        user = decrypt_token(token)
        family = Family.objects.filter(user_id__in=[user]).last()
        print(family)
        role = Role.objects.filter(user_id=[user]).last()
        print(role)

        if user : 
            serializer = Permissions_serializers(data = request.data)

            if not serializer.is_valid():
                    print(serializer.errors)
                    return Response({'status' : 0,'message' :serializer.errors},status=status.HTTP_400_BAD_REQUEST)

            else:
                new_permission = serializer.save(user_id=user,family_id=family,role="admin")
                permission = Permissions.objects.get(permission_id = new_permission.permission_id) 
                return Response({'data' : serializer.data,
                "status": 1,
                "message": "permission data fetched successfully",
                "response_error": False},status=status.HTTP_200_OK)
        else:
            return Response({"status":0,"message":serializer.errors},status=status.HTTP_400_BAD_REQUEST)

    # # update permission by post
    # def update(self,request,pk): 
    #     try:
    #         permission = Permissions.objects.get(role_id = pk)
    #         serializer = Permissions_serializers(instance=permission,data=request.data,partial=True
    #         )
    #         if serializer.is_valid():
    #             serializer.save()
    #             return Response({'data':serializer.data,
    #             "status_code": 200,
    #             "status_message": "permission data updated successfully",
    #             "response_error": False})
    #         return Response({'data':{},'status': 400, 'errors' : serializer.errors})

    #     except Exception as e:
    #         print(e)
    #         return Response({'status' : 404, 'errors' : 'invalid id'})

        
    
    # # find by id  permission with get
    # def retrieve(self, request, pk):
    #     try:
    #         if pk is not None:
    #             permission = Permissions.objects.get(pk=pk)
    #             serializer = Permissions_serializers(permission)
    #             return Response({'data': serializer.data,
    #             "status_code": 200,
    #             "status_message": "permissione data fetched successfully",
    #             "response_error": False})
    #     except Exception as e:
    #         print(e)
    #         return Response({'status' : 404, 'errors' : 'invalid id'})

     
    # permission  delete
    def destroy(self,request,pk):
        token = request.META.get("HTTP_AUTHORIZATION")
        user = decrypt_token(token)  
        if user:
            try:
                task = Permissions.objects.get(pk = pk)
                task.is_active = False
                task.delete()
                return Response({'status':0,'message':'data deleted'},status=status.HTTP_204_NO_CONTENT)
            except:
                return Response({'status' : 0 , 'message' : 'invalid id'},status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"status":0,"message":"User does not exist"},status = status.HTTP_401_UNAUTHORIZED)