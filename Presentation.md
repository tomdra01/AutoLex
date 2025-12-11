## 1. 🌐 The Problem Context
[Slov-Lex.sk](https://www.slov-lex.sk/)

* **The Domain:** Slov-Lex is the unified central database for all Slovak legislation.
* **The Pain Point:**
    * No public API for downloading documents.
    * Manual research requires navigating complex filters and finding amendments one by one.
    * **Goal:** Automate this process using an AI Agent that can "reason" about search queries.

---

## 2. 🏗️ System Architecture

* **Framework:** Built on **AutoGen** (Multi-Agent System) powered by **Mistral Nemo**.
* **Design Pattern:** Professional "Src Layout" for modularity.
    * `src/agents/`: **The Brain** (Reasoning & Planning).
    * `src/tools/`: **The Muscle** (Execution & Scraping).
    * `coding/`: **The Sandbox** (Safe execution environment).

---

## 3. 🧠 The "Brain" `src/agents/legal_researcher.py`

* **Role:** The `Legal_Researcher` agent acts as the autonomous planner.
* **Prompt Engineering:**
    * **Workflow:** Strictly defined pipeline: `SCAN` $\rightarrow$ `DOWNLOAD` $\rightarrow$ `SUMMARIZE`.
    * **Safety Mechanism:** Implemented a **Critical Termination Rule** to prevent infinite "polite loops" common in LLMs.

---

## 4. ⚡ The Scanner `src/tools/scanner.py`

* **The Challenge:** Sequential HTTP requests are too slow (IO-bound latency).
* **The Solution:** Implemented **Multi-threading** (`concurrent.futures`).
    * **Performance:** Scans ~600 laws (one legislative year) in seconds by running **20 parallel workers**.
    * **Efficiency:** Fetches lightweight XML metadata first, avoiding heavy PDF downloads.

---

## 5. 🧩 The Fetcher `src/tools/fetcher.py`
`_guess_and_download_pdf` method

* **The Core Difficulty:** Slov-Lex PDF URLs are **non-deterministic**.
    * *Example:* Law ID `57` isn't `law_57.pdf`. It is `ZZ_2020_57_20200327.pdf` (contains a dynamic validity date).
* **The Heuristic Algorithm:**
    1.  **Parse:** Download XML metadata to extract official dates (`ucinny`, `vyhlaseny`).
    2.  **Generate:** Create a candidate list of filenames (Target Date $\pm$ 2 days).
    3.  **Brute-force:** Test URLs against the server until a `200 OK` response is received.

---

## 6. 🔮 Future Work
* **RAG (Retrieval Augmented Generation):** Indexing downloaded text into a Vector DB (ChromaDB) to enable "Chat with your Law" functionality.
* **Web Frontend:** Migrating from CLI to a React/FastAPI dashboard.