import os
import re

import streamlit as st
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

# Load API key from .env (local) or Streamlit secrets (cloud)
load_dotenv()

# ── Page config ──────────────────────────────────────────
st.set_page_config(
    page_title="SKILL Script Generator",
    page_icon="⚡",
    layout="wide",
)

# ── Models (check console.groq.com/docs/deprecations if you get a 404) ──
MODEL_OPTIONS = [
    "openai/gpt-oss-120b",
    "qwen/qwen3.6-27b",
    "openai/gpt-oss-20b",
]
DEFAULT_MODEL = os.getenv("GROQ_MODEL", MODEL_OPTIONS[0])
if DEFAULT_MODEL not in MODEL_OPTIONS:
    MODEL_OPTIONS.insert(0, DEFAULT_MODEL)

# ── Header ────────────────────────────────────────────────
st.title("⚡ Cadence SKILL Script Generator")
st.markdown("**Describe your PCB automation task in plain English → get a draft SKILL script**")

st.divider()

# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")

    model = st.selectbox("Groq Model", MODEL_OPTIONS, index=MODEL_OPTIONS.index(DEFAULT_MODEL))

    temperature = st.slider(
        "Creativity", 0.0, 1.0, 0.2, 0.1,
        help="Lower = more precise code. Higher = more creative.",
    )

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
SYSTEM_PROMPT = """You are an expert Cadence Allegro PCB Editor SKILL programmer.

Generate complete SKILL code for the task the user describes.

Rules:
1. Use only documented Allegro SKILL functions you are confident exist, for example:
   axlDBGetDesign, axlSetFindFilter, axlAddSelectAll, axlGetSelSet, axlClearSelSet,
   axlDeleteObject, axlHighlightObject, axlDehighlightObject, axlGetActiveLayer,
   axlDBCreateShape, axlDBCreateText, axlUIWPrint, axlFormCreate, axlFormDisplay.
   Database objects are accessed with attributes, for example
   axlDBGetDesign()->components, ->nets, ->vias, ->shapes, and ->refdes, ->xy.
2. Never invent function names. If you are not sure a function exists, still write
   the best attempt but add a comment line starting with ;; VERIFY: explaining what to check.
3. Wrap the logic in a procedure with a clear name, use let() for local variables,
   and check for nil before using results.
4. Print results with axlUIWPrint or write them to a file with outfile / fprintf / close.
5. Add short comments explaining each section.
6. End by calling the main procedure.

Return only the SKILL code with comments. No text outside the code."""

# ── Main UI ───────────────────────────────────────────────
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("📝 Describe Your Task")

    user_input = st.text_area(
        "What do you want to automate in Cadence Allegro?",
        value=st.session_state.get("user_input", ""),
        height=150,
        placeholder="Example: Find all components on the TOP layer and print their RefDes and X Y coordinates to a file...",
    )

    with st.expander("⚙️ Advanced Options"):
        include_gui = st.checkbox("Include GUI dialog/form", value=False)
        include_log = st.checkbox("Write output to log file", value=True)
        allegro_version = st.selectbox("Allegro Version", ["17.4", "17.2", "22.1"], index=0)
        extra_context = st.text_area(
            "Additional context (optional)",
            placeholder="e.g. Design has 6 layers, components use imperial units...",
            height=80,
        )

    generate_btn = st.button("⚡ Generate SKILL Code", type="primary", use_container_width=True)

with col2:
    st.subheader("💻 Generated SKILL Code")

    if generate_btn and user_input.strip():
        enhanced_prompt = f"Task: {user_input}"
        if include_gui:
            enhanced_prompt += "\nRequirement: Include an axlFormCreate-based dialog for user input."
        if include_log:
            enhanced_prompt += "\nRequirement: Write all output to a log file using outfile/fprintf."
        if allegro_version:
            enhanced_prompt += f"\nAllegro Version: {allegro_version}"
        if extra_context:
            enhanced_prompt += f"\nAdditional context: {extra_context}"

        with st.spinner("🤖 Generating SKILL code..."):
            try:
                llm = ChatGroq(
                    model=model,
                    temperature=temperature,
                    api_key=os.getenv("GROQ_API_KEY"),
                )

                prompt = ChatPromptTemplate.from_messages([
                    ("system", SYSTEM_PROMPT),
                    ("human", "{task}"),
                ])

                chain = prompt | llm
                response = chain.invoke({"task": enhanced_prompt})

                st.session_state.generated_code = response.content
                st.session_state.last_task = user_input

            except Exception as e:
                msg = str(e)
                st.error(f"Error: {msg}")
                if "model_not_found" in msg or "404" in msg:
                    st.info(
                        "The selected model may have been retired. Pick another model in the "
                        "sidebar, or check console.groq.com/docs/deprecations"
                    )
                elif "401" in msg or "invalid_api_key" in msg.lower():
                    st.info("Check your GROQ_API_KEY in the .env file or Streamlit secrets.")
                elif "429" in msg:
                    st.info("Rate limit reached. Wait a minute and try again.")

    if "generated_code" in st.session_state:
        code = st.session_state.generated_code

        # Remove any reasoning text some models put in <think> tags
        code = re.sub(r"<think>.*?</think>", "", code, flags=re.DOTALL).strip()

        # Remove markdown code fences if present
        if "```" in code:
            lines = [l for l in code.split("\n") if not l.strip().startswith("```")]
            code = "\n".join(lines).strip()

        st.code(code, language="lisp")

        col_a, col_b = st.columns(2)
        with col_a:
            st.download_button(
                "⬇️ Download .il file",
                data=code,
                file_name="generated_skill.il",
                mime="text/plain",
                use_container_width=True,
            )
        with col_b:
            if st.button("🔄 Regenerate", use_container_width=True):
                del st.session_state.generated_code
                st.rerun()

        with st.expander("📖 How to run in Cadence Allegro"):
            st.markdown(
                """
1. Download the `.il` file using the button above
2. Open **Cadence Allegro PCB Editor**
3. In the command window type: `skill load("path/to/generated_skill.il")`
4. Check the CIW or the log file for the output

**Tip:** Read the code and test on a copy of your design first.
                """
            )

    elif not generate_btn:
        st.info("👈 Describe your task and click **Generate SKILL Code**")

# ── Footer ────────────────────────────────────────────────
st.divider()
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 12px;'>
    SKILL Script Generator | Built with Python + LangChain + Groq |
    <a href='https://github.com/karthikeyankcse' target='_blank'>github.com/karthikeyankcse</a>
    </div>
    """,
    unsafe_allow_html=True,
)
