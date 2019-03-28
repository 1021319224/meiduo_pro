import re
from user.models import User
from django.contrib.auth.backends import ModelBackend


class MeiduoModelBackend(ModelBackend):
    '''多用户登陆'''
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            if re.match(r'1[3-9]\d{9}$',username):
                user= User.objects.get(mobile=username)

            else:
                user = User.objects.get(username=username)
        except:
            return None


        if user.check_password(password):
            return user
        else:
            return None