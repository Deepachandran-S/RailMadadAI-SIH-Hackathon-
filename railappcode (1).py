import streamlit as st
import PIL.Image
import io
import google.generativeai as genai
import openai
from io import BytesIO
from IPython.display import Image as IPImage, display as IPdisplay
# Initialize OpenAI API
openai.api_key = ""
# Configure Google Generative AI API
genai.configure(api_key="")
model = genai.GenerativeModel("gemini-1.5-pro")
visionmodel = genai.GenerativeModel("gemini-1.5-flash")

# Function to get a response from OpenAI
def get_chatgpt_response(messages):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    return response['choices'][0]['message']['content']

def upload_image():
    uploaded_image = st.file_uploader("Upload an image", type=["jpg", "png"])
    if uploaded_image is not None:
        img = PIL.Image.open(uploaded_image)
        st.image(img, caption="Uploaded Image", use_column_width=True)
        
        # Convert PIL Image to IPython Image
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')  # Change format as needed
        img_byte_arr.seek(0)
        
        # IPython Image requires a file path or URL, so we use BytesIO
        ip_img = IPImage(img_byte_arr.read())
        
        try:
            # Convert IPython Image to a format compatible with the vision model
            # Note: Update this line based on actual API requirements
            response = visionmodel.generate_content(img)  # Modify according to API documentation
            categories = """Complaints, Service-related, Delays and cancellations, Fares and ticketing, Amenities and facilities, Accessibility, Safety and security, Customer service, Infrastructure-related, Track conditions, Station conditions, Station security, Other, Lost and found, Damage to property, Crimes, Property crimes, Theft, Vandalism, Violent crimes, Assault, Homicide, Other crimes, Fraud, Drug trafficking, Terrorism, Disorderly conduct, Specific concerns, Child safety, Cybersecurity"""
            categories2="""Medical Assistance, Security, Divyangyan Facilities, Facilities for Women with Special Needs, Electrical Equipment, Coach-Cleanliness, Punctuality, Water Availablity, Coach- Maintenance, Catering & vending services, Staff Behaviour, Corruption/Bribery, Bed Roll, Miscellaneous"""
            stri = f"Give the name of Category out of {categories2} {response.text}  and a two-line summary of what is being happened"

            # Generate the content using the text-based model
            resp = model.generate_content(stri)

            # Display the response in markdown format
            
            return resp.text
        except Exception as e:
            return f"Error processing the image: {str(e)}"
    return None

# Streamlit UI with custom styles
st.markdown(
    """
    <style>
    body {
        background-color: #000000;
    }
    .stApp {
        background-color: #000000;
    }
    .header {
        color: #FFD700;
        text-align: center;
        padding: 20px;
    }
    .subheader {
        color: #FFD700;
        padding-bottom: 10px;
    }
    .user_input {
        background-color: #333333;
        padding: 10px;
        border-radius: 5px;
        color: #FFD700;
    }
    .button {
        background-color: #FFD700;
        color: #000000;
        border: none;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 5px;
    }
    .output {
        background-color: #333333;
        padding: 20px;
        border-radius: 10px;
        color: #FFD700;
    }
    .currency-img {
        width: 100px;
        margin: 10px auto;
        display: block;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<h1 class="header">🚆 Rail Madad 🚆</h1>', unsafe_allow_html=True)
st.markdown('<h2 class="subheader">Submit Your Complaint:</h2>', unsafe_allow_html=True)

# Upload image
uploaded = upload_image()

# Process the image if uploaded
if uploaded and st.button("Analyze Image"):
    result = uploaded
    st.markdown(f"<h2 style='color:gold;'>Response:</h2>", unsafe_allow_html=True)
    st.markdown(f"<div style='background-color:#333333;color:#FFD700;padding:10px;border-radius:10px;'>{result}</div>", unsafe_allow_html=True)

# Initialize chat history for text-based complaints
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful assistant for railway complaints."}
    ]

# Text-based complaint submission
issue_category = st.selectbox(
    'Category of Issue',
    ['Train Delay', 'Seat Reservation Issue', 'Food Quality', 'Cleanliness', 'Other']
)
coach_number = st.text_input('Coach Number')
seat_number = st.text_input('Seat Number')
description = st.text_area('Complaint Description')
attachment = st.file_uploader('Upload Supporting Documents (if any)', type=['jpg', 'png', 'pdf'])

if st.button('Submit Complaint'):
    # Construct the prompt for ChatGPT
    user_message = (
        f"Complaint Details:\n"
        f"Category: {issue_category}\n"
        f"Coach Number: {coach_number}\n"
        f"Seat Number: {seat_number}\n"
        f"Description: {description}\n\n"
        f"Please assist with this issue."
    )
    
    # Add user message to the conversation history
    st.session_state.messages.append({"role": "user", "content": user_message})
    
    # Get response from ChatGPT
    response = get_chatgpt_response(st.session_state.messages)
    
    # Add ChatGPT's response to the conversation history
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Display the response
    st.markdown('<h2 class="subheader">Response:</h2>', unsafe_allow_html=True)
    st.markdown(f'<div class="output">{response}</div>', unsafe_allow_html=True)

# Allow for continued conversation
st.markdown('<h2 class="subheader">Ask Another Question:</h2>', unsafe_allow_html=True)
user_input = st.text_input("You:", key="user_input", placeholder="Ask a follow-up question about your complaint.")

if st.button('Send', key="send"):
    # Add user's follow-up question to the conversation history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Get response from ChatGPT
    response = get_chatgpt_response(st.session_state.messages)
    
    # Add ChatGPT's response to the conversation history
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Display
