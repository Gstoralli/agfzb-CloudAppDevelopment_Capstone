import requests
import json
import os
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth


# Create a `get_request` to make HTTP GET requests
def get_request(url, **kwargs):
    #print(kwargs)
    #print("GET from {} ".format(url))
    try:
        # Call get method of requests library with URL and parameters
        if kwargs is not None and ('api_key' in kwargs.keys()):
            #print("com auth")
            #print("api_key: {}".format(kwargs['api_key']))
            params = dict()
            params["text"] = kwargs["text"]
            params["version"] = kwargs["version"]
            params["features"] = kwargs["features"]
            params["language"] = "en"
            params["return_analyzed_text"] = kwargs["return_analyzed_text"]
            response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
                                    auth=HTTPBasicAuth('apikey', kwargs['api_key']))
        else:
            #print("sem auth")
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    #print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data


# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, payload, **kwargs):
    print(kwargs)
    print("POST to {} ".format(url))
    try:
        # Call post method of requests library with URL, parameters and data
        response = requests.post(url, params=kwargs, json=payload)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data

# Create a get_dealers_from_cf method to get dealers from a cloud function
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    if kwargs is not None and ('state' in kwargs.keys()):
        json_result = get_request(url, state=kwargs['state'])
    else:
        json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["result"]
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            #dealer_doc = dealer["doc"]
            dealer_doc = dealer if kwargs is not None and ('state' in kwargs.keys()) else dealer['doc']
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   state=dealer_doc["state"], st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
def get_dealer_reviews_from_cf(url, dealerId):
    results = []
    json_result = get_request(url, dealerId=dealerId)
    if json_result:
        # Get the row list in JSON as dealers
        reviews = json_result["reviews"]
        # For each dealer object
        for review in reviews:
            # Get its content in `doc` object
            review_doc = review["doc"]
            # Create a CarDealer object with values in `doc` object
            review_obj = DealerReview(id=review_doc["_id"], dealership=review_doc["dealership"],
                                    name=review_doc["name"], purchase=review_doc["purchase"],
                                    review=review_doc["review"], purchase_date=review_doc["purchase_date"],
                                    car_make=review_doc["car_make"], car_model=review_doc["car_model"],
                                    car_year=review_doc["car_year"], sentiment=analyze_review_sentiments(review_doc["review"]))
            results.append(review_obj)
        return results


# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
def analyze_review_sentiments(dealerreview):
    # Call get_request with a URL parameter
    url     = "https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/" + os.environ['WATSON_URL_KEY'] + "/v1/analyze"
    # GET ENVIRONMENT VARIABLES
    api_key = os.environ['WATSON_APIKEY']

    json_result = get_request(url, text=dealerreview, api_key=api_key, version="2020-08-01", features="sentiment", return_analyzed_text=True)
    if json_result:
        # Get the sentiment label and score in JSON
        sentiment = json_result["sentiment"]["document"]["label"]
        score = json_result["sentiment"]["document"]["score"]
        # Create a sentiment object with the label and score
        sentiment_obj = {"label": sentiment, "score": score}
        return sentiment_obj
