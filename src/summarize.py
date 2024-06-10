import json
import csv
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
db_path="data/telegram.db"
with open('data/interim/trimmed_messages.csv') as f:
    df = pd.read_csv(f)
# check if the table exists
if os.path.exists(db_path):
    os.remove(db_path)
engine = create_engine("sqlite:///telegram.db")
df.to_sql("telegram", engine, index=False)


db = SQLDatabase(engine=engine)
print(db.dialect)
print(db.get_usable_table_names())
result=db.run("SELECT * FROM telegram WHERE reaction_count > 100;")
# update db to use the new table
# db.update_table("telegram")
def _handle_error(error) -> str:
    return str(error)[:50]

print("result:",result)
from langchain_community.agent_toolkits import create_sql_agent
llm = Ollama(
    model="phi3"
)
agent_executor = create_sql_agent(llm, db=db, max_iterations=25,handle_parsing_errors="_handle_error",verbose=True)
agent_executor.invoke({"input": "first, query all the messages from the 'telegram' table that have >50 reaction_count . Next, summarize and tell me, what are the main trends in the messages that have >50 reaction_count, "})