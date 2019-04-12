from django.conf.urls import url
from . import views

urlpatterns = [

    url(r'^qq/login/$', views.OAuthQQURLView.as_view()),
    url(r'^oauth_callback/$',views.OAuthUserView.as_view()),

]