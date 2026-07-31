import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os

# Load API key from .env file
load_dotenv()

# ── Page config ──────────────────────────────────────────
st.set_page_config(
    page_title="SKILL Script Generator",
    page_icon="⚡",
    layout="wide"
)

# ── App Header ────────────────────────────────────────────
st.title("⚡ Cadence SKILL Script Generator")
st.markdown("**Describe your PCB automation task in plain English → Get ready-to-run SKILL code**")
st.divider()

# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")

    model = st.selectbox(
        "Groq Model",
        ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"],
        index=0
    )

    temperature = st.slider("Creativity", 0.0, 1.0, 0.2, 0.1,
                            help="Lower = more precise code. Higher = more creative.")

    st.divider()
    st.header("📋 Example Tasks")
    examples = [
        "Find all components on TOP layer and print their RefDes",
        "Place all decoupling caps within 200 mils of their IC",
        "Check minimum clearance between all copper shapes on signal layers",
        "Generate a report of all vias with their X Y coordinates",
        "Highlight all nets connected to VCC and GND",
        "Find all components with value 100nF and list their locations",
        "Change all silkscreen text height to 60 mils",
        "Delete all empty copper shapes on all layers",
    ]
    for ex in examples:
        if st.button(ex, use_container_width=True):
            st.session_state.user_input = ex

    st.divider()
    st.caption("Built by Karthikeyan K | EDA + AI")

# ── System Prompt ─────────────────────────────────────────
SYSTEM_PROMPT = """You are an expert Cadence Allegro SKILL programming assistant with deep knowledge of:
- Cadence Allegro PCB Editor SKILL API
- axlDB functions (axlGetCurrentDesign, axlGetCell, axlGetPadstack, etc.)
- axlUI functions for user interface interactions
- Design object manipulation (components, pins, nets, shapes, vias)
- Layer operations and design rule checking
- Common PCB automation patterns

When the user describes a PCB automation task, generate complete, working Cadence SKILL code that:
1. Is properly structured with a main function
2. Includes error handling using axlError and axlMsgPop
3. Has clear comments explaining each section
4. Uses correct SKILL syntax (procedure, let, foreach, when, unless, etc.)
5. Returns meaningful output to the user via printf or axlMsgPop
6. Can be loaded and run directly in Allegro PCB Editor

Always:
- Start with a procedure definition
- Use axlGetCurrentDesign() to get the design object
- Include proper variable declarations using let()
- Add a header comment explaining what the script does
- End with calling the main procedure

Return ONLY the SKILL code with comments. No explanations outside the code block."""

# ── Main UI ───────────────────────────────────────────────
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("📝 Describe Your Task")

    user_input = st.text_area(
        "What do you want to automate in Cadence Allegro?",
        value=st.session_state.get("user_input", ""),
        height=150,
        placeholder="Example: Find all components on the TOP layer and print their RefDes and X Y coordinates to a file..."
    )

    # Extra context options
    with st.expander("⚙️ Advanced Options"):
        include_gui = st.checkbox("Include GUI dialog/form", value=False)
        include_log = st.checkbox("Write output to log file", value=True)
        allegro_version = st.selectbox("Allegro Version", ["17.4", "17.2", "22.1"], index=0)
        extra_context = st.text_area("Additional context (optional)",
                                      placeholder="e.g. Design has 6 layers, components use imperial units...",
                                      height=80)

    generate_btn = st.button("⚡ Generate SKILL Code", type="primary", use_container_width=True)

with col2:
    st.subheader("💻 Generated SKILL Code")

    if generate_btn and user_input.strip():
        # Build enhanced prompt
        enhanced_prompt = f"Task: {user_input}"
        if include_gui:
            enhanced_prompt += "\nRequirement: Include an axlForm-based GUI dialog for user input."
        if include_log:
            enhanced_prompt += "\nRequirement: Write all output to a log file using outfile/fprintf."
        if allegro_version:
            enhanced_prompt += f"\nAllegro Version: {allegro_version}"
        if extra_context:
            enhanced_prompt += f"\nAdditional context: {extra_context}"

        with st.spinner("🤖 Generating SKILL code..."):
            try:
                # Initialize LLM
                llm = ChatGroq(
                    model=model,
                    temperature=temperature,
                    api_key=os.getenv("GROQ_API_KEY")
                )

                # Create prompt
                prompt = ChatPromptTemplate.from_messages([
                    ("system", SYSTEM_PROMPT),
                    ("human", "{task}")
                ])

                # Generate
                chain = prompt | llm
                response = chain.invoke({"task": enhanced_prompt})
                generated_code = response.content

                # Store in session
                st.session_state.generated_code = generated_code
                st.session_state.last_task = user_input

            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.info("Check your GROQ_API_KEY in the .env file")

    # Display generated code
    if "generated_code" in st.session_state:
        code = st.session_state.generated_code

        # Clean up markdown code blocks if present
        if "```" in code:
            lines = code.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            code = "\n".join(lines)

        st.code(code, language="lisp")

        # Action buttons
        col_a, col_b = st.columns(2)
        with col_a:
            st.download_button(
                "⬇️ Download .il file",
                data=code,
                file_name="generated_skill.il",
                mime="text/plain",
                use_container_width=True
            )
        with col_b:
            if st.button("🔄 Regenerate", use_container_width=True):
                if "generated_code" in st.session_state:
                    del st.session_state.generated_code
                st.rerun()

        # Usage instructions
        with st.expander("📖 How to run in Cadence Allegro"):
            st.markdown("""
            1. Download the `.il` file using the button above
            2. Open **Cadence Allegro PCB Editor**
            3. Go to **File → Script** or open the **SKILL REPL** (`skill_repl` in command window)
            4. Type: `load("path/to/generated_skill.il")`
            5. Call the main procedure name shown at the bottom of the script
            
            **Tip:** Always test on a copy of your design first!
            """)

    elif not generate_btn:
        st.info("👈 Describe your task and click **Generate SKILL Code**")

# ── Footer ────────────────────────────────────────────────
st.divider()
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 12px;'>
    SKILL Script Generator | Built with Python + LangChain + Groq LLaMA 3.3 | 
    <a href='https://github.com/karthikeyankcse' target='_blank'>github.com/karthikeyankcse</a>
    </div>
    """,
    unsafe_allow_html=True
)