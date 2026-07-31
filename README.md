# ⚡ Cadence SKILL Script Generator

> **Plain English → Ready-to-run Cadence SKILL code in seconds**

An AI-powered tool that generates Cadence Allegro SKILL automation scripts from natural language descriptions. Built by an EDA automation engineer with 6+ years of SKILL programming experience — the AI understands real PCB design workflows, not just generic code patterns.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![LangChain](https://img.shields.io/badge/LangChain-Latest-green)
![Groq](https://img.shields.io/badge/Groq-LLaMA_3.3_70B-orange)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-red)

---

## 🎯 What It Does

Instead of writing SKILL code manually, just describe what you want:

| You type | You get |
|---|---|
| *"Find all components on TOP layer and print their RefDes"* | Complete SKILL procedure with `axlGetCells`, file output, error handling |
| *"Place all decoupling caps within 200 mils of their IC"* | SKILL code with proximity checks and placement logic |
| *"Generate a report of all vias with X Y coordinates"* | Via iterator with formatted CSV output |
| *"Highlight all nets connected to VCC and GND"* | Net traversal with highlight commands |

---

## 🚀 Live Demo

> 🔗 **[Try it live on Streamlit Cloud](#)** *(coming soon)*

---

## 🛠️ Tech Stack

- **LangChain** — Prompt chaining and LLM orchestration
- **Groq API** — LLaMA 3.3 70B for fast, accurate code generation
- **Streamlit** — Clean web UI, no frontend knowledge needed
- **Python 3.12** — Core application logic

---

## ⚙️ Features

- 🧠 **Domain-aware AI** — Trained prompt understands real Cadence SKILL APIs (`axlGetCurrentDesign`, `axlGetCells`, `axlDBCreateShape`, etc.)
- 📋 **8 example tasks** — Click to auto-fill and generate instantly
- ⚙️ **Advanced options** — Toggle GUI dialogs, log file output, Allegro version
- ⬇️ **Download as .il file** — Ready to load directly in Allegro PCB Editor
- 🔄 **Regenerate** — Get alternative implementations instantly
- 🎚️ **Creativity slider** — Control precision vs. creativity of generated code

---

## 📦 Installation

```bash
# Clone the repo
git clone https://github.com/karthikeyankcse/skill-script-generator.git
cd skill-script-generator

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Create .env file with your Groq API key
echo GROQ_API_KEY=your_key_here > .env
```

Get your free Groq API key at **[console.groq.com](https://console.groq.com)**

---

## ▶️ Run

```bash
streamlit run app.py
```

Open **http://localhost:8501** in your browser.

---

## 📖 How to Use Generated Code in Allegro

1. Click **⬇️ Download .il file**
2. Open **Cadence Allegro PCB Editor**
3. In the command window type: `load("path/to/generated_skill.il")`
4. The script auto-runs — check `component_log.txt` for output

---

## 🧠 Why This Exists

EDA engineers spend hours writing repetitive SKILL scripts for tasks like:
- Extracting component data
- Running custom DRC checks
- Automating placement tasks
- Generating custom reports

This tool generates those scripts in seconds — letting engineers focus on design, not scripting syntax.

---

## 👤 Author

**Karthikeyan K** — EDA Automation Engineer | 6+ years Cadence SKILL | Python | AI  
📧 karthikeyankcse@gmail.com  
🔗 [github.com/karthikeyankcse](https://github.com/karthikeyankcse)

---

## 📄 License

MIT License — free to use and modify.