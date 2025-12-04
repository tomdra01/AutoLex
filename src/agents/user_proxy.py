import autogen

user_proxy = autogen.UserProxyAgent(
    name="User_Proxy",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    code_execution_config={"work_dir": "coding", "use_docker": False},
    is_termination_msg=lambda x: "TERMINATE" in x.get("content", "")
)