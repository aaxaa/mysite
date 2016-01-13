# coding:utf8
from django.core.management.base import BaseCommand, CommandError
from main.settings import EMAY_KEY, EMAY_PWD, EMAY_SN

import requests, xmltodict


class Command(BaseCommand):
	help = 'use for emay sms accout'

	def add_arguments(self, parser):
		parser.add_argument('--register',
			action='store_true',
			dest='register',
			default=False,
			help="register emay accout")

		parser.add_argument('--registerdetail',
			action='store_true',
			dest='registerdetail',
			default=False,
			help="post register detail for emay accout")

		parser.add_argument('--message',
			dest='message',
			default=False,
			help="a message text want to send")

		parser.add_argument('--phone',
			dest='phone',
			default=False,
			help="a phone number to send message")


	def handle(self, *args, **options):
		if options['register']:
			r = requests.post('http://hprpt2.eucp.b2m.cn:8080/sdkproxy/regist.action', data={'cdkey':EMAY_KEY,'password':EMAY_PWD})
			if int(r.status_code) == 200:
				data = xmltodict.parse(r.text.strip())
				if int(data['response']['error'])==0:
					self.stdout.write(self.style.SUCCESS('register success!'))
				else:
					self.stdout.write('register error: %s'%data['response']['message'])
			else:
				self.stdout.write('request get a %s response' % status_code)
		elif options['registerdetail']:
			r = requests.post('http://hprpt2.eucp.b2m.cn:8080/sdkproxy/registdetailinfo.action', data={
				'cdkey':EMAY_KEY,
				'password':EMAY_PWD,
				'ename':u'顺德容桂贝尔美医疗美容专科医院',
				'linkman':u'梁添荣',
				'phonenum':'0757-28298577',
				'mobile':'15602209800',
				'email':'15602209800@163.com',
				'fax':'0757-28301268',
				'address':u'广东省佛山市顺德区容桂南区工业区新容西路19号',
				'postcode':'528305'
			})
			if int(r.status_code) == 200:
				data = xmltodict.parse(r.text.strip())
				if int(data['response']['error'])==0:
					self.stdout.write(self.style.SUCCESS('register success!'))
				else:
					self.stdout.write('register error: %s'%data['response']['message'])
			else:
				self.stdout.write('request get a %s response' % status_code)
		else:
			if options['message'] != '' and options['phone'] != '':
				r = requests.post('http://hprpt2.eucp.b2m.cn:8080/sdkproxy/sendsms.action', data={
					'cdkey':EMAY_KEY,
					'password':EMAY_PWD,
					'phone':options['phone'],
					'message':"%s%s"%(EMAY_SN, options['message'])
				})
			if int(r.status_code) == 200:
				data = xmltodict.parse(r.text.strip())
				if int(data['response']['error'])==0:
					self.stdout.write(self.style.SUCCESS('register success!'))
				else:
					self.stdout.write('register error: %s'%data['response']['message'])
			else:
				self.stdout.write('request get a %s response' % status_code)
