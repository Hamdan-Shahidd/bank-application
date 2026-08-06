ai: Assisttant's brain

- retriver.py: This contains the "read the manual" part. It chops the HBLs pdf into small chunks, convert them into embeddings and then store them in a vector database. When a user asks something from the agent, it converts the questions into embeddings and return the closest chunnks to the questions. 

- agent.py: This is "decide what to do" part. It gives gemini a system prompt and whatever the retrive_policy found. Gemini then either replies with a plain text or calls a tool that is available to it. 

- __init__.py: Make the python folder a package from which we can import. 