
import os
from celery import Celery
os.environ["DJANGO_SETTINGS_MODULE"] = "meiduo_mall.setting.dev"
# 创建实例
celery_app = Celery('meiduo')

# 加载配置
celery_app.config_from_object('celery_tasks.config')

# 进行注册
celery_app.autodiscover_tasks(['celery_tasks.sms','celery_tasks.email'])


