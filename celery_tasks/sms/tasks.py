#bind: 保证task对象会作为第一个参数自动传入
#name :异步任务别名
#retry_backoff：异常自动充实的时间间隔，第Ｎ次（retry_backoff*2^(n-1)）s
#max_retries：异常自动重试次数的上限
from meiduo_mall.libs.yuntongxun.sms import CCP
# from . import constants
# from meiduo_mall.utils import logger
from celery_tasks.main import celery_app


@celery_app.task(bind=True)
def ccp_send_sms(self, mobile, sms_code):
    print('---------------------------------')
    ccp=CCP()
    send_ret = ccp.send_template_sms(str(mobile),[str(sms_code),5],1)
    print(send_ret)
    return send_ret
    # try:
    #     send_ret = CCP().send_template_sms(mobile, [sms_code, 5],1)
    # except Exception as e:
    #     # logger.logger.error(e)
    #     print(e)
    #
    #     raise self.retry(exc=e, max_retries=3)
    # if send_ret != 0:
    #     raise self.retry(exc=Exception('发送短信失败'), max_retries=3)




