from flask import Flask, jsonify, request
import pandas as pd, numpy as np
from pathlib import Path
import joblib 
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

app = Flask(__name__)

# to first import the data into the backend
current_path = Path(__file__).parent
tfidf = joblib.load("../models/category_vectoriser.pkl")
category_model = joblib.load("../models/category_model.pkl")
stop_word = list(ENGLISH_STOP_WORDS)
priority_model = joblib.load("../models/priority_model.pkl")
preprocessed = joblib.load("../models/priority_preprocessor.pkl")

file_path = current_path / ".."/ "data" / "new_customer_complaints.csv"

try:
    data = pd.read_csv(file_path)
except FileNotFoundError:
    print(F'Error loading file {file_path}')


@app.route("/")
def show_message():
    return "GlowCare cosmetics Company"

# to get the kpi of the data
@app.route("/get_kpi", methods=['GET'])
def get_kpi():

    total_complaints = len(data)
    complaint_status = data['new_complaint_status'].value_counts().to_dict()

    resolved_complaints = complaint_status.get('resolved', 0)
    awaiting_complaints = complaint_status.get('awaiting', 0)
    in_progress = complaint_status.get('in_progress', 0)
    priority = data['new_complaint_priority'].nunique()
    category = data['new_complaint_category'].nunique()


    print(resolved_complaints)
    print(awaiting_complaints)
    print(in_progress)

    return jsonify({
        "total_complaints" : total_complaints,
        "resolved" : resolved_complaints,
        "awaiting" : awaiting_complaints,
        "in_progress" : in_progress,
        "priority" : priority,
        "category" : category
    })

# to get the analytics data
@app.route('/analytics', methods=['GET'])
def get_analytics():

    try:
        country = data['new_customer_country'].value_counts().to_dict()
        category = data['new_complaint_category'].value_counts().to_dict()
        communication = data['new_communication_channel'].value_counts().to_dict()
        product = data['new_complaint_product_type'].value_counts().to_dict()
        priority = data['new_complaint_priority'].value_counts().to_dict()
        department = data['new_department_assigend'].value_counts().to_dict()

        country_value = {
            "nigeria" : country.get('Nigeria', 0),
            "morocco" : country.get("Morocco", 0),
            "ghana" : country.get('Ghana', 0),
            "algeria" : country.get('Algeria', 0),
            "egypt" : country.get("Egypt", 0),
            "kenya" : country.get("Kenya", 0),
            "tunisia" : country.get('Tunisia', 0)
        }

        category_value = {
            "product_quality" : category.get("product_quality", 0),
            "packaging" : category.get("packaging", 0),
            "delivery" : category.get("delivery", 0),
            "customer_service" : category.get("customer_service", 0),
            "refund" : category.get("refund", 0),
            "billing" : category.get("billing", 0)
        }
        
        communication_value = {
            "phone_call" : communication.get('Phone Call', 0),
            "email" : communication.get("Email", 0),
            "mobile_app" : communication.get("Mobile App", 0),
            "website" : communication.get('Website', 0) 
        }

        product_value = {
            "kohl" : product.get('Kohl', 0),
            "lipstick" : product.get('Lipstick', 0),
            "eyeliner" : product.get("Eyeliner", 0),
            "body_lotion" : product.get("Body Lotion", 0),
            "blush" : product.get("Blush", 0),
            "concealer" : product.get("Concealer", 0),
            "sunscreen" : product.get("Sunscreen", 0),
            "primer" : product.get("Primer", 0),
            "foundation" : product.get("Foundation", 0),
            "eyeshadow" : product.get("Eyeshadow", 0),
            "cleanser" : product.get("Cleanser", 0)
        }

        priority_value = {
            "1" : priority.get(1, 0),
            "2" : priority.get(2, 0),
            "3" : priority.get(3, 0),
            "4" : priority.get(4, 0),
            "5" : priority.get(5, 0)
        }

        department_values = {
            "customer_support" : department.get("Customer Support", 0),
            "quality_control" : department.get("Quality Control Department", 0),
            "packaging_department" : department.get("Packaging Department", 0),
            "delivery_department" : department.get("Delivery Department", 0),
            "finance_department" : department.get("Finance Department", 0)
        }

        return jsonify({
            'country_values' : country_value,
            'category_values' : category_value,
            'communication_values' : communication_value,
            'product_values' : product_value,
            'priority_values' : priority_value,
            'department_values' : department_values
        })
    except Exception as e:
        return jsonify({
            "error" : "Error", "message" : str(e)
        })

