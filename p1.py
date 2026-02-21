import streamlit as st
from groq import Groq
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Code Mentor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .feature-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
def init_session_state():
    defaults = {
        'code_history': [],
        'current_language': 'Python',
        'explanation_style': 'Beginner-Friendly',
        'conversation': [],
        'last_explanation': '',
        'last_code': ''
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# --- Helper Functions ---
def get_style_prompt(style: str) -> str:
    style_prompts = {
        "Beginner-Friendly": """
        Explain this code as if to someone completely new to programming.
        - Start with a simple overview of what the code does
        - Explain each line in plain English
        - Use everyday analogies where possible
        - Point out common mistakes beginners make
        """,
        "Technical Deep Dive": """
        Provide a technical deep dive:
        - Explain syntax and semantics precisely
        - Discuss time/space complexity if applicable
        - Mention language-specific features and best practices
        - Suggest potential optimizations
        """,
        "With Analogies": """
        Use analogies and real-world comparisons:
        - Compare code concepts to everyday objects/situations
        - Use metaphors that non-programmers would understand
        - Create visual mental models
        """,
        "Problem-Solver": """
        Focus on the problem being solved:
        - What real-world problem does this code solve?
        - What are alternative approaches to solve this?
        - When would we use this pattern vs another?
        """
    }
    return style_prompts.get(style, style_prompts["Beginner-Friendly"])

def generate_explanation(client, code: str, language: str, style: str) -> str:
    style_prompt = get_style_prompt(style)
    
    prompt = f"""
    You are an expert {language} programming tutor.
    
    EXPLANATION STYLE: {style_prompt}
    
    CODE TO EXPLAIN:
    ```{language.lower()}
    {code}
    ````
    
    Provide your explanation in this format:
    
    ## 🎯 Summary
    [One sentence explaining what this code does]
    
    ## 📝 Line-by-Line Breakdown
    [Explain each line clearly]
    
    ## 🔑 Key Concepts
    [List the important programming concepts used]
    
    ## ⚠️ Common Pitfalls
    [What mistakes should beginners avoid?]
    
    ## 💡 Practice Exercise
    [Suggest a small modification or exercise to practice]
    """
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",  # FREE model on Groq!
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=2000
    )
    return response.choices[0].message.content

def get_chat_response(client, conversation: list, question: str, language: str) -> str:
    context = "\n".join([
        f"{'User' if m['role'] == 'user' else 'Assistant'}: {m['content']}" 
        for m in conversation[-6:]
    ])
    
    prompt = f"""
    You are a friendly {language} coding tutor having a conversation.
    
    Previous conversation:
    {context}
    
    User's new question: {question}
    
    Provide a helpful, clear answer. Use code examples in markdown when helpful.
    """
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=1000
    )
    return response.choices[0].message.content

# --- Sidebar Configuration ---
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Key Input
    api_key = st.text_input(
        "🔑 Groq API Key (FREE!)",
        type="password",
        help="Get your FREE key from https://console.groq.com/"
    )
    
    if api_key:
        st.success("✅ API Key provided")
    else:
        st.warning("⚠️ API Key required")
    
    st.markdown("---")
    
    # Language Selection
    st.session_state.current_language = st.selectbox(
        "💻 Programming Language",
        ["Python", "JavaScript", "Java", "C++", "C#", "Go", "Ruby", "PHP", "Swift", "Kotlin", "TypeScript", "Rust", "HTML/CSS", "SQL"]
    )
    
    # Explanation Style
    st.session_state.explanation_style = st.radio(
        "📚 Explanation Style",
        ["Beginner-Friendly", "Technical Deep Dive", "With Analogies", "Problem-Solver"]
    )
    
    st.markdown("---")
    
    # Statistics
    st.markdown("### 📊 Your Stats")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Sessions", len(st.session_state.code_history))
    with col2:
        languages_used = len(set(h.get('language', 'Python') for h in st.session_state.code_history)) if st.session_state.code_history else 0
        st.metric("Languages", languages_used)
    
    st.markdown("---")
    
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.code_history = []
        st.session_state.conversation = []
        st.session_state.last_explanation = ''
        st.session_state.last_code = ''
        st.rerun()
    
    with st.expander("❓ Get FREE API Key"):
        st.markdown("""
        **Groq is 100% FREE!**
        
        1. Go to [console.groq.com](https://console.groq.com/)
        2. Sign up with Google/GitHub
        3. Go to **API Keys**
        4. Click **Create API Key**
        5. Copy and paste here!
        
        ✅ No credit card needed
        ✅ Very fast responses
        ✅ Generous free limits
        """)

# --- Main Content ---
st.markdown('<h1 class="main-header">🎓 AI Code Mentor</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: gray;">Your personal AI tutor for understanding code • Powered by Groq (FREE!)</p>', unsafe_allow_html=True)

