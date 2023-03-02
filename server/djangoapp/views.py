from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import os
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
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
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/" + os.environ['IBM_URL_DOMAIN'] + "/default/get-dealership.json"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        
        # Concat all dealer's short name
        #dealer_names = '<br>'.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        return render(request, 'djangoapp/index.html', {'dealerships': dealerships})


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    if request.method == "GET":
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/" + os.environ['IBM_URL_DOMAIN'] + "/default/get-review-python.json"
        # Get dealers from the URL
        reviews = get_dealer_reviews_from_cf(url, dealer_id)
        for review in reviews:
            review.sentiment_escaped = review.sentiment['label']
        
        return render(request, 'djangoapp/dealer_details.html', {'reviews': reviews, 'dealer_id': dealer_id})

# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    if request.method == "GET":
        return render(request, 'djangoapp/add_review.html', {'dealer_id': dealer_id})
    elif request.method == "POST":
        # CHECK USER LOGIN
        if not request.user.is_authenticated:
            messages.error(request, "You must login to submit a review.")
            return redirect('djangoapp:login')
        review = {}
        review["name"] = request.POST.get('name')
        review["dealership"] = dealer_id
        review["review"] = request.POST.get('review')
        review["purchase"] = 0
        review["another"] = ""
        review["purchase_date"] = "2021-12-01"
        review["car_make"] = "Toyota"
        review["car_model"] = "Corolla"
        review["car_year"] = 2020
        review["IAM_API_KEY"] = os.environ['CLOUDANT_APIKEY']
        review["COUCH_URL"] = "https://" + os.environ['CLOUDANT_URL_KEY'] + ".cloudantnosqldb.appdomain.cloud"

        json_payload = review
        
        #review["sentiment"] = ""
        #review["id"] = 0
        #review["purchase_date"] = datetime.strptime(review["purchase_date"], '%Y-%m-%d').strftime('%m/%d/%Y')
        url = "https://us-south.functions.cloud.ibm.com/api/v1/namespaces/" + os.environ['IBM_URL_DOMAIN'] + "/actions/add-review"
        # Get dealers from the URL
        couch_url = "https://" + os.environ['CLOUDANT_URL_KEY'] + ".cloudantnosqldb.appdomain.cloud"
        response = post_request(url, json_payload, IAM_API_KEY=os.environ['CLOUDANT_APIKEY'], COUCH_URL=couch_url)

        return redirect("djangoapp:dealer_details", dealer_id=dealer_id)

        #if response.status_code == 204:
        #    messages.success(request, "Review added successfully.")
        #else:
        #    print(response.text)
        #    messages.error(request, "There was an error adding your review.")

        return redirect('djangoapp:dealer_details', dealer_id=dealer_id)

