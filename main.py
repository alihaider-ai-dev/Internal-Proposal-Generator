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
Using the template provided, generate a hyper-personalized proposal based on the following job description:
Instructions:
- never replace the links in case studies with hyperlinks or words, keep it as is
- never use placeholders as these will be sent in the exact way you put them in. Examples of placeholders would be: [your link], [Your Name]
- Remove this sentence from the personalized proposal “Using the template provided, generate a hyper-personalized proposal based on the following job description: ”
- Return the Proposal Directly without any Prefix or Postfix Phrases or Text.

    <template>
[Greeting in client’s local language using the available Client Name/Company Name (if available)]
I’ve closely reviewed your project details, and I’m certain that my team and I at AIHealthStudio.ai are ideally positioned to deliver exceptional results for [Project name]. We’ve just concluded a project in [same industry or sector of the project or job], allowing us to hit the ground running with the right libraries & frameworks. Happy to elaborate on these when we get to chat.
I also understand you’re busy and likely receiving 10s of applications from other freelancers/agencies, but here’s why a chat with me is worth your time:
💼 Business-minded: We understand AI Software products unit economics and will advise on the most cost-effective, secure and scalable AI tech stack you should use while keeping your best interests at heart.
💰 Competitive pricing: As we’ve built many AI products already, that makes us resourceful and efficient.
🚀 Fast delivery and clear communication: We work weekdays and weekends to meet week-long deadlines, not months. We’re organized and communicate clearly—no micromanagement needed.
🔄 360° service: We provide full-stack solutions from UX/UI product design to backend development to the latest LLM Agentic techniques, frontend, QA, LLM observability and deployment. No need for additional hires.
🎥 Some of my recent clients interviews:
- https://youtu.be/BcigeX3i-dk?si=sTAgQZZn0KXIzVaM (Mr Michael Galliker, CEO of Regulatory Globe GmbH)
- https://www.youtube.com/watch?v=-W7qbUGwlXE (Mr Christian Vancea, CEO of Essentio GmbH)
- https://www.youtube.com/watch?v=S8WLRkpTLiQ (Dr. Walsh, Owner of Metabolic Fitness Pro)
- https://youtu.be/xJKDFZO-V10?si=TL8DJxjmP6dC3NWT  (Mr Scott Zerby, Mayor & Council at shorewood city, Minnesota)
- https://www.youtube.com/watch?v=Sq1u1WpWFHo (Mrs. Ingrid Paulson, Founder/CEO of datym.ai)
- https://youtu.be/sc3I4q8iJSk?si=nc7acuYzK_sQSEQH (Mr Mohammed Baadhim, Sr. Manager at Arweqah Social Incubator)
📝 Finally, to prepare a detailed Software Requirements Specification (SRS) document for you with an accurate quote, we’ll need to set up a meeting and discuss the project details in detail
📞 You can send me a message here or schedule a meeting using my calendar link here: https://cal.com/aihealthstudio/30mins .
Looking forward to speaking soon,
Ahmed
CEO, AI Health Studio
P.S: Please consider the attached price as a placeholder until we discuss the specifics of your project.
"""

# Function to scrape job description with proper error handling
def scrape_job_description(url: str) -> tuple[bool, str]:
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
    try:
        with st.status("🤖 Generating your proposal...", expanded=True) as status:            
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
            
            # Updated copy button with corrected JavaScript
            st.components.v1.html(
                f"""
                <div class="copy-button">
                    <button onclick="copyToClipboard()" class="copy-btn">
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
                    function copyToClipboard() {{
                        const proposalText = `{proposal.replace("`", "\\`").replace("'", "\\'")}`;
                        navigator.clipboard.writeText(proposalText).then(function() {{
                            const btn = document.querySelector(".copy-btn");
                            btn.innerHTML = "✅ Copied!";
                            setTimeout(() => {{
                                btn.innerHTML = "📋 Copy to Clipboard";
                            }}, 2000);
                        }}).catch(function(err) {{
                            console.error('Failed to copy:', err);
                        }});
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
