from functools import partial
#from api.admin import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.backends import TokenBackend
from api.models import User

def create_token(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh)

def decrypt_token(token):
    try:
        valid_data = TokenBackend(algorithm='HS256').decode(str(token),verify=False)
        user = valid_data
        user_id = user['user_id']
        try:
            user = User.objects.get(pk =user_id )
            return user
        except:
            return 0
    except:
        return 0