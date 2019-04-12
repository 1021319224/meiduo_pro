from itsdangerous.jws import TimedJSONWebSignatureSerializer
from django.conf import settings


def dumps(json,expires):
    """
    将字典加密，返回加密字符串
    :param json:
    :param expires:
    :return:
    """
    serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY,expires_in=expires)
    json_str = serializer.dumps(json).decode()
    return json_str

def loads(json_str,expires):
    """
    将加密字符串解密
    :param json_str:
    :param expires:
    :return:
    """
    serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY,expires_in=expires)
    try:
        json = serializer.loads(json_str)
    except:
        # 如果字符串被修改过，或超期，会抛出异常
        return None
    else:
        return json