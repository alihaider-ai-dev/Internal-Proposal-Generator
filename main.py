import anthropic
import streamlit as st
from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv

load_dotenv()

# Initialize the Anthropic client with the API key
client = anthropic.Anthropic(
    api_key=os.getenv('ANTHROPIC_API_KEY')
)
st.session_state.client = client

if "messages" not in st.session_state:
    st.session_state.messages = []

if "copied" not in st.session_state:
    st.session_state.copied = []

# Function to scrape the job description from a provided URL
def scrape_job_description(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.get_text()
    except Exception as e:
        st.error(f"Error scraping URL: {str(e)}")
        return None

default_template = """
    <template>

[**Greeting in client’s local language using the available Client Name/Company Name (if available)**]  

I’ve closely reviewed your project details, and I’m certain that my team and I at **AIDevStudio.ai** are ideally positioned to deliver exceptional results for **[Simplified Project Title]**. We’ve just concluded a similar project in **[relevant industry or sector]**, allowing us to hit the ground running with informed strategies and the right AI libraries & frameworks. Happy to elaborate on these when we get to chat.  

I also understand you’re busy and likely receiving tens of applications from other freelancers/agencies, but here’s why a chat with me is worth your time:  

- **:briefcase: Business-minded**: We understand AI software products’ unit economics and will advise on the most cost-effective, secure, and scalable AI tech stack you should use while keeping your best interests at heart.  
- **:moneybag: Competitive pricing**: As we’ve built many AI products already, we are resourceful and efficient.  
- **:rocket: Fast delivery and clear communication**: We work weekdays and weekends to meet week-long deadlines, not months. We’re organized and communicate clearly—no micromanagement needed.  
- **:arrows_counterclockwise: 360° service**: We provide full-stack solutions from UX/UI product design to backend development, the latest LLM Agentic techniques, frontend, QA, LLM observability, and deployment. No need for additional hires.  

**:movie_camera: Some of my recent client interviews:**  
- [Mr. Michael Galliker, CEO of Regulatory Globe GmbH](https://youtu.be/BcigeX3i-dk?si=sTAgQZZn0KXIzVaM)  
- [Mr. Christian Vancea, CEO of Essentio GmbH](https://www.youtube.com/watch?v=-W7qbUGwlXE)  
- [Dr. Walsh, Owner of Metabolic Fitness Pro](https://www.youtube.com/watch?v=S8WLRkpTLiQ)  
- [Mr. Scott Zerby, Mayor & Council at Shorewood City, Minnesota](https://youtu.be/xJKDFZO-V10?si=TL8DJxjmP6dC3NWT)  
- [Mrs. Ingrid Paulson, Founder/CEO of datym.ai](https://www.youtube.com/watch?v=Sq1u1WpWFHo)  
- [Mr. Mohammed Baadhim, Sr. Manager at Arweqah Social Incubator](https://youtu.be/sc3I4q8iJSk?si=nc7acuYzK_sQSEQH)  

**:memo: Finally**, to prepare a detailed Software Requirements Specification (SRS) document for you with an accurate quote, we’ll need to set up a meeting and discuss the project details in depth.  

**:telephone_receiver: You can send me a message here or schedule a meeting using my calendar link**: [https://cal.com/aidevstudio/30mins](https://cal.com/aidevstudio/30mins).  

Looking forward to speaking soon,  

**Ahmed**  
*CEO, AI Dev Studio*  

**P.S.**: Please consider the attached price as a placeholder until we discuss the specifics of your project.  

    </template>
"""

# Function to generate the greeting based on the template and job description
def generate_greeting(template, job_description: str):
    with st.spinner('Generating your personalized proposal...'):
        response = st.session_state.client.messages.create(
            model="claude-3-5-sonnet-20240620",
            messages=[
                {
                    "role": "user", 
                    "content": f"Using the template provided, generate a hyper-personalized proposal (only proposal and nothing else) based on the following job description: {job_description}. Make sure to generate the whole text including the part that is fixed or unchanged in the template. Keep the same spacing and formatting of the paragraphs and use the emojis in the template as well"
                }
            ],
            system=template,
            temperature=0.1,
            max_tokens=4096,
            top_p=1,
            stream=False,
        )
        greeting = response.content[0].text
        return greeting

# Streamlit interface with improved styling
st.set_page_config(page_title="AI Proposal Generator", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        height: 3em;
        font-size: 18px;
    }
    .main {
        padding: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Header with logo and title
col1, col2 = st.columns([1, 4])
with col1:
    st.image("Logo.png", width=200)  # Replace with your logo
with col2:
    st.title("AI-Powered Proposal Generator")
    st.markdown("*Generate personalized proposals in seconds*")

# Create tabs for different input methods
tab1, tab2 = st.tabs(["📝 Direct Input", "🔗 URL Input"])

with tab1:
    # Default template in a collapsible section
    with st.expander("Customize Template", expanded=False):
        template = st.text_area("Template", default_template, height=300)
    
    job_description = st.text_area("📋 Paste Your Job Description Here", 
                                 placeholder="Paste the job description text here...",
                                 height=200)

with tab2:
    url = st.text_input("🌐 Enter Job Posting URL", 
                       placeholder="https://example.com/job-posting")
    if url:
        with st.spinner("Scraping job description..."):
            job_description = scrape_job_description(url)
            if job_description:
                st.success("Job description scraped successfully!")
                with st.expander("View Scraped Content"):
                    st.write(job_description)

# Generate button with loading state
if st.button("✨ Generate Proposal", type="primary"):
    if not job_description:
        st.error("Please provide a job description first!")
    else:
        greeting = generate_greeting(template, job_description)
        
        # Display the generated proposal in a nice box
        st.markdown("### 📄 Generated Proposal")
        st.markdown("""---""")
        st.markdown(greeting)
        st.components.v1.html(f"""
        <div style="display: flex; justify-content: center; margin-top: 20px;">
        
        <textarea id="greeting-text" style="width: 0px; height: 0px;">{greeting}</textarea>
        <button onclick="copyToClipboard()" style="border: 2px solid #4CAF50; background-color: white; color: #4CAF50; border-radius: 5px; padding: 10px 20px; font-size: 16px; cursor: pointer; transition: all 0.3s ease;">Copy to Clipboard</button>
        <style>
            button:hover {{
                background-color: #4CAF50 !important;
                color: white !important;
                transform: translateY(-2px);
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            }}
        </style>
        <script>
            function copyToClipboard() {{
                var copyText = document.getElementById("greeting-text");
                copyText.select();
                copyText.setSelectionRange(0, 99999);
                document.execCommand("copy");
                
                // Add visual feedback
                var button = document.querySelector("button");
                button.innerHTML = "Copied!";
                setTimeout(function() {{
                    button.innerHTML = "Copy to Clipboard";
                }}, 2000);
            }}
        </script>
        </div>
    """, height=100)

# Footer
st.markdown("""---""")
st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>Developed by AI Dev Studio</p>
    </div>
""", unsafe_allow_html=True)