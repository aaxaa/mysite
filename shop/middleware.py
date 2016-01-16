from django.shortcuts import redirect
from main.settings import WECHAT_APPID
from urllib import quote

from shop.models import CustomerConnect


class WxMiddleware(object):
	def process_request(self, request):
		if (not request.path.startswith('/admin/')) and 'code' not in request.GET and 'state' not in request.GET:
			if 'openid' in request.session and request.session['openid']:
				customer_connect = CustomerConnect.objects.get(openid=request.session['openid'])
				#del request.session['openid']
				if not customer_connect.customer:
					return redirect('https://open.weixin.qq.com/connect/oauth2/authorize?appid=%s&redirect_uri=%s&response_type=code&scope=snsapi_userinfo&state=%s#wechat_redirect'%(WECHAT_APPID, quote('http://shop.baremeii.com/wx_callback/'),request.path))
			else:
				return redirect('https://open.weixin.qq.com/connect/oauth2/authorize?appid=%s&redirect_uri=%s&response_type=code&scope=snsapi_userinfo&state=%s#wechat_redirect'%(WECHAT_APPID, quote('http://shop.baremeii.com/wx_callback/'),request.path))
		
