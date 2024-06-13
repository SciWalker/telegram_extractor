import json
import csv
import ast
agentic=False
with open('data/raw/channel_messages.json') as f:
    messages = json.load(f)
# trim the messages to only include the message text
trimmed_messages_list = []
for message in messages:
    if message.get('message') is not None and message.get('reactions') is not None:
        if message['reactions']['results'] is None or len(message['reactions']['results']) == 0:
            continue
        trimmed_messages={}
        trimmed_messages["message"]=(message['message'])
        trimmed_messages_reaction_count=0
        for reaction in message['reactions']['results']:
            trimmed_messages_reaction_count+=reaction['count']
        trimmed_messages['reactions']=message['reactions']['results']
        trimmed_messages["reaction_count"]=trimmed_messages_reaction_count
        # print all the keys
        trimmed_messages_list.append(trimmed_messages)



with open('data/interim/trimmed_messages.csv', 'w') as f:
    writer = csv.DictWriter(f, fieldnames=trimmed_messages_list[0].keys())
    writer.writeheader()
    for message in trimmed_messages_list:
        writer.writerow(message)
# write the trimmed messages to a new file
# with open('data/interim/trimmed_messages.json', 'w') as f:
#     json.dump(trimmed_messages, f)


import os
from langchain_community.llms import Ollama


from langchain_community.utilities import SQLDatabase
from sqlalchemy import create_engine
import pandas as pd


from langchain.prompts import PromptTemplate





db_path="data/telegram.db"
with open('data/interim/trimmed_messages.csv') as f:
    df = pd.read_csv(f)
# check if the table exists
if os.path.exists(db_path):
    os.remove(db_path)
engine = create_engine("sqlite:///data/telegram.db")
try:
    df.to_sql("telegram", engine, index=False)
except:
    print("Table already exists")

db = SQLDatabase(engine=engine)
print(db.dialect)
print(db.get_usable_table_names())
# update db to use the new table
# db.update_table("telegram")
def _handle_error(error) -> str:
    return str(error)[:50]
from langchain_community.agent_toolkits import create_sql_agent
llm = Ollama(
    model="phi3"
)
if agentic==True:
    agent_executor = create_sql_agent(llm, db=db, max_iterations=25,handle_parsing_errors="_handle_error",verbose=True)
    agent_executor.invoke({"input": "first, query all the messages from the 'telegram' table that have >50 reaction_count . Next, summarize and tell me, what are the main trends in the messages that have >50 reaction_count, "})
else:
    result=db.run("SELECT * FROM telegram WHERE reaction_count > 10;")

    # Define the prompt template
    prompt_template = PromptTemplate(
        input_variables=["text", "reactions", "likes"],
        template="""
        Analyze the following post:

        Text: {text}

        Reactions: {reactions}

        Number of Likes: {likes}

        Provide an analysis including the general sentiment, the level of engagement, and any other notable observations.
        """
    )
    # Function to analyze each post
    def analyze_post(post):
        text, reactions, likes=post
        prompt = prompt_template.format(text=text, reactions=reactions, likes=likes)
        response = llm(prompt)
        return response
    # Remove any extraneous escape characters
    # result = result.replace("\\n", "\n").replace('\\"', '"')
    # Evaluate the cleaned string as a Python expression
    tuple_list = ast.literal_eval(result)
    # Analyze each post in the string list
    analysis_results = [analyze_post(post) for post in tuple_list]

    # save the results to a file
    with open('data/processed/analysis_results.txt', 'w') as f:
        for result in analysis_results:
            f.write(result + '\n')
    