# to get the complete data frame 
@app.route("/get_complaints", methods=['GET'])
def get_complaints():

    if data is not None:
        try:
            complaints = data.to_dict(orient='records')
            return jsonify({
                "complaint" : complaints
            })
        except FileNotFoundError as e:
            return jsonify({
                "error" : "File Not Found", "message" : "File not found", "details" : str(e)
            })

# get filter for my data 
@app.route("/get_filters", methods=['GET'])
def get_filters():

    try:
        filter = {}

        countries = data['new_customer_country'].dropna().unique().tolist()
        categories = data['new_complaint_category'].unique().tolist()
        communication_channel = data['new_communication_channel'].unique().tolist()
        products = data['new_complaint_product_type'].unique().tolist()
        department = data['new_department_assigend'].unique().tolist()
        status = data['new_complaint_status'].unique().tolist()

        filter['countries'] = countries
        filter['categories'] = categories
        filter['communication_channel'] = communication_channel
        filter['products'] = products
        filter['department'] = department
        filter['status'] = status

        return jsonify(filter)

    except Exception as e:
        return jsonify({
            "error" : "Error",
            "message" : "Error getting the unique values",
            "details" : str(e)
        })


# get the predictive category of a complaint
@app.route("/get_category", methods=['POST'])
def get_category():

    data = request.get_json()
    if not data:
        raise ValueError("No JSON recieved")

    try:
        data_description = data.get('description_text')
        if not data_description or data_description.strip().lower() == "":
            return jsonify({"error" : "Cannot Predict an Empty string"}), 400

        def get_stop_words(sentence):
            split_sentence = sentence.split()

            clear_description = [word for word in split_sentence if word not in stop_word]

            return " ".join(clear_description)

        data_description = get_stop_words(data_description)


        vectorise_text = tfidf.transform([data_description])

        description_prediction = category_model.predict(vectorise_text)[0]
        description_prediction_proba = category_model.predict_proba(vectorise_text)[0]
        max_description_proba = max(description_prediction_proba)
        percentage_probability = round(max_description_proba * 100, 2)

        return jsonify({
            "status" : "success",
            "model_prediction" : description_prediction,
            "model_probability" : f"{percentage_probability}%"
        }), 200

    except Exception as e:
        return jsonify({
            "error" : "Error",
            "message" : str(e)
        }), 500


@app.route("/get_priority", methods=['POST'])
def get_priority():

    data = request.get_json()
    if not data:
        return jsonify({ "status" : "error", "message" : "No JSON value recieved"}), 400

    try:

        complaint_category = data.get('complaint_category')
        complaint_description = data.get("complaint_description", "").strip().lower()
        complaint_product = data.get('complaint_product')
        communication_channel = data.get("communication_channel")

        def get_stop_word(sentence):
            split_sentence = sentence.split()
        
            cleaned_sentence = [word for word in split_sentence if word not in stop_word]
        
            return " ".join(cleaned_sentence)
        
        cleaned_complaint = get_stop_word(complaint_description)


        complaint_data = pd.DataFrame({
            "new_complaint_category" : [complaint_category],
            "lower_case_cleaned_description" : [complaint_description],
           "new_complaint_product_type" : [complaint_product],
           "new_communication_channel" : [communication_channel],
           "cleaned_complaints" : [cleaned_complaint]
        })

        preprocessed_column = preprocessed.transform(complaint_data)

        predicted_value = priority_model.predict(preprocessed_column)[0]
        predicted_value_proba = priority_model.predict_proba(preprocessed_column)[0]
        max_proba = max(predicted_value_proba)
        percentage_proba = round(max_proba * 100, 2)

        return jsonify({
            "status" : "success",
            "predicted_priority" : int(predicted_value),
            "priority_proba" : percentage_proba
        }), 200

    except Exception as e:
        return jsonify({
            "status" : "error",
            "message" : str(e)
        }), 500


if __name__ == "__main__":
    app.run(debug=True)