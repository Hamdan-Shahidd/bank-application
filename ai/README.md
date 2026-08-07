ai: Assisttant's brain

- retriver.py: This contains the "read the manual" part. It chops the HBLs pdf into small chunks, convert them into embeddings and then store them in a vector database. When a user asks something from the agent, it converts the questions into embeddings and return the closest chunnks to the questions. 

- agent.py: This is "decide what to do" part. It gives gemini a system prompt and whatever the retrive_policy found. Gemini then either replies with a plain text or calls a tool that is available to it. 

- __init__.py: Make the python folder a package from which we can import. 


Text to SQL AI agent: 
LLM never write the full query, it only writes the filter conditions. Don't use full text to SQL conversion because it can leak the user's data. The pipeline is shown below;
1. User asks "How much did I deposit last month greater than 500?"
2. LLM writes the filter conditions;
   kind = 'deposit' AND amount > 500 AND created_at >= date('now' , '-30 days')
3. Your pthon code checks if the fragemnt is safe.
4. Python code wraps it inside the real query that ALWAYS restrict results to your own user_id.
5. The database run the query.
6. The raw rows come back.
7. A second LLM call turns the rows into a normal sentence. 
Two LLM calls happen one write the filters and one describe the results. Neither touches the database directly. 
