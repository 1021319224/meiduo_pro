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
from meiduo_mall.utils.loggers import logger
from meiduo_mall.utils.response_code import RETCODE
from oauth.models import OAuthQQUser


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
        print(request.GET)

        if not code:
            return http.HttpResponseForbidden('缺少code')
        #  创建工具对象
        oauth = OAuthQQ(
            client_id=settings.QQ_CLIENT_ID,
            client_secret=settings.QQ_CLIENT_SECRET,
            redirect_uri=settings.QQ_REDIRECT_URI,
            state=next
        )

        # 1. 使用code向QQ服务器请求access_token
        access_token = oauth.get_access_token(code)
        print("access_token",access_token)
        # 2. 使用access_token向服务器请求openid
        openid = oauth.get_open_id(access_token=access_token)
        print("openid",openid)
        # 判断是否初次授权
        try:
            # 如果存在,保持登录，重定向到首页,将用户名存入到cooike中
            qq_user = OAuthQQUser.objects.get(openid = openid)

        except OAuthQQUser.DoesNotExist:
            #  初次绑定，未查询到数据
            # access_token = generate_access_token(openid)
            context = {'access_token':access_token}
            return render(request,'oauth_callback.html',context)
        else:
            qq_user = OAuthQQUser.user
            login(request, qq_user)
            response = redirect(reversed('contents:index'))
            response.set_cookie('username', qq_user.username,max_age=3600*24*60)
            return response

        #return http.HttpResponseServerError('OAuth2.0认证失败')

    def post(self, request):
        '''美多商城用户绑定到openid'''

        # 接受参数
        mobile = request.GET.get('mobile')
        pwd = request.GET.get('pwd')
        sms_code_client = request.POST.get('sms_code')
        access_token = request.POST.get('access_token')

        # 校验参数
        # 判断参数是否齐全
        if not all([mobile,pwd,sms_code_client]):
            return http.HttpResponseForbidden('缺少必要参数')
        # 判断手机号是否合法
        if not re.match(r'^1[3-9]\d{9}$',mobile):
            return http.HttpResponseForbidden('请输入正确手机号')
        # 判断密码是否合格
        if not re.match(r'^[0-9A-Za-z]{8,20}$',pwd):
            return http.HttpResponseForbidden('请输入8-20位的密码')
        # 判断短信验证码是否一致
        redis_conn = get_redis_connection('verify_code')
        sms_code_server = redis_conn.get('sms_%s' % mobile)
        if sms_code_client is None:
            return render(request,'oauth_callback.html',{'sms_code_errmsg':'无效的短信验证码'})
        if sms_code_client != sms_code_server.decode():
            return http.HttpResponseForbidden(request,'oauth_callback.html',{'sms_code_errmsg':'验证码不正确'})
        # 判断openid是否有效：错误提示放在sms_code_errmsg位置
        # openid = check_access_token(access_token)

        # 保存数据
        # 将用户绑定openid
        # 实现状态保持
        # 响应绑定结果
        # 登录时用户名写入到cookie,有效期15天