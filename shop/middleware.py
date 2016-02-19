from django.shortcuts import redirect
from shop.models import Shopcart, MessageLog, Message
from main.settings import WECHAT_APPID
from urllib import quote

from shop.models import CustomerConnect


class WxMiddleware(object):
	def process_request(self, request):
		if (not request.path.startswith('/admin')) and (not request.path.startswith('/ckeditor')) and (not request.path.startswith('/wxpay_notify/')) and 'code' not in request.GET and 'state' not in request.GET and 'openid' not in request.session:
			return redirect('https://open.weixin.qq.com/connect/oauth2/authorize?appid=%s&redirect_uri=%s&response_type=code&scope=snsapi_userinfo&state=%s#wechat_redirect'%(WECHAT_APPID, quote('http://shop.baremeii.com/wx_callback/'),request.path))

class TipMiddleware(object):
	def process_response(self, request, response):
		num = 0
		msg = 0
		if 'customer' in request.session:
			try:
				shopcart_product = Shopcart.objects.get(customer__id=request.session['customer']['id'])
				num = shopcart_product.products.count()
			except:
				pass
			try:
				message_log = MessageLog.objects.get(customer__id=request.session['customer']['id'])
				msg = Message.objects.filter(customer__id=request.session['customer']['id'],update_at__qt=message_log.last_visite_at).count()
			except:
				pass


		elif 'shopcart' in request.session:
			num = len(request.session['shopcart']['products_list'])

		response.set_cookie('message_num', msg)
		response.set_cookie('shopcart_num', num)
		return response
		
