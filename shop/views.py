from django.shortcuts import render


def main(request):
    return render(request, 'home.html')


def server(request):
    return render(request, 'server.html')


def beauty(request):
    return render(request, 'beauty.html')


def shopcart(request):
    return render(request, 'shopcart.html')


def customer(request):
    return render(request, 'customer.html')


def login(request):
	return render(request, 'login.html')


def register(request):
    return render(request, 'register.html')
