from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
# def about(request):
# ...
def about_us(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/about_us.html', context)


# Create a `contact` view to return a static contact page
def contact_us(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/contact_us.html', context)

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/login.html', context)
    elif request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('psw')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"You are now logged in as {username}")
            return redirect('djangoapp:index')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('djangoapp:login')

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    context = {}
    if request.method == 'GET':
        logout(request)
        messages.success(request, "You have successfully logged out.")
        return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('psw')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        # check user already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, f"Username already exists.")
            return redirect('djangoapp:registration')
        # check if password is valid
        if len(password) < 6:
            messages.error(request, f"Password must be at least 6 characters.")
            return redirect('djangoapp:registration')
        
        user = User.objects.create_user(username=username, password=password, first_name=first_name, last_name=last_name)
        user.save()
        # login after registration
        login(request, user)
        messages.success(request, f"New account created: {username}")
        return redirect('djangoapp:index')

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    if request.method == "GET":
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/gustavo%40novahub.com.br_dev/default/get-dealership.json"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        # Concat all dealer's short name
        #dealer_names = '<br>'.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        return render(request, 'djangoapp/index.html', {'dealerships': dealerships})


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    if request.method == "GET":
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/gustavo%40novahub.com.br_dev/default/get-review-python.json"
        # Get dealers from the URL
        reviews = get_dealer_reviews_from_cf(url, dealer_id)
        # Concat all dealer's short name
        #dealer_names = '<br>'.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        return render(request, 'djangoapp/dealer_details.html', {'reviews': reviews, 'dealer_id': dealer_id})

# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
# ...

