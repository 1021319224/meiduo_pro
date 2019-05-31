# bind: 保证task对象会作为第一个参数自动传入
# name :异步任务别名
# retry_backoff：异常自动充实的时间间隔，第Ｎ次（retry_backoff*2^(n-1)）s
# max_retries：异常自动重试次数的上限
from django.conf import settings

from celery_tasks.main import celery_app
from django.core.mail import send_mail

from meiduo_mall.utils import loggers


@celery_app.task(bind=True, name='send_verify_email', retry_backoff=3)
def send_verify_email(self, to_email, verify_url):
    subject = "美多商城邮箱验证"
    from_email = settings.EMAIL_FROM
    html_message = '<p>尊敬的用户您好！</p><p>感谢您使用美多商城。</p><p>您的邮箱为：%s 。请点击此链接激活您的邮箱：' \
                   '</p><p><a href="%s">%s</a></p>' % (to_email, verify_url, verify_url)
    try:
        send_mail(subject, '', from_email, [to_email], html_message=html_message)
    except Exception as e:
        loggers.logger.error(e)
        raise self.retry(exc=e, max_retries=3)