# Check API Key
if not api_key:
    st.markdown("""
    <div class="feature-box">
        <h3>👋 Welcome to AI Code Mentor!</h3>
        <p>This tool helps you understand any code snippet with AI-powered explanations.</p>
        <h4>Features:</h4>
        <ul>
            <li>📝 Line-by-line code explanations</li>
            <li>💬 Ask follow-up questions</li>
            <li>🌍 Support for 14+ programming languages</li>
            <li>🎯 4 different explanation styles</li>
            <li>📊 Track your learning progress</li>
        </ul>
        <p><strong>👈 Enter your FREE Groq API key in the sidebar to start!</strong></p>
        <p>Get your free key at: <a href="https://console.groq.com/" target="_blank">console.groq.com</a></p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# Configure Groq Client
try:
    client = Groq(api_key=api_key)
except Exception as e:
    st.error(f"❌ Error configuring API: {str(e)}")
    st.stop()

# --- Main Tabs ---
tab1, tab2, tab3 = st.tabs(["📝 Explain Code", "💬 Ask Questions", "📜 History"])

# Tab 1: Code Explainer
with tab1:
    code_input = st.text_area(
        f"Paste your {st.session_state.current_language} code here:",
        height=200,
        placeholder="# Paste your code here...\nprint('Hello, World!')",
        key="code_input_area"
    )
    
    with st.expander("📚 Load Example Code"):
        col1, col2, col3 = st.columns(3)
        
        examples = {
            "Python - Loop": """for i in range(5):
    print(f"Count: {i}")
print("Done!")""",
            "Python - Function": """def greet(name):
    message = f"Hello, {name}!"
    return message

result = greet("World")
print(result)""",
            "JavaScript": """const numbers = [1, 2, 3, 4, 5];
const doubled = numbers.map(n => n * 2);
console.log(doubled);"""
        }
        
        for i, (name, code) in enumerate(examples.items()):
            col = [col1, col2, col3][i % 3]
            with col:
                if st.button(name, key=f"example_{i}", use_container_width=True):
                    st.session_state.code_input_area = code
                    st.rerun()
    
    if st.button("🔍 Explain This Code", type="primary", use_container_width=True):
        if not code_input.strip():
            st.warning("⚠️ Please enter some code first!")
        else:
            with st.spinner("🧠 Analyzing your code..."):
                try:
                    explanation = generate_explanation(
                        client,
                        code_input,
                        st.session_state.current_language,
                        st.session_state.explanation_style
                    )
                    
                    st.session_state.last_explanation = explanation
                    st.session_state.last_code = code_input
                    st.session_state.code_history.append({
                        'code': code_input,
                        'explanation': explanation,
                        'language': st.session_state.current_language,
                        'style': st.session_state.explanation_style,
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M")
                    })
                    
                    st.session_state.conversation = [
                        {"role": "user", "content": f"Explain this code:\n```\n{code_input}\n```"},
                        {"role": "assistant", "content": explanation}
                    ]
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.info("Check your API key or try again.")
    
    if st.session_state.last_explanation:
        st.markdown("---")
        st.markdown("### 📖 Explanation")
        
        with st.expander("👁️ View Code", expanded=False):
            st.code(st.session_state.last_code, language=st.session_state.current_language.lower())
        
        st.markdown(st.session_state.last_explanation)
        
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💬 Ask a Question", use_container_width=True):
                st.info("👉 Go to the 'Ask Questions' tab!")
        with col2:
            if st.button("🔄 Clear & Start Over", use_container_width=True):
                st.session_state.last_explanation = ''
                st.rerun()

# Tab 2: Q&A Chat
with tab2:
    st.markdown("### 💬 Ask Follow-up Questions")
    
    if not st.session_state.conversation:
        st.info("👈 First, explain some code in the 'Explain Code' tab!")
    else:
        for message in st.session_state.conversation:
            role = message["role"]
            content = message["content"]
            
            if role == "user":
                st.markdown(f"**🧑 You:**")
            else:
                st.markdown(f"**🤖 Mentor:**")
            st.markdown(content)
            st.markdown("---")
        
        question = st.text_input(
            "Ask a question:",
            placeholder="Why do we use a loop here?",
            key="question_input"
        )
        
        col1, col2 = st.columns([3, 1])
        with col1:
            ask_button = st.button("📤 Send", type="primary", use_container_width=True)
        with col2:
            if st.button("🗑️ Clear", use_container_width=True):
                st.session_state.conversation = []
                st.rerun()
        
        if ask_button and question:
            with st.spinner("Thinking..."):
                try:
                    st.session_state.conversation.append({"role": "user", "content": question})
                    
                    response = get_chat_response(
                        client,
                        st.session_state.conversation,
                        question,
                        st.session_state.current_language
                    )
                    
                    st.session_state.conversation.append({"role": "assistant", "content": response})
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# Tab 3: History
with tab3:
    st.markdown("### 📜 Learning History")
    
    if not st.session_state.code_history:
        st.info("No history yet!")
    else:
        st.markdown(f"**Total Sessions:** {len(st.session_state.code_history)}")
        
        for i, session in enumerate(reversed(st.session_state.code_history), 1):
            with st.expander(f"📌 Session {i} - {session['language']} ({session['timestamp']})"):
                st.code(session['code'], language=session['language'].lower())
                preview = session['explanation'][:300] + "..."
                st.markdown(preview)

# Footer
st.markdown("---")
st.markdown(
    '<p style="text-align: center; color: gray;">🎓 AI Code Mentor | Powered by Groq (FREE!) | Built for Hackathon</p>',
    unsafe_allow_html=True
)