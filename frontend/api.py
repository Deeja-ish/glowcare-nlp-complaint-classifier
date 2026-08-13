import requests
import streamlit as st


# get the kpi data from the backend
def get_kpi():
    try:
        response = requests.get("http://127.0.0.1:5000/get_kpi")

        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error Fetching KPI data {response.text}")
            return None
        
    except requests.exceptions.ConnectionError:
        st.error("Error Connecting to the flask backend")
        return None


# get the analytics data from the backend
def get_analytics():
    try:
        response = requests.get("http://127.0.0.1:5000/analytics")

        if response.status_code == 200:
           return response.json()
        else:
            st.error(f"Error Fetching Analytics Data {response.text}")
            return None
        
    except requests.exceptions.ConnectionError:
        st.error("Error connecting to flask backend")
        return None

# get the filters data from the backend
def get_filters():
    try:
        response = requests.get("http://127.0.0.1:5000/get_filters")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error Fetching Filters data {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("Error Connecting to the flask backend")
        return None


# get the complaints data from the backend
def get_complaint():
    try:
        response = requests.get("http://127.0.0.1:5000/get_complaints")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error Fetching the complaints data {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("Error Connecting to the flask backend")
        return None

# get the decription prediction route 
def predict_complaint(complaint_text):
    payload = {
        "description_text" : complaint_text
    }

    try:
        response = requests.post("http://127.0.0.1:5000/get_category", json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error Fetching the category api {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("Error Connection to the flask backend")
        return None


def predict_priority(complaint_category, complaint_description, complaint_product, communication_channel):
    payload = {
        "complaint_category" : complaint_category,
        "complaint_description" : complaint_description,
        "complaint_product" : complaint_product,
        "communication_channel" : communication_channel
    }

    try:
        response = requests.post("http://127.0.0.1:5000/get_priority", json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error Fetching the Priority api {response.text}")
    except requests.exceptions.ConnectionError:
        st.error("Error connecting to the Flask backend")


