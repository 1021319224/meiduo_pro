from django.shortcuts import render

# Create your views here.
from django.views import View


class IndexView(View):
    """首页显示"""
    def get(self, request):
        """提供首页广告界面"""
        context = {
            'categories':[],
            'contents':[]
        }
        return render(request,'index.html')