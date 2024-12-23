from django.shortcuts import render,redirect
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from django.http import JsonResponse
import time
import json
from django.shortcuts import render
from django.http import JsonResponse
import requests
from datetime import datetime, timedelta
import os

# Create your views here.


def home(request):
	return render(request,'home.html',{})	
def home1(request):

	if request.method == 'POST':
		pnr = request.POST['pnr']
		url = "https://irctc-indian-railway-pnr-status.p.rapidapi.com/getPNRStatus/"+ str(pnr)

		headers = {
			"x-rapidapi-key": "f8e32c6793mshb6e4d5bbb04e429p18de5cjsn576bee3617df",
			"x-rapidapi-host": "irctc-indian-railway-pnr-status.p.rapidapi.com"
		}
		try:
			response = requests.get(url, headers=headers)
			data = response.json()
		except Exception as e:
			response = "error .. ."	

		# context = {"response":response.json()}
		context = {
        "pnrNumber": data.get("data", {}).get("pnrNumber"),
        "trainNumber": data.get("data", {}).get("trainNumber"),
        "trainName": data.get("data", {}).get("trainName"),
        "dateOfJourney": data.get("data", {}).get("dateOfJourney"),
        "sourceStation": data.get("data", {}).get("sourceStation"),
        "destinationStation": data.get("data", {}).get("destinationStation"),
        "chartStatus": data.get("data", {}).get("chartStatus"),
        "passengerList": data.get("data", {}).get("passengerList", []),
    }


		return render(request, 'pnr.html', context)
	
	else:
		return render(request, 'pnr.html', {'pnr':"wrong pnr"})	



def Train_info(request):
    context = {"response": None, "error": None}
    
    if request.method == 'POST':
        train_number = request.POST.get('train_number', None)
        if train_number:
            url = f"https://indian-railway-irctc.p.rapidapi.com/api/trains-search/v1/train/{train_number}"
            querystring = {"isH5":"true","client":"web"}
            # url = f"https://api.example.com/train/{train_number}"  # Replace with actual API endpoint
            headers = {
				"x-rapidapi-key": "35958a2dd9mshb92df6efcffaefdp117a08jsnf100cac54e6c",
				"x-rapidapi-host": "indian-railway-irctc.p.rapidapi.com",
				"x-rapid-api": "rapid-api-database"
			}
            try:
                response = requests.get(url, headers=headers, params=querystring)
                if response.status_code == 200:
                    context['response'] = response.json()
                else:
                    context['error'] = "Failed to fetch train information. Please check the train number."
            except Exception as e:
                context['error'] = str(e)
        else:
            context['error'] = "Please provide a train number."
    
    return render(request, 'train_info.html', context)


def live_train_status(request):
    if request.method == "POST":
        # Get data from the form
        train_number = request.POST.get("train_number")
        departure_date = request.POST.get("departure_date")

        if not train_number or not departure_date:
            return render(request, "live_train_status.html", {"error": "Please provide both train number and departure date."})

        try:
            # Convert the date to YYYYMMDD format for the API
            formatted_date = datetime.strptime(departure_date, "%Y-%m-%d").strftime("%Y%m%d")
        except ValueError:
            return render(request, "live_train_status.html", {"error": "Invalid date format. Please try again."})

        # API details
        url = "https://indian-railway-irctc.p.rapidapi.com/api/trains/v1/train/status"
        querystring = {
            "departure_date": formatted_date,
            "isH5": "true",
            "client": "web",
            "train_number": train_number
        }
        headers = {
            "x-rapidapi-key": "35958a2dd9mshb92df6efcffaefdp117a08jsnf100cac54e6c",
            "x-rapidapi-host":"indian-railway-irctc.p.rapidapi.com",
            "x-rapid-api": "rapid-api-database"
        }
        # Fetch data from API
        try:
            response = requests.get(url, headers=headers, params=querystring)
            data = response.json()

            # Process data
            if data["status"]["result"] == "success":
                body = data["body"]
                train_status_message = body["train_status_message"]
                stations = body["stations"]

                # Determine delay/early status and time difference
                for station in stations:
                    scheduled_arrival = station.get("arrivalTime")
                    actual_arrival = station.get("actual_arrival_time")

                    if scheduled_arrival != "--" and actual_arrival != "--":
                        # Calculate the time difference
                        scheduled_dt = datetime.strptime(scheduled_arrival, "%H:%M")
                        actual_dt = datetime.strptime(actual_arrival, "%H:%M")
                        time_difference = actual_dt - scheduled_dt

                        if time_difference != timedelta(0):
                            station["is_delayed"] = time_difference.total_seconds() > 0
                            station["time_difference"] = str(abs(time_difference))
                        else:
                            station["is_delayed"] = False
                            station["time_difference"] = "On Time"
                    else:
                        station["is_delayed"] = False
                        station["time_difference"] = "N/A"

                return render(request, "live_train_status.html", {
                    "train_status_message": train_status_message,
                    "stations": stations,
                    "current_station": body.get("current_station", "Unknown"),
                    "time_of_availability": body.get("time_of_availability", "N/A"),
                    "terminated": body.get("terminated", False),
                })
            else:
                return render(request, "live_train_status.html", {"error": "Unable to fetch train status. Please check your inputs."})
        except Exception as e:
            return render(request, "live_train_status.html", {"error": str(e)})

    return render(request, "live_train_status.html")

def get_stations(request):
    """
    Fetch stations based on city or generic name provided by the user.
    """
    if request.method == 'POST':  # Check if the form was submitted
        city_name = request.POST.get('city_name', '')  # Get the city name from form input
        url = "https://rstations.p.rapidapi.com/v1/railways/stations/india"
        headers = {
            "x-rapidapi-key": "35958a2dd9mshb92df6efcffaefdp117a08jsnf100cac54e6c",
            "x-rapidapi-host": "rstations.p.rapidapi.com",
            "Content-Type": "application/json"
        }
        payload = {"search": city_name}

        try:
            response = requests.post(url, json=payload, headers=headers)
            stations = response.json()  # Parse JSON response
        except requests.exceptions.RequestException as e:
            stations = []  # Handle any errors and return an empty list
            print(f"An error occurred: {e}")

        return render(request, 'stations.html', {'stations': stations, 'city_name': city_name})
    
    return render(request, 'stations.html', {'stations': None})