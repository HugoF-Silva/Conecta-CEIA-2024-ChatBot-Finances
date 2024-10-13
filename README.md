# Conecta-CEIA-2024-ChatBot-Finances

 ChatBot as free educational purpose. The main goal is to show some techniques that people use today to levarage fast chatbot POCs and/or MVPs to solve real problems. This is 1 of 3 chatbots shown.
 This bot uses OpenAI API Key, and while the class was being held, it was available for use until the class ended or the credit ended.
 If you want to run the chatbot, you will need your own OpenAI API key.

 The code isn't OOP organized nor correctly divided considering functional programming.
 
 The translation in the `preprocessing.ipynb` colab uses googletrans, which has conflict with the supabase version I was using.
 
 It didn't bother me because I'm not doing a real case application, but I know it can bother you, so attention:
 
 -> Supabase is used all the time at the backend, you can change for another db that features vector stores or replace for a local vector store
 
 -> `supabase==2.9.0` needs `httpx==0.27.2`
 
 -> `googletrans==4.0.0-rc1` needs `httpx==0.13.3`

 -> Googletrans will be used just while you are translating your dataset (if you want)
 
 -> Googletrans isn't the best way to translate a dataset, there's actually [this good repo](https://github.com/vTuanpham/Large_dataset_translator?tab=readme-ov-file) if you want
 
 -> Googletrans can't handle properly some requests, so you will need to rerun translation to some row values.
 
 -> Or you can just solve this and replace this `preprocessing.ipynb` for your own preprossing.

# N8N workflow:

This was my "backend".
You can see that there's a `FinBot_copy.json`. To use this, you will need your n8n account, and import this file to the n8n, and then set the supabase credentials, your google console project oauth (that enables api calls to drive), and openai credentials.

You will also need to set the credentials where is defined `os.getenv()`.
I can't give you mine haha. Google console api credentials can be a pain in the ass sometimes, good luck with that one.
