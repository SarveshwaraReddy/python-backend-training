from django.shortcuts import render


def home(request):
    return render(request, 'employees/home.html')


def about(request):
    return render(request, 'employees/about.html')


def contact(request):
    return render(request, 'employees/contact.html')
