import random
from django.http.response import HttpResponseForbidden,JsonResponse,HttpResponse
from django.shortcuts import render
# Create your views here.
from django.views import View
from django_redis import get_redis_connection
from meiduo_mall.libs.yuntongxun.sms import CCP
from . import constants
from meiduo_mall.libs.captcha.captcha import captcha
from meiduo_mall.utils.response_code import RETCODE
from celery_tasks.sms.tasks import ccp_send_sms


class ImageCodeView(View):
    # 生成验证码　captcha.generate_captcha()
    def get(self, request, uuid):

        text, code, image = captcha.generate_captcha()
        print(uuid)
        redis_cli = get_redis_connection('image_code')
        redis_cli.setex(uuid, constants.IMAGE_CODE_EXPIRES, code)
        return HttpResponse(image, content_type='image/png')


class SMSCodeView(View):
    def get(self, request, mobile):
        # 接受参数
        image_code_client = request.GET.get('image_code')
        print('===============',request.GET)

        uuid = request.GET.get('image_code_id')
        print(uuid)
        # 校验参数
        if not all([image_code_client, uuid]):
            return JsonResponse({'code':RETCODE.NECESSARYPARAMERR,'errmsg':'缺少必要参数'})

        # 创建对象连接到数据库
        redis_conn = get_redis_connection('sms_code')

        # 判断是否发送短信过于频繁
        # send_flag = redis_conn.get(mobile + '_flag')
        # print('oooooooooooooooooooooooooooooo', send_flag)
        # if send_flag:
        #     # return http.JsonResponse({'code':RETCODE.THROTTLINGERR, 'errmsg':"发送短信过于频繁"})
        #     return HttpResponseForbidden('送短信过于频繁')
        # 提取图形验证码
        redis_cli=get_redis_connection('image_code')
        image_code_server = redis_cli.get(uuid)
        if image_code_server is None:
            # 验证码过期或者不存在
            # return http.JsonResponse({'code':RETCODE.IMAGECODEERR, 'errmsg':'图形验证码失效'})
            return HttpResponseForbidden('图形验证码失效')
        # 对比图形验证码
        image_code_server = image_code_server.decode()
        if image_code_client.lower() != image_code_server.lower():
            # return http.JsonResponse({'code':RETCODE.IMAGECODEERR, 'errmsg':'图形验证码验证失败'})
            return HttpResponseForbidden('图形验证码验证失败')

        # 生成短信验证码
        sms_code = '%06d' %random.randint(0, 999999)
        print(sms_code)

        # 优化使用管道
        redis_pl = redis_conn.pipeline()
        redis_pl.setex(mobile, constants.SMS_CODE_EXPIRES, sms_code)
        redis_pl.setex(mobile + '_flag', constants.SMS_CODE_FLAG, 1)

        redis_pl.execute()

        # # 保存短信验证码
        # redis_conn.setex('sms_%s' % mobile, constants.SMS_CODE_EXPIRES//60, sms_code)
        # CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_EXPIRES//60], constants.SEND_SMS_TEMPLATE_ID)


        ccp_send_sms.delay(mobile,sms_code)
        # 响应结果
        return JsonResponse({'code': RETCODE.OK, 'errmsg': '发送短信成功'})