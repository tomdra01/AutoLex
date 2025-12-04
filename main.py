import os
import autogen
from src.agents.user_proxy import user_proxy
from src.agents.legal_researcher import legal_researcher
from src.tools.scraper import fetch_specific_law, scan_laws_for_keyword

TARGET_YEAR = 2020
TARGET_TOPIC = "volieb"  # Try: "dane" (taxes), "skolstvo" (education)
TASK_PROMPT = f"Find any laws from {TARGET_YEAR} related to '{TARGET_TOPIC}'."


autogen.agentchat.register_function(
    fetch_specific_law,
    caller=legal_researcher,
    executor=user_proxy,
    name="fetch_specific_law",
    description="Downloads XML and PDF for a specific Slovak law ID."
)

autogen.agentchat.register_function(
    scan_laws_for_keyword,
    caller=legal_researcher,
    executor=user_proxy,
    name="scan_laws_for_keyword",
    description="Searches law titles for a keyword."
)

if __name__ == "__main__":
    if not os.path.exists("coding"):
        os.makedirs("coding")

    print(f"Starting AutoLex...\nTask: {TASK_PROMPT}\n" + "-" * 40)

    user_proxy.initiate_chat(
        legal_researcher,
        message=TASK_PROMPT
    )