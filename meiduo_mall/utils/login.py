from django.contrib.auth.decorators import login_required
from django import views


class LoginRequiredMixin(object):
    """验证用户是否登陆拓展类"""

    @classmethod
    def as_view(cls,**initkwargs):
        view = super().as_view()
        return login_required(view)

