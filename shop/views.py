from django.shortcuts import render


def main(request):
    return render(request, 'shop/home.html')


def server(request):
    return render(request, 'shop/server.html')
