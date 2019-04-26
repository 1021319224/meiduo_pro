import re

from django import http
from django.contrib.auth import login
from django.shortcuts import render, redirect

# Create your views here.
from QQLoginTool.QQtool import OAuthQQ
from django.views import View

# oauth = OAuthQQ()
from django_redis import get_redis_connection

from django.conf import settings
from pymysql import DatabaseError

from meiduo_mall.utils.loggers import logger
from meiduo_mall.utils.meiduo_signature import dumps,loads
from meiduo_mall.utils.response_code import RETCODE
from oauth import constants
from oauth.models import OAuthQQUser
from user.models import User

class OAuthQQURLView(View):

    def get(self,request):
        next = request.GET.get('next')
        # 创建ｑｑ登陆对象
        oauth = OAuthQQ(
            client_id=settings.QQ_CLIENT_ID,
            client_secret = settings.QQ_CLIENT_SECRET,
            redirect_uri= settings.QQ_REDIRECT_URI,
            state=next
        )
        # 生成授权地址
        login_url = oauth.get_qq_url()
        print(login_url)
        return http.JsonResponse({'code':RETCODE.OK,'errmsg':'OK','login_url':login_url})


class OAuthUserView(View):

    "用户扫码登陆的回调处理"
    def get(self,request):
        """Oauth2.0 认证"""
        # 提取code参数
        code = request.GET.get('code')
        next = request.GET.get('next')
        #
        # if not code:
        #     return http.HttpResponseForbidden('缺少code')
        #  创建工具对象
        oauth = OAuthQQ(
            client_id=settings.QQ_CLIENT_ID,
            client_secret=settings.QQ_CLIENT_SECRET,
            redirect_uri=settings.QQ_REDIRECT_URI,
            state=next
        )
        # 1. 使用code向QQ服务器请求access_token
        access_token = oauth.get_access_token(code)
        # 2. 使用access_token向服务器请求openid
        openid = oauth.get_open_id(access_token=access_token)
        # 判断是否初次授权
        try:
            # 如果存在,保持登录，重定向到首页,将用户名存入到cooike中
            qq_user = OAuthQQUser.objects.get(openid = openid)


        except OAuthQQUser.DoesNotExist:
            #  初次绑定，未查询到数据
            # access_token = generate_access_token(openid)
            json_str = dumps({"openid":openid}, constants.OPENID_EXPIRES)
            context = {'token':json_str}
            return render(request,'oauth_callback.html',context)
        else:
            # 查询到授权对象，则状态保持，转到相关页面
            qq_user = qq_user.user
            login(request, qq_user)
            response = redirect(reversed('contents:index'))
            response.set_cookie('username', qq_user.username,max_age=3600*24*60)
            return response

        #return http.HttpResponseServerError('OAuth2.0认证失败')

    "美多商城用户绑定到openid"

    def post(self,request):
        # 接受参数 openid mobile,password,sms_code
        access_token = request.POST.get('access_token')
        username = request.POST.get('username')
        password = request.POST.get('pwd')
        mobile = request.POST.get('mobile')
        state = request.GET.get('state','/')
        print(request.POST)
        openid_dict = loads(access_token,constants.OPENID_EXPIRES)
        print(openid_dict)
        if openid_dict is None:
            return http.HttpResponseForbidden('授权信息已经过期，请重新授权')
        openid = openid_dict.get('openid')
        # 验证参数
        # 处理
        try:
            user = User.objects.get(mobile=mobile)
        except :
            # 初次授权
            user = User.objects.create(mobile,password=password,mobile=mobile)
        else:
            # 非初次授权
            if not user.check_password(password):
                return http.HttpResponseForbidden("密码错误")

        # 绑定
        qquser = OAuthQQUser.objects.create(
            user = user,
            openid=openid
        )
        # 状态保持
        login(request,user)
        response = redirect(state)
        response.set_cookie('username',user.username)
        # 响应
        return response