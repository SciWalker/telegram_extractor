# telegram_extractor
this repo is about extracting useful info from telegram
steps:
1. you need to get the api_id and save those params in the config.json as follows:
 {
    "api_id": <api_id>,
    "api_hash": <api_hash>,
    "phone" : <phone_number>,
    "username" : <tg_username>
}
2. run the get_messages.py to crawl through a telegram channel
3. run summarize.py which utilizes the ollama+llm to summarize the top messages by reaction counts (you need to get ollama installed, can refer to https://ollama.com)

future works:
- Sentiment analysis
- Message categorization and topic modeling
- Integration with other messaging platforms
- Enhanced data visualization for extracted information