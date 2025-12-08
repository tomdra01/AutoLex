# AutoLex ⚖️🇸🇰

**AutoLex** is an AI Agent designed to autonomously research and retrieve Slovak legislation from the [Slov-Lex](https://www.slov-lex.sk/) database.

Built on the **AutoGen** framework (powered by **Mistral Nemo**), AutoLex replaces manual searching with an intelligent agentic workflow. It understands natural language requests (e.g., *"Find 2024 election laws"*), scans law metadata in parallel, and autonomously downloads official PDFs.

## 🚀 Features

* **Natural Language Search:** Find laws by topic and year using plain English or Slovak.
* **Agentic Workflow:** The AI autonomously decides when to scan the index versus when to download specific files.
* **High-Speed Scanning:** Multi-threaded scanner checks hundreds of law titles in seconds.
* **Smart Retrieval:** Includes a heuristic engine to "guess" and locate valid PDF URLs (resolving dynamic validity dates).
* **Modular Architecture:** Professional `src` layout separating agents, tools, and configuration.

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