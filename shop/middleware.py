from django.shortcuts import redirect
from main.settings import WECHAT_APPID, WECHAT_APPSECRET
import requests

class WxMiddleware(object):
	def process_request(self, request):
		if 'customer' not in request.session:
			if request.GET.get('state','') == 'a1b2c3':
				r = requests.get('https://api.weixin.qq.com/sns/oauth2/access_token?appid=%s&secret=%s&code=%s&grant_type=authorization_code'%(WECHAT_APPID, WECHAT_APPSECRET, request.GET.get('code')))
				if int(r.status_code) == 200:
					data = r.json()

					r2 = requests.get('https://api.weixin.qq.com/sns/userinfo?access_token=%s&openid=%s&lang=zh_CN'%(data['access_token'], data['openid']))

					if int(r2.status_code) == 200:
						print r.json()

			else:
				return redirect('https://open.weixin.qq.com/connect/oauth2/authorize?appid=APPID&redirect_uri=%s&response_type=code&scope=snsapi_userinfo&state=a1b2c3#wechat_redirect'%(WECHAT_APPID))
			
