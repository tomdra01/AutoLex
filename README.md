# AutoLex ⚖️🇸🇰

**AutoLex** is an AI Agent designed to autonomously research and retrieve Slovak legislation from the [Slov-Lex](https://www.slov-lex.sk/) database.

Built on the **AutoGen** framework (powered by **Mistral Nemo**), AutoLex replaces manual searching with an intelligent agentic workflow. It understands natural language requests (*"Find 2024 election laws"*), scans law metadata in parallel, and autonomously downloads official PDFs.

## 🚀 Features

* **Natural Language Search:** Find laws by topic and year using plain English or Slovak.
* **Agentic Workflow:** The AI autonomously decides when to scan the index versus when to download specific files.
* **High-Speed Scanning:** Multi-threaded scanner checks hundreds of law titles in seconds.
* **Smart Retrieval:** Includes a heuristic engine to "guess" and locate valid PDF URLs (resolving dynamic validity dates).
* **Modular Architecture:** Professional `src` layout separating agents, tools, and configuration.

## 💡 Technical Highlight: Dynamic PDF Retrieval

One of the core technical challenges in scraping Slov-Lex is that **PDF URLs are not predictable**.
* A law with ID `57` from `2020` is **not** simply named `law_57_2020.pdf`.
* The filename includes a dynamic "validity date" string, e.g., `ZZ_2020_57_20200327.pdf`.

**AutoLex solves this by:**
1.  Downloading the law's **XML metadata** first.
2.  Parsing the XML to extract key dates (e.g., "Declared Date", "Effective Date").
3.  Mathematically generating a list of potential filenames by applying a ±2 day offset to these dates.
4.  Testing these URLs against the server until the correct official document is found.

## 🛠️ Architecture

The system uses a Multi-Agent architecture:
* **`User_Proxy`:** Acts as the project manager, handling code execution and file system operations.
* **`Legal_Researcher`:** The AI brain that interprets user intent, plans the research, and executes tool calls.
* **`scanner.py`:** A parallelized tool for fast metadata searching.
* **`fetcher.py`:** A specialized downloader for retrieving XMLs and resolving PDF paths.

## 📂 Project Structure

```text
AutoLex/
├── src/
│   ├── agents/           # Agent definitions (prompts & config)
│   ├── tools/            # Python tools (Scanner & Fetcher)
│   └── config.py         # API Keys & Constants
├── main.py               # Application entry point
├── requirements.txt      # Dependencies
└── downloads/            # Output folder for XML/PDFs
```

## ⚙️ Dependencies

* **Python 3.10+**
* **pyautogen** (or `autogen`): The framework for building multi-agent systems.
* **mistralai**: The official client for interacting with Mistral's LLM API.
* **lxml**: A high-performance library for parsing Slov-Lex XML metadata.
* **python-dotenv**: For managing environment variables (API keys) securely.
* **requests**: For handling HTTP requests to download laws and PDFs.
* **fix-busted-json**: A utility to repair malformed JSON responses from the LLM.

## 🚀 Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/tomdra01/AutoLex.git
cd autolex
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
AutoLex requires a Mistral API key (or any OpenAI-compatible key).
Create a `.env` file in the root directory with the following content:
```env
MISTRAL_API_KEY=your_actual_api_key_here
```
### 4. Run the Application
Configure the Task: Open main.py and modify the variables at the top to define your research goal:
```python
TARGET_YEAR = 2024
TARGET_TOPIC = "volieb"  # e.g., "dane" (taxes), "skolstvo" (education)
```
Then execute:
```bash
python main.py
```
View the downloaded XML and PDF files in the `downloads/` folder.

## 📄 License
This project is for educational purposes. Please respect the terms of service of the data source (Slov-Lex).
