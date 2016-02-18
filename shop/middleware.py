from django.shortcuts import redirect
from main.settings import WECHAT_APPID
from urllib import quote

from shop.models import CustomerConnect


class WxMiddleware(object):
	def process_request(self, request):
		if (not request.path.startswith('/admin')) and (not request.path.startswith('/ckeditor')) and (not request.path.startswith('/wxpay_notify/')) and 'code' not in request.GET and 'state' not in request.GET and 'openid' not in request.session:
			return redirect('https://open.weixin.qq.com/connect/oauth2/authorize?appid=%s&redirect_uri=%s&response_type=code&scope=snsapi_userinfo&state=%s#wechat_redirect'%(WECHAT_APPID, quote('http://shop.baremeii.com/wx_callback/'),request.path))

class TipMiddleware(object):
	def process_template_response(self, request, response):
		response.context_data.update({'message_num':2, 'shopcart_num':2})
		return response
		
