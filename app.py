import streamlit as st
import pandas as pd
from twilio.rest import Client

# Load the court scenarios CSV file
df_scenarios = pd.read_csv('court_scenarios.csv')

# Twilio Configuration using Streamlit secrets
TWILIO_ACCOUNT_SID = st.secrets["TWILIO_ACCOUNT_SID"]  # Fetch from Streamlit secrets
TWILIO_AUTH_TOKEN = st.secrets["TWILIO_AUTH_TOKEN"]  # Fetch from Streamlit secrets
TWILIO_WHATSAPP_NUMBER = 'whatsapp:+14155238886'  # Your Twilio WhatsApp number (sandbox number)

# Initialize Twilio client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Function to search for relevant documents based on keywords
def get_document_suggestions(case_description):
    suggested_documents = []
    for _, row in df_scenarios.iterrows():
        # Check if the case description contains keywords from the "description" field
        if any(keyword.lower() in case_description.lower() for keyword in row['description'].split()):
            # Collect document suggestions from the columns defined
            for col in ['document_suggestions__001', 'document_suggestions__002', 'document_suggestions__003']:
                if pd.notnull(row[col]):
                    suggested_documents.append(row[col])  # Add each document suggestion
    return list(set(suggested_documents))  # Return unique suggestions

# Streamlit UI
st.title("Court Case Document Suggestion Tool")

# Input case description
case_description = st.text_area("Enter a description of your court case:")

# Get document suggestions based on the case description
suggestions = []
if case_description:
    suggestions = get_document_suggestions(case_description)

# Display suggested documents when the button is clicked
if st.button("Get Document Suggestions"):
    if case_description:
        if suggestions:
            st.write("### Suggested Documents")
            for doc in suggestions:
                st.write("- " + doc)  # Display each document suggestion
        else:
            st.write("No document suggestions found. Try rephrasing your case description.")
    else:
        st.write("Please enter a case description to get suggestions.")

# Client's WhatsApp number input
client_name = st.text_input("Enter client's name:")
client_whatsapp_number = st.text_input("Enter client's WhatsApp number (e.g., +1234567890):")

# Appointment details input
appointment_date = st.date_input("Select Appointment Date:")
appointment_time = st.time_input("Select Appointment Time:")
appointment_location = st.text_input("Enter Appointment Location:")

# Button to send WhatsApp message
if st.button("Send Document Collection Message"):
    if client_whatsapp_number and suggestions and client_name:
        # Create a formatted message including appointment details with bullet points for documents
        document_list = "\n".join([f"• {doc}" for doc in suggestions])  # Format documents with bullet points
        message_body = (
            f"Hello {client_name}!\n\n"
            f"Please bring the following documents while meeting your lawyer:\n"
            f"{document_list}\n\n"
            f"Appointment Details:\n"
            f"Date: {appointment_date}\n"
            f"Time: {appointment_time}\n"
            f"Location: {appointment_location}\n\n"
            "Please make sure to bring these documents safely.\n\n"
            "Thank you!"
        )
        try:
            message = client.messages.create(
                body=message_body,
                from_=TWILIO_WHATSAPP_NUMBER,
                to=f'whatsapp:{client_whatsapp_number}'
            )
            st.success(f"Message sent to {client_whatsapp_number}: {message_body}")
        except Exception as e:
            st.error(f"Failed to send message: {str(e)}")
    else:
        st.warning("Please enter a valid WhatsApp number, client name, and ensure there are suggested documents.")
