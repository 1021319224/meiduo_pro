import json
import re
from django import http
from django.conf import settings
from django.contrib.auth import login, authenticate, logout
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from celery_tasks.email.tasks import send_verify_email
from meiduo_mall.utils import meiduo_signature
from meiduo_mall.utils.login import LoginRequiredMixin
from meiduo_mall.utils.response_code import RETCODE
from user import constants
from user.models import User


class RegisterView(View):
    """用户注册"""
    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        # username = request.POST.get('user_name')
        # password = request.POST.get('pwd')
        # password2 = request.POST.get('cpwd')
        # mobile = request.POST.get('phone')
        # allow = request.POST.get('allow')
        # sms_code = request.POST.get('msg_code')
        #
        #
        # # 判断参数是否齐全
        # if not all([username, password, password2, mobile, allow,sms_code]):
        #     return http.HttpResponseForbidden('缺少必要参数')
        # # 判断用户名是否符合要求
        # if not re.match(r'^[a-zA-Z0-9_-]{5,20}$',username):
        #     return http.HttpResponseForbidden('用户名格式不正确')
        # # 判断密码是否符合要求
        # if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
        #     return http.HttpResponseForbidden('密码格式不正确')
        # # 判断两次密码两次是否一致
        # if password != password2:
        #     return http.HttpResponseForbidden('两次密码输入不一致')
        # # 判断手机号是否合法
        # if not re.match(r'^1\d{10}$', mobile):
        #     return http.HttpResponseForbidden('请输入正确手机号码')
        #
        # user = User.objects.create_user(username=username, password=password,mobile=mobile,allow=allow)
        #
        # # except DatabaseError:
        # #     return render(request, 'register.html', {'register_errmsg':'注册失败'})
        #
        # # return http.HttpResponse(request, 'index.html')
        # login(request, user)
        #
        # return redirect('/')

        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        password2 = request.POST.get('cpwd')
        mobile = request.POST.get('phone')
        sms_code = request.POST.get('msg_code')
        allow = request.POST.get('allow')

        # 验证
        # 1.非空
        if not all([username, password, password2, mobile, sms_code, allow]):
            return http.HttpResponseForbidden('填写数据不完整')
        # 2.用户名
        if not re.match('^[a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseForbidden('用户名为5-20个字符')
        if User.objects.filter(username=username).count() > 0:
            return http.HttpResponseForbidden('用户名已经存在')
        # 密码
        if not re.match('^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden('密码为8-20个字符')
        # 确认密码
        if password != password2:
            return http.HttpResponseForbidden('两个密码不一致')
        # 手机号
        if not re.match('^1[3456789]\d{9}$', mobile):
            return http.HttpResponseForbidden('手机号错误')
        if User.objects.filter(mobile=mobile).count() > 0:
            return http.HttpResponseForbidden('手机号存在')
        # 短信验证码

        # 处理
        # 1.创建用户对象
        user = User.objects.create_user(
            username=username,
            password=password,
            mobile=mobile
        )
        # 2.状态保持
        login(request, user)

        # 响应
        return redirect('/login/')


class UsernameCountView(View):
    """验证用户名是否重复"""
    def get(self, request, username):
        count = User.objects.filter(username=username).count()
        return http.JsonResponse({
            'count': count,
            'code': RETCODE.OK,
            'errmsg': 'OK'
        })


class MobileCountView(View):
    """验证手机号是否重复"""
    def get(self,request,mobile):
        count = User.objects.filter(mobile=mobile).count()
        return http.JsonResponse({
            'count': count,
            'code': RETCODE.OK,
            'errmsg': 'OK'
        })


class LoginView(View):
    """
    用户登录
    """
    def get(self, request):
        """
        :param request: 　请求对象
        :return:  返回登陆模板
        """
        return render(request, 'login.html')

    def post(self, request):
        """
        :param request:
        :return:
        """

        username = request.POST.get('username')
        password = request.POST.get('pwd')
        remembered = request.POST.get('remembered')
        # next_url = request.GET.get('next','index')

        # 判断参数是否完整
        if not all([username,password]):
            return http.HttpResponseForbidden("缺少必要参数")
        # 判断用户名是否满足要求
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$',username):
            return http.HttpResponseForbidden('请输入正确用户名或手机号')
        # 判断密码是否符合
        if not re.match(r'[0-9A-Za-z]{8,20}',password):
            return http.HttpResponseForbidden("密码错误")

        # 认证用户登录
        user = authenticate(username= username,password=password)
        if user is None:
            return render(request, 'login.html', {'account_errmsg':'用户名或者密码错误'})
        # 实现状态保持
        login(request, user)
        # 设置状态保持的周期
        if remembered != 'on':
            # 没有记住用户，浏览器会话结束
            request.session.set_expiry(0)
        else:
            # 记住用户，None表示两周后过期
            request.session.set_expiry(None)

        # 响应注册结果
        response = redirect(reverse('contents:index'))
        response.set_cookie('username',user.username, max_age=3600*24*15)


        return response


class LogoutView(View):
    """退出登陆"""
    def get(self, request):

        logout(request)

        response = redirect(reverse('contents:index'))

        response.delete_cookie('username')

        return response

# class UserCenterInfoView(View):
#     def get(self, request):
#         if request.user.is_authenticated:
#
#             return render(request, 'user_center_info.html')
#         else:
#             return redirect(reverse('user:login'))
class UserCenterInfoView(LoginRequiredMixin,View):
    """
    用户中心
    """
    def get(self,request):
        return render(request,'user_center_info.html')

class EmailView(LoginRequiredMixin,View):
    def put(self,request):
        # 接受
        json_dict = json.loads(request.body.decode())
        email = json_dict.get('email')
        # 验证
        if not all([email]):
            return http.JsonResponse({'code': RETCODE.EMAILERR, 'errmsg': "邮箱错误"})
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return http.JsonResponse({'code': RETCODE.EMAILERR, 'errmsg': "邮箱格式错误"})
        # 处理
        user = request.user
        user.email = email
        user.save()



        # 生成激活链接地址
        token = meiduo_signature.dumps({'user_id':user.id},constants.EMAIL_ACTIVE_EXPIRES)
        verify_url = settings.EMAIL_VERIFY_URL + '?token=' + token

        # subject = "美多商城邮箱验证"
        # from_email = settings.EMAIL_FROM
        # html_message = '<p>尊敬的用户您好！</p><p>感谢您使用美多商城。</p><p>您的邮箱为：%s 。请点击此链接激活您的邮箱：' \
        #                '</p><p><a href="%s">%s</a></p>' % (email, verify_url, verify_url)
        # send_mail(subject, '', from_email, [email], html_message=html_message)



        # 异步发送验证邮件
        send_verify_email.delay(to_email=email,verify_url=verify_url)
        # 响应
        return http.JsonResponse({'code':RETCODE.OK,'errmsg':"OK"})

class EmailActiveView():

    def get(self,request):

        # 接受
        token = request.GET.get('token')
        # 验证
        if not all([token]):
            return http.HttpResponseForbidden('参数无效')
        # 解密 获取用户编号
        json_dict = meiduo_signature.loads(token,constants.EMAIL_ACTIVE_EXPIRES)
        if json_dict is None:
            return http.HttpResponseForbidden('激活信息无效')
        user_id = json_dict.get('user_id')
        # 处理
        try:
            user = User.objects.get(pk = user_id)
        except:
            return http.HttpResponseForbidden('用户无效')
        user.email_active = True
        user.save()

        # 返回
        return redirect('/info/')

    class AddressView(LoginRequiredMixin,View):
        def get(self,request):
            pass








