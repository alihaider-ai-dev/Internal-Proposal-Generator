import anthropic
import streamlit as st
from bs4 import BeautifulSoup
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration with consistent styling
st.set_page_config(
    page_title="AI Proposal Generator",
    page_icon="✨",
    layout="wide"
)

# Custom CSS for consistent styling
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        height: 3em;
        font-size: 18px;
        margin-top: 1em;
    }
    .main {
        padding: 2rem;
    }
    .stAlert {
        margin-top: 1em;
    }
    .proposal-container {
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 20px;
        margin: 20px 0;
        background-color: #fff;
    }
    .copy-button {
        display: flex;
        justify-content: center;
        margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session states
if "client" not in st.session_state:
    st.session_state.client = anthropic.Anthropic(
        api_key=os.getenv('ANTHROPIC_API_KEY')
    )

if "messages" not in st.session_state:
    st.session_state.messages = []

if "processing" not in st.session_state:
    st.session_state.processing = False

# Default template
default_template = """
    <template>
[**Greeting in client's local language using the available Client Name/Company Name (if available)**]  

I've closely reviewed your project details, and I'm certain that my team and I at **AIDevStudio.ai** are ideally positioned to deliver exceptional results for **[Simplified Project Title]**. We've just concluded a similar project in **[relevant industry or sector]**, allowing us to hit the ground running with informed strategies and the right AI libraries & frameworks. Happy to elaborate on these when we get to chat.  

I also understand you're busy and likely receiving tens of applications from other freelancers/agencies, but here's why a chat with me is worth your time:  

- **:briefcase: Business-minded**: We understand AI software products' unit economics and will advise on the most cost-effective, secure, and scalable AI tech stack you should use while keeping your best interests at heart.  
- **:moneybag: Competitive pricing**: As we've built many AI products already, we are resourceful and efficient.  
- **:rocket: Fast delivery and clear communication**: We work weekdays and weekends to meet week-long deadlines, not months. We're organized and communicate clearly—no micromanagement needed.  
- **:arrows_counterclockwise: 360° service**: We provide full-stack solutions from UX/UI product design to backend development, the latest LLM Agentic techniques, frontend, QA, LLM observability, and deployment. No need for additional hires.  

**:movie_camera: Some of my recent client interviews:**  
[Client testimonials list]

**:memo: Finally**, to prepare a detailed Software Requirements Specification (SRS) document for you with an accurate quote, we'll need to set up a meeting and discuss the project details in depth.  

**:telephone_receiver: You can send me a message here or schedule a meeting using my calendar link**: [https://cal.com/aidevstudio/30mins](https://cal.com/aidevstudio/30mins).  

Looking forward to speaking soon,  

**Ahmed**  
*CEO, AI Dev Studio*  

**P.S.**: Please consider the attached price as a placeholder until we discuss the specifics of your project.  
    </template>
"""

# Function to scrape job description with proper error handling
def scrape_job_description(url: str) -> tuple[bool, str]:
    """
    Scrape job description from URL with enhanced error handling
    Returns: (success: bool, content: str)
    """
    try:
        with st.spinner("🔍 Fetching job description..."):
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            return True, soup.get_text()
    except requests.exceptions.RequestException as e:
        return False, f"Error fetching URL: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

# Function to generate proposal with progress tracking
def generate_proposal(template: str, job_description: str) -> str:
    """Generate personalized proposal using Claude"""
    try:
        with st.status("🤖 Generating your proposal...", expanded=True) as status:
            status.write("Analyzing job description...")
            
            response = st.session_state.client.messages.create(
                model="claude-3-5-sonnet-20240620",
                messages=[{
                    "role": "user",
                    "content": f"Using the template provided, generate a hyper-personalized proposal based on the following job description: {job_description}. Keep the same formatting and emojis."
                }],
                system=template,
                temperature=0.1,
                max_tokens=4096,
                top_p=1,
                stream=False,
            )
            
            status.write("✅ Proposal generated successfully!")
            status.update(label="Generation complete!", state="complete")
            
            return response.content[0].text
    except Exception as e:
        st.error(f"Error generating proposal: {str(e)}")
        return None

# Header
col1, col2 = st.columns([1, 4])
with col1:
    st.image("Logo.png", width=200)
with col2:
    st.title("✨ AI-Powered Proposal Generator")
    st.markdown("*Transform job descriptions into persuasive proposals in seconds*")

# Main interface with tabs
tab1, tab2 = st.tabs(["📝 Direct Input", "🔗 URL Input"])

with tab1:
    with st.expander("✏️ Customize Template", expanded=False):
        template = st.text_area(
            "Proposal Template",
            value=default_template,
            height=300,
            help="Customize the proposal template to match your needs"
        )
    
    job_description = st.text_area(
        "📋 Job Description",
        placeholder="Paste the job description text here...",
        height=200,
        help="Enter the job description you want to create a proposal for"
    )

with tab2:
    url = st.text_input(
        "🌐 Job Posting URL",
        placeholder="https://example.com/job-posting",
        help="Enter the URL of the job posting to automatically extract the description"
    )
    
    if url:
        success, content = scrape_job_description(url)
        if success:
            st.success("✅ Job description scraped successfully!")
            job_description = content
            with st.expander("👀 View Scraped Content", expanded=False):
                st.markdown(job_description)
        else:
            st.error(content)

# Generate proposal
if st.button("✨ Generate Proposal", type="primary", disabled=not job_description):
    if job_description:
        proposal = generate_proposal(template, job_description)
        
        if proposal:
            st.markdown("### 📄 Generated Proposal")
            st.markdown("---")
            
            # Display proposal in a nice container
            with st.container():
                st.markdown(
                    f'<div class="proposal-container">{proposal}</div>',
                    unsafe_allow_html=True
                )
            
            # Copy button with JavaScript
            st.components.v1.html(
                f"""
                <div class="copy-button">
                    <textarea id="proposal-text" style="display: none;">{proposal}</textarea>
                    <button onclick="copyProposal()" class="copy-btn">
                        📋 Copy to Clipboard
                    </button>
                </div>
                <style>
                    .copy-btn {{
                        padding: 10px 20px;
                        font-size: 16px;
                        border: 2px solid #4CAF50;
                        border-radius: 5px;
                        background-color: white;
                        color: #4CAF50;
                        cursor: pointer;
                        transition: all 0.3s ease;
                    }}
                    .copy-btn:hover {{
                        background-color: #4CAF50;
                        color: white;
                        transform: translateY(-2px);
                        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                    }}
                </style>
                <script>
                    function copyProposal() {{
                        const text = document.getElementById("proposal-text");
                        text.select();
                        document.execCommand("copy");
                        
                        const btn = document.querySelector(".copy-btn");
                        btn.innerHTML = "✅ Copied!";
                        setTimeout(() => {{
                            btn.innerHTML = "📋 Copy to Clipboard";
                        }}, 2000);
                    }}
                </script>
                """,
                height=100
            )

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>Developed by AI Dev Studio</p>
    </div>
    """,
    unsafe_allow_html=True
)
