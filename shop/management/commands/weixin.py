# coding:utf8
from django.core.management.base import BaseCommand, CommandError
from shop.utils import build_downloadall
from shop.models import Order

import requests, xmltodict
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'get all weixin pay order'

    def handle(self, *args, **options):
        date = (datetime.today() - timedelta(days=0)).strftime("%Y%m%d")
        print date
        self.stdout.write('start download all bill')
        headers = {'Content-Type': 'application/xml'}
        response = requests.post('https://api.mch.weixin.qq.com/pay/downloadbill', data=build_downloadall({'bill_date':date,'bill_type':'ALL'}), headers=headers)
        response.encoding = 'utf-8'
        i = 0
        data = []
        for l in response.text.split("\n"):
            if i!=0:
                self.stdout.write(l)
                arr = l.split(",")
                if len(arr) == 24:
                    data.append({'order_txt':arr[6].strip('`'),'status':arr[9].strip('`'),'fee':arr[12].strip('`')})
            i += 1

        if len(data):
            for row in data:
                if row['status'] == 'SUCCESS':
                    try:
                        order = Order.objects.get(order_txt=row['order_txt'])
                        order.status = 3
                        if "%0.2f"%float(order.total_price) == row['fee']:
                            order.wxstatus = 1
                        else:
                            order.wxstatus = 2

                        order.save()
                    except:
                        pass
