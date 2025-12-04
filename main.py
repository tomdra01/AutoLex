import os
import autogen
from config import llm_config
from tools.scraper import fetch_specific_law, scan_laws_for_keyword

# User Proxy Agent Configuration
user_proxy = autogen.UserProxyAgent(
    name="User_Proxy",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    code_execution_config={"work_dir": "coding", "use_docker": False},
    is_termination_msg=lambda x: "TERMINATE" in x.get("content", "")
)

# The Legal Researcher Agent
researcher = autogen.AssistantAgent(
    name="Legal_Researcher",
    system_message="""You are a Slovak Legal Researcher.

    YOUR TOOLS:
    1. scan_laws_for_keyword(year, keyword): Use this when the user asks about a TOPIC.
    2. fetch_specific_law(year, law_id): Use this when you know the Law ID.

    YOUR PROCESS:
    - If the user asks about a topic -> SCAN for it.
    - If the SCAN returns matches -> Automatically DOWNLOAD the relevant laws using 'fetch_specific_law'.
    - After downloading, summarize exactly what you found (Title, Article Count, PDF status).
    - CRITICAL: After providing the summary, do NOT ask "Is there anything else?". Just say "TERMINATE" immediately.""",
    llm_config=llm_config,
)

# Register BOTH tools to the Legal Researcher
autogen.agentchat.register_function(
    fetch_specific_law,
    caller=researcher,
    executor=user_proxy,
    name="fetch_specific_law",
    description="Downloads XML/PDF for a specific law ID."
)

# Register the Scan Tool
autogen.agentchat.register_function(
    scan_laws_for_keyword,
    caller=researcher,
    executor=user_proxy,
    name="scan_laws_for_keyword",
    description="Searches law titles for a keyword."
)

# Run with a Search Task
if __name__ == "__main__":
    if not os.path.exists("coding"):
        os.makedirs("coding")

    # Test the Search capability
    task = "Find any laws from 2024 related to 'volieb' (elections)."

    print(f"Starting Agent Task: {task}\n" + "-" * 40)

    user_proxy.initiate_chat(
        researcher,
        message=task
    )