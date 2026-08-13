import streamlit as st
from api import get_kpi, get_analytics, get_filters, get_complaint, predict_complaint, predict_priority
import plotly.express as px
import pandas as pd

st.set_page_config(page_title='GlowCare Cosmetics', layout="wide")
# Side bar

st.sidebar.title("GlowCare Complaint Intelligence Sysyem")
st.sidebar.divider()
page = st.sidebar.radio(
    "Navigate",
    ["Home", "Dashboard", 'Complaint Explorer', 'Category Prediction', "Priority Prediction"]
)

kpi_data = get_kpi()
analytics = get_analytics()
filters = get_filters()
complaints = get_complaint()


def show_plots(dict_values, x_label, chart_title):
    if dict_values:
        data_frame = pd.DataFrame(list(dict_values.items()), columns=[x_label, "Total Complaints"])
        data_frame[x_label] = data_frame[x_label].str.replace("_", " ").str.title()
        fig3 = px.bar(data_frame, x=x_label, y="Total Complaints", title=chart_title, color=x_label)
        st.plotly_chart(fig3, use_container_width=True)

# the function to get the data filtering 
show_complaint_data = complaints.get("complaint")
df = pd.DataFrame(show_complaint_data)

def show_filter_data(header, category):
    st.subheader(header)
    group = filters.get(category, [])
    options = ["All"] + group
    return st.selectbox("Select an option: ", options)


# show home create am markdown file to explain the project
def show_home():
    st.title("GlowCare Cosmetics Complaints Intelligent System")
    st.markdown("Monitor customer complaints, identify complaints trends, and predict complaint category and priority using machine learning")

    st.divider()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        with st.container(border=True):
            st.subheader("Dataset")
            st.markdown(f"""
                * **Complaints** : {kpi_data.get("total_complaints", 0)}
                * **Category** : {kpi_data.get("category", 0)}
                * **Priority** : {kpi_data.get("priority", 0)}
            """)

    with col2:
        with st.container(border=True):
            st.subheader("Machine Learning")
            st.markdown("""
                * TF-IDF 
                * Naive Bayes
                * Logistic Regression 
            """)

    with col3: 
        with st.container(border=True):
            st.subheader('Backend')
            st.markdown("""
                * Flask Rest Api
                * 6 Endpoints
                * JSON responses
            """)

    with col4:
        with st.container(border=True):
            st.subheader("Frontend")
            st.markdown("""
                * Streamlit Dashboard
                * 6 Interactive Charts
                * Live Predictions
             """)

    st.divider()

    st.subheader("Workflow")
    with st.container(border=True):
        st.markdown("""
        ``` text
            Customer Complaint
            Flask Backend
            Machine Learning
            Dashboard and Predictions
        ```
    """)

    st.divider()

    st.subheader("Navigation Guide")
    st.markdown("""
        * **Dashboard** - View complaints statictics and trend.
        * **Complaint Explorer** - Search and filter customer complaints.
        * **Category Predictions** - Predict the complaint category.
        * **Category Priority** - Predict the complaint priority.
    """)


# show dashboard
def show_dashboard():
    st.title("Dashboard")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        with st.container(border=True):
            st.subheader('Total Complaints')
            st.write(f"### {kpi_data.get("total_complaints", 0)}")

    with col2:
        with st.container(border=True):
            st.subheader("Resolved")
            st.write(f"### {kpi_data.get("resolved", 0)}")

    with col3:
        with st.container(border=True):
            st.subheader('Awaiting')
            st.write(f"### {kpi_data.get("awaiting", 0)}")

    with col4:
        with st.container(border=True):
            st.subheader("In progress")
            st.write(f"### {kpi_data.get("in_progress", 0)}")

    st.divider()

    col1, col2 = st.columns(2)
    #  get the category dictionary from the backend
    with col1:
        dict_category = analytics.get("category_values", {})
        if dict_category:
            # create a datframe
            category_data = pd.DataFrame(list(dict_category.items()), columns=['Category', "Total Complaints"])
            category_data['Category'] = category_data['Category'].str.replace("_", " ").str.title()
            # plot the bar using build plotly package
            fig = px.bar(
                category_data, x="Category", y='Total Complaints', color="Category", title='Total Complaints by Catgory'
            )
            st.plotly_chart(fig, use_container_width=True)
    with col2:
        # get the communication channel from the backend 
        dict_communication = analytics.get("communication_values", {})
        # create a dataframe
        if dict_communication:
            communication_data = pd.DataFrame(list(dict_communication.items()), columns=['Communication Channels', 'Total Complaints'])
            communication_data['Communication Channels'] = communication_data['Communication Channels'].str.replace("_", " ").str.title()
            # plot the graph using plotly
            fig1 = px.bar(
                communication_data, x="Communication Channels", y='Total Complaints', color='Communication Channels', title='Complaints send by communication Channel'
            )
            st.plotly_chart(fig1, use_container_width=True)
    st.divider()
    col3, col4 = st.columns(2)
    with col3:
        show_plots(analytics.get('country_values', {}), x_label="Country", chart_title="Complaints By Country")
    with col4:
        show_plots(analytics.get("department_values", {}), x_label="Departments", chart_title="Complaints By Departments")
    st.divider()
    col5, col6 = st.columns(2)
    with col5:
        show_plots(analytics.get("priority_values", {}), x_label='Priority', chart_title="Complaints By Priority")
    with col6:
        show_plots(analytics.get("product_values", {}), x_label='Products', chart_title='Complaints By Products')



# show complaint
def show_complaint():
    st.title("Customer Complaint Dataset Explorer")
    st.write("Browse, search and filter customer complaints")
    st.divider()

    filtered_data = df.copy()
    # to filter by complaint category
    col1, col2  = st.columns(2)
    with col1:
        selected_category = show_filter_data("Filter By Category", "categories")
    if selected_category != "All":
        filtered_data = filtered_data[filtered_data['new_complaint_category'] == selected_category]

    #  get the commuinication filter
    with col2:
        selected_communication = show_filter_data("Filter By Communication", "communication_channel")
    if selected_communication != "All":
        filtered_data = filtered_data[filtered_data['new_communication_channel'] == selected_communication]

    col3, col4 = st.columns(2)
    with col3:
        selected_countries = show_filter_data("Filter By Countries", 'countries')
    if selected_countries != "All":
        filtered_data = filtered_data[filtered_data['new_customer_country'] == selected_countries]

    with col4:
        selected_department = show_filter_data("Filter By Department", 'department')
    if selected_department != "All":
        filtered_data = filtered_data[filtered_data['new_department_assigend'] == selected_department]

    col5, col6 = st.columns(2)
    with col5:
        selected_product = show_filter_data("Filter By Product", 'products')
    if selected_product != "All":
        filtered_data = filtered_data[filtered_data['new_complaint_product_type'] == selected_product]

    with col6:
        selected_status = show_filter_data("Filter By Status", 'status')
    if selected_status != "All":
        filtered_data = filtered_data[filtered_data['new_complaint_status'] == selected_status]

    st.dataframe(filtered_data, use_container_width=True)

    st.divider()

    new_csv = filtered_data.to_csv(index=False).encode('utf-8')
    st.download_button(label="Download Data as csv", data=new_csv, file_name='glowcare_filtered_data.csv', mime="text/csv")

# show complaint prediction
def show_complaint_prediction():
    st.title("Category Prediction")

    st.write("Predict the category of a customer complaint using a trained TF-IDF + Machine Learning model.")
    st.divider()
    user_input = st.text_area("Complaint Description", placeholder="My cleanser is broken")

    st.divider()

    if st.button('Predict Complaints'):
        if not user_input.strip():
            st.warning("Cannot Predict an empty complaints")
        else:
            with st.spinner('Predicting complaints......'):
                prediction_result = predict_complaint(user_input)
                if prediction_result and prediction_result["status"] == "success":

                    category = prediction_result.get('model_prediction')
                    probability = prediction_result.get("model_probability", 0)
                    st.success("Prediction Successfull")

                    st.metric("Predicted label: ", value=category.replace("_", " ").title())
                    st.metric("Confidence_level: ", value=probability)


# show complaint priority
def show_complaint_priority():
    st.title("Complaint Priority")
    st.write("Predict the priority level of your complaint")

    st.divider()

    
    category = st.selectbox("Complaint Category", filters.get("categories", []))
    description = st.text_area("Complaint Decription", placeholder="The Cleanser arrived but the packaging was damaged").strip().lower()
    product = st.selectbox("Complaint Product", filters.get("products", []))
    channel = st.selectbox("Communication Channel", filters.get("communication_channel"))
    

    if st.button("Predict Priority"):
        if not category or not description or not product or not channel:
            st.warning("Cannot Predict an Empty values")
        else:
            with st.spinner("Predicting Priority....."):
                priority = predict_priority(category, description, product, channel)

                if priority and priority['status'] == "success":
                    st.success("Priority Predicted Successfully")
                    priority_value = priority.get("predicted_priority", 0)
                    priority_proba = priority.get("priority_proba", 0)

                    st.metric(label="Predicted Priority", value=int(priority_value))
                    st.metric(label="Predicted Probability", value=priority_proba)


# Router
if page == "Home":
    show_home()
elif page == "Dashboard":
    show_dashboard()
elif page == "Complaint Explorer":
    show_complaint()
elif page == "Category Prediction":
    show_complaint_prediction()
elif page == "Priority Prediction":
    show_complaint_priority()





