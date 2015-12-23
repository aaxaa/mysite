from django.shortcuts import render


def main(request):
    return render(request, 'shop/home.html')


def server(request):
    return render(request, 'shop/server.html')


def beauty(request):
    return render(request, 'shop/beauty.html')


def shopcart(request):
    return render(request, 'shop/shopcart.html')


def customer(request):
    return render(request, 'shop/customer.html')


def register(request):
    return render(request, 'shop/register.html')
