# from django.shortcuts import render
# from django.http import JsonResponse
# import threading
# import feedparser
# import xlsxwriter
# import pandas as pd
# import re
# import contractions
# import spacy
# from newspaper import Article
# from transformers import (
#     AutoTokenizer,
#     AutoModelForSequenceClassification,
#     TFDistilBertModel,
#     pipeline,
#     DistilBertTokenizer
# )
# import torch
# import tensorflow as tf

# # ─────── RSS CONFIG ───────
# RSS_FEEDS = {
#     'News18_Latest': 'https://www.news18.com/rss/news.xml',
#     'News18_India':  'https://www.news18.com/rss/india.xml',
#     'TheHindu':      'https://www.thehindu.com/news/national/?service=rss',
#     'TOI':           'https://timesofindia.indiatimes.com/rssfeedstopstories.cms',
# }

# # ─────── NLP SETUP ───────
# _nlp = spacy.load('en_core_web_sm')
# _stopwords = set(__import__('nltk').corpus.stopwords.words('english')) - {'not'}

# # Sentiment: CardiffNLP Twitter-RoBERTa
# sent_tok   = AutoTokenizer.from_pretrained("tokenizer_roberta/sentiment_tokenizer/")
# sent_model = AutoModelForSequenceClassification.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment/")
# _label_map = {'negative':1,'neutral':2,'positive':0}

# # Category: DistilBERT
# custom_objects = {'TFDistilBertModel': TFDistilBertModel}
# cls_model = tf.keras.models.load_model(
#     "distilbert_model.h5",
#     custom_objects=custom_objects
# )
# cls_tok  = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
# _max_len = 512
# _categories = {
#     0:"Entertainment",1:"Business",2:"Politics",3:"Judiciary",
#     4:"Crime",5:"Culture",6:"Sports",7:"Science",
#     8:"International",9:"Technology"
# }

# # Emotion: DistilBERT-based emotion classifier
# emotion_model = pipeline(
#     "sentiment-analysis",
#     model='bhadresh-savani/distilbert-base-uncased-emotion',
#     top_k=1
# )

# # ─────── HELPERS ───────
# def preprocess(text):
#     s = str(text).lower()
#     s = contractions.fix(s)
#     s = re.sub(r'[^a-z\s]', ' ', s)
#     doc = _nlp(s)
#     lemmas = [tok.lemma_ for tok in doc if tok.lemma_ != '-PRON-']
#     return ' '.join(w for w in lemmas if w not in _stopwords)

# def predict_sentiment(text):
#     inp    = sent_tok(text[:514], return_tensors='pt')
#     out    = sent_model(**inp)
#     scores = torch.softmax(out.logits[0], dim=0)
#     return [
#         scores[_label_map['positive']].item(),
#         scores[_label_map['negative']].item(),
#         scores[_label_map['neutral']].item()
#     ]

# def predict_category(text):
#     inp   = cls_tok(
#         text,
#         return_tensors='tf',
#         truncation=True,
#         padding='max_length',
#         max_length=_max_len
#     )
#     preds = cls_model.predict([inp['input_ids'], inp['attention_mask']])[0]
#     return _categories[int(preds.argmax())]

# def predict_emotion(text):
#     # returns a label like 'joy', 'sadness', etc.
#     return emotion_model(text[:1500])[0][0]['label']

# # ─────── FETCH & EXTRACT FULL TEXT ───────
# def fetch_and_process(max_items=20, output_file='RSS_FullText.xlsx'):
#     wb = xlsxwriter.Workbook(output_file)
#     ws = wb.add_worksheet()
#     ws.write_row(0, 0, [
#         'Source','Title','FullArticle','Link','Published'
#     ])
#     row = 1

#     for source, url in RSS_FEEDS.items():
#         feed  = feedparser.parse(url)
#         taken = 0
#         for entry in feed.entries:
#             if taken >= max_items:
#                 break
#             link = entry.get('link','')
#             # skip video links
#             if '/video' in link or 'video' in source.lower():
#                 continue
#             media = entry.get('media_content', [])
#             if any(m.get('type','').startswith('video/') for m in media):
#                 continue

#             # download full article
#             art = Article(link)
#             try:
#                 art.download(); art.parse()
#                 full = art.text
#             except:
#                 continue

#             ws.write_row(row, 0, [
#                 source,
#                 entry.get('title',''),
#                 full,
#                 link,
#                 entry.get('published','')
#             ])
#             row  += 1
#             taken+= 1

#     wb.close()

# # ─────── DJANGO VIEW ───────
# def index(request):
#     print("Session started")

#     # 1) Fetch full articles in background
#     t = threading.Thread(target=fetch_and_process)
#     t.start(); t.join()

#     # 2) Load into DataFrame
#     df = pd.read_excel('RSS_FullText.xlsx')

#     # 3) Preprocess & Predict
#     news = []
#     for _, r in df.iterrows():
#         raw = r['FullArticle'] or ''
#         # optionally translate first if needed:
#         # raw = translate(raw)

#         clean = preprocess(raw)
#         cat   = predict_category(clean)
#         sent  = predict_sentiment(clean)
#         emo   = predict_emotion(clean)

#         # log
#         print(f"URL: {r['Link']}")
#         print(f"Category: {cat}")
#         print(f"Sentiment: +{sent[0]:.3f}, -{sent[1]:.3f}, ~{sent[2]:.3f}")
#         print(f"Emotion: {emo}")

#         news.append({
#             'Source':      r['Source'],
#             'Title':       r['Title'],
#             'FullArticle': raw,
#             'URL':         r['Link'],
#             'Published':   r['Published'],
#             'Category':    cat,
#             'Sentiment':   sent,
#             'Emotion':     emo,
#         })

#     print("Session ended")
#     return JsonResponse(
#         {'result':'success','news':news},
#         safe=False,
#         json_dumps_params={'ensure_ascii':False}
#     )


# from django.shortcuts import render
# from django.http import JsonResponse
# import threading
# import feedparser
# import xlsxwriter
# import pandas as pd
# import re
# import contractions
# import spacy
# from newspaper import Article
# from transformers import (
#     AutoTokenizer,
#     AutoModelForSequenceClassification,
#     TFDistilBertModel,
#     pipeline,
#     DistilBertTokenizer
# )
# import torch
# import tensorflow as tf
# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart

# # ─────── RSS CONFIG ───────
# RSS_FEEDS = {
#     'News18_Latest': 'https://www.news18.com/rss/news.xml',
#     'News18_India':  'https://www.news18.com/rss/india.xml',
#     'TheHindu':      'https://www.thehindu.com/news/national/?service=rss',
#     'TOI':           'https://timesofindia.indiatimes.com/rssfeedstopstories.cms',
# }

# # ─────── GOVERNMENT DEPARTMENT MAPPING ───────
# DEPARTMENT_MAPPING = {
#     0: {  # Entertainment
#         'name': 'Ministry of Information & Broadcasting',
#         'emails': ['info@mib.gov.in']
#     },
#     1: {  # Business
#         'name': 'Ministry of Finance / DPIIT',
#         'emails': ['fm@gov.in', 'dpiit@gov.in']
#     },
#     2: {  # Politics
#         'name': "Prime Minister's Office",
#         'emails': ['connect.pmo@gov.in']
#     },
#     3: {  # Judiciary
#         'name': 'Ministry of Law & Justice',
#         'emails': ['lawmin@gov.in']
#     },
#     4: {  # Crime
#         'name': 'Ministry of Home Affairs',
#         'emails': ['jscpg-mha@gov.in', 'mha.web@gov.in']
#     },
#     5: {  # Culture
#         'name': 'Ministry of Culture',
#         'emails': ['secy-culture@gov.in']
#     },
#     6: {  # Sports
#         'name': 'Ministry of Youth Affairs and Sports',
#         'emails': ['secy-yas@gov.in']
#     },
#     7: {  # Science
#         'name': 'Department of Science & Technology (DST)',
#         'emails': ['dstinfo@gov.in']
#     },
#     8: {  # International
#         'name': 'Ministry of External Affairs (MEA)',
#         'emails': ['usfsp.mea@gov.in']
#     },
#     9: {  # Technology
#         'name': 'Ministry of Electronics and IT (MeitY)',
#         'emails': ['contact@meity.gov.in']
#     }
# }

# # ─────── EMAIL CONFIG ───────
# EMAIL_CONFIG = {
#     'sender_email': 'lakshsharma16052004',  # Replace with your email
#     'sender_password': 'bhsq enex bzah rouw',        # Replace with your password
#     'smtp_server': 'smtp.gmail.com',          # Change if using different provider
#     'smtp_port': 587
# }

# # ─────── NLP SETUP ───────
# _nlp = spacy.load('en_core_web_sm')
# stopwords = set(__import__('nltk').corpus.stopwords.words('english')) - {'not'}

# # Sentiment: CardiffNLP Twitter-RoBERTa
# sent_tok = AutoTokenizer.from_pretrained("tokenizer_roberta/sentiment_tokenizer/")
# sent_model = AutoModelForSequenceClassification.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment/")
# _label_map = {'negative':1,'neutral':2,'positive':0}

# # Category: DistilBERT
# custom_objects = {'TFDistilBertModel': TFDistilBertModel}
# cls_model = tf.keras.models.load_model(
#     "distilbert_model.h5",
#     custom_objects=custom_objects
# )
# cls_tok = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
# _max_len = 512
# _categories = {
#     0:"Entertainment",1:"Business",2:"Politics",3:"Judiciary",
#     4:"Crime",5:"Culture",6:"Sports",7:"Science",
#     8:"International",9:"Technology"
# }

# # Emotion: DistilBERT-based emotion classifier
# emotion_model = pipeline(
#     "sentiment-analysis",
#     model='bhadresh-savani/distilbert-base-uncased-emotion',
#     top_k=1
# )

# # ─────── HELPERS ───────
# def preprocess(text):
#     s = str(text).lower()
#     s = contractions.fix(s)
#     s = re.sub(r'[^a-z\s]', ' ', s)
#     doc = _nlp(s)
#     lemmas = [tok.lemma_ for tok in doc if tok.lemma_ != '-PRON-']
#     return ' '.join(w for w in lemmas if w not in stopwords)

# def predict_sentiment(text):
#     inp = sent_tok(text[:514], return_tensors='pt')
#     out = sent_model(**inp)
#     scores = torch.softmax(out.logits[0], dim=0)
#     return [
#         scores[_label_map['positive']].item(),
#         scores[_label_map['negative']].item(),
#         scores[_label_map['neutral']].item()
#     ]

# def predict_category(text):
#     inp = cls_tok(
#         text,
#         return_tensors='tf',
#         truncation=True,
#         padding='max_length',
#         max_length=_max_len
#     )
#     preds = cls_model.predict([inp['input_ids'], inp['attention_mask']])[0]
#     return int(preds.argmax())

# def predict_emotion(text):
#     return emotion_model(text[:1500])[0][0]['label']

# def send_email(to_emails, subject, body):
#     """Send email to concerned department about negative news"""
#     try:
#         msg = MIMEMultipart()
#         msg['From'] = EMAIL_CONFIG['sender_email']
#         msg['To'] = ", ".join(to_emails)
#         msg['Subject'] = subject
        
#         msg.attach(MIMEText(body, 'plain'))
        
#         server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
#         server.starttls()
#         server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['sender_password'])
#         server.sendmail(EMAIL_CONFIG['sender_email'], to_emails, msg.as_string())
#         server.quit()
#         return True
#     except Exception as e:
#         print(f"Error sending email: {e}")
#         return False

# # ─────── FETCH & EXTRACT FULL TEXT ───────
# def fetch_and_process(max_items=20, output_file='RSS_FullText.xlsx'):
#     wb = xlsxwriter.Workbook(output_file)
#     ws = wb.add_worksheet()
#     ws.write_row(0, 0, [
#         'Source','Title','FullArticle','Link','Published'
#     ])
#     row = 1

#     for source, url in RSS_FEEDS.items():
#         feed = feedparser.parse(url)
#         taken = 0
#         for entry in feed.entries:
#             if taken >= max_items:
#                 break
#             link = entry.get('link','')
#             # skip video links
#             if '/video' in link or 'video' in source.lower():
#                 continue
#             media = entry.get('media_content', [])
#             if any(m.get('type','').startswith('video/') for m in media):
#                 continue

#             # download full article
#             art = Article(link)
#             try:
#                 art.download()
#                 art.parse()
#                 full = art.text
#             except:
#                 continue

#             ws.write_row(row, 0, [
#                 source,
#                 entry.get('title',''),
#                 full,
#                 link,
#                 entry.get('published','')
#             ])
#             row += 1
#             taken += 1

#     wb.close()

# # ─────── DJANGO VIEW ───────
# def index(request):
#     print("Session started")

#     # 1) Fetch full articles in background
#     t = threading.Thread(target=fetch_and_process)
#     t.start()
#     t.join()

#     # 2) Load into DataFrame
#     df = pd.read_excel('RSS_FullText.xlsx')

#     # 3) Preprocess & Predict
#     news = []
#     negative_news = []  # Store negative news for reporting
    
#     for _, r in df.iterrows():
#         raw = r['FullArticle'] or ''
#         clean = preprocess(raw)
#         cat_id = predict_category(clean)
#         cat_name = _categories[cat_id]
#         sent = predict_sentiment(clean)
#         emo = predict_emotion(clean)

#         # Check if negative sentiment is greater than 70%
#         if sent[1] > 0.8:
#             negative_news.append({
#                 'title': r['Title'],
#                 'url': r['Link'],
#                 'category': cat_name,
#                 'sentiment': sent,
#                 'published': r['Published'],
#                 'source': r['Source'],
#                 'description': raw[:1000] + '...' if len(raw) > 1000 else raw
#             })

#         news.append({
#             'Source': r['Source'],
#             'Title': r['Title'],
#             'FullArticle': raw,
#             'URL': r['Link'],
#             'Published': r['Published'],
#             'Category': cat_name,
#             'Sentiment': sent,
#             'Emotion': emo,
#         })

#     # Send alerts for negative news
#     for item in negative_news:
#         department = DEPARTMENT_MAPPING.get(predict_category(preprocess(item['description'])))
        
#         if department:
#             email_body = (
#                 f"A negative news article was detected.\n\n"
#                 f"Title: {item['title']}\n"
#                 f"URL: {item['url']}\n"
#                 f"Category: {item['category']}\n"
#                 f"Sentiment Score: Positive={item['sentiment'][0]:.2f}, "
#                 f"Negative={item['sentiment'][1]:.2f}, "
#                 f"Neutral={item['sentiment'][2]:.2f}\n"
#                 f"Published: {item['published']}\n"
#                 f"Source: {item['source']}\n\n"
#                 f"Article Description:\n{item['description']}\n\n"
#                 f"Please review this article for potential action."
#             )
            
#             subject = f"Negative News Alert: {item['category']} - {item['title'][:50]}..."
            
#             # Send email to concerned department
#             success = send_email(
#                 department['emails'],
#                 subject,
#                 email_body
#             )
            
#             if success:
#                 print(f"Alert sent to {department['name']} about: {item['url']}")
#             else:
#                 print(f"Failed to send alert about: {item['url']}")

#     print("Session ended")
#     return JsonResponse(
#         {'result':'success','news':news},
#         safe=False,
#         json_dumps_params={'ensure_ascii':False}
#     )

from django.shortcuts import render
from django.http import JsonResponse
import threading
import feedparser
import xlsxwriter
import pandas as pd
import re
import contractions
import spacy
from newspaper import Article
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TFDistilBertModel,
    pipeline,
    DistilBertTokenizer
)
import torch
import tensorflow as tf
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ─────── RSS CONFIG ───────
RSS_FEEDS = {
    'News18_Latest': 'https://www.news18.com/rss/news.xml',
    'News18_India':  'https://www.news18.com/rss/india.xml',
    'TheHindu':      'https://www.thehindu.com/news/national/?service=rss',
    'TOI':           'https://timesofindia.indiatimes.com/rssfeedstopstories.cms',
}

# ─────── GOVERNMENT DEPARTMENT MAPPING ───────
DEPARTMENT_MAPPING = {
    0: {  # Entertainment
        'name': 'Ministry of Information & Broadcasting',
        'emails': ['info@mib.gov.in']
    },
    1: {  # Business
        'name': 'Ministry of Finance / DPIIT',
        'emails': ['fm@gov.in', 'dpiit@gov.in']
    },
    2: {  # Politics
        'name': "Prime Minister's Office",
        'emails': ['connect.pmo@gov.in']
    },
    3: {  # Judiciary
        'name': 'Ministry of Law & Justice',
        'emails': ['lawmin@gov.in']
    },
    4: {  # Crime
        'name': 'Ministry of Home Affairs',
        'emails': ['jscpg-mha@gov.in', 'mha.web@gov.in']
    },
    5: {  # Culture
        'name': 'Ministry of Culture',
        'emails': ['secy-culture@gov.in']
    },
    6: {  # Sports
        'name': 'Ministry of Youth Affairs and Sports',
        'emails': ['secy-yas@gov.in']
    },
    7: {  # Science
        'name': 'Department of Science & Technology (DST)',
        'emails': ['dstinfo@gov.in']
    },
    8: {  # International
        'name': 'Ministry of External Affairs (MEA)',
        'emails': ['usfsp.mea@gov.in']
    },
    9: {  # Technology
        'name': 'Ministry of Electronics and IT (MeitY)',
        'emails': ['contact@meity.gov.in']
    }
}

# ─────── EMAIL CONFIG ───────
EMAIL_CONFIG = {
    'sender_email': 'lakshsharma16052004',  # Replace with your email
    'sender_password': 'bhsq enex bzah rouw',        # Replace with your password
    'smtp_server': 'smtp.gmail.com',          # Change if using different provider
    'smtp_port': 587
}

# ─────── NLP SETUP ───────
_nlp = spacy.load('en_core_web_sm')
stopwords = set(__import__('nltk').corpus.stopwords.words('english')) - {'not'}

# Sentiment: CardiffNLP Twitter-RoBERTa
sent_tok = AutoTokenizer.from_pretrained("tokenizer_roberta/sentiment_tokenizer/")
sent_model = AutoModelForSequenceClassification.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment/")
_label_map = {'negative':1,'neutral':2,'positive':0}

# Category: DistilBERT
custom_objects = {'TFDistilBertModel': TFDistilBertModel}
cls_model = tf.keras.models.load_model(
    "distilbert_model.h5",
    custom_objects=custom_objects
)
cls_tok = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
_max_len = 512
_categories = {
    0:"Entertainment",1:"Business",2:"Politics",3:"Judiciary",
    4:"Crime",5:"Culture",6:"Sports",7:"Science",
    8:"International",9:"Technology"
}

# Emotion: DistilBERT-based emotion classifier
emotion_model = pipeline(
    "sentiment-analysis",
    model='bhadresh-savani/distilbert-base-uncased-emotion',
    top_k=1
)

# ─────── HELPERS ───────
def preprocess(text):
    s = str(text).lower()
    s = contractions.fix(s)
    s = re.sub(r'[^a-z\s]', ' ', s)
    doc = _nlp(s)
    lemmas = [tok.lemma_ for tok in doc if tok.lemma_ != '-PRON-']
    return ' '.join(w for w in lemmas if w not in stopwords)

def predict_sentiment(text):
    inp = sent_tok(text[:514], return_tensors='pt')
    out = sent_model(**inp)
    scores = torch.softmax(out.logits[0], dim=0)
    return [
        scores[_label_map['positive']].item(),
        scores[_label_map['negative']].item(),
        scores[_label_map['neutral']].item()
    ]

def predict_category(text):
    inp = cls_tok(
        text,
        return_tensors='tf',
        truncation=True,
        padding='max_length',
        max_length=_max_len
    )
    preds = cls_model.predict([inp['input_ids'], inp['attention_mask']])[0]
    return int(preds.argmax())

def predict_emotion(text):
    return emotion_model(text[:1500])[0][0]['label']

def send_email(to_emails, subject, body):
    """Send email to concerned department about negative news"""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG['sender_email']
        msg['To'] = ", ".join(to_emails)
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
        server.starttls()
        server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['sender_password'])
        server.sendmail(EMAIL_CONFIG['sender_email'], to_emails, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

# ─────── FETCH & EXTRACT FULL TEXT ───────
def fetch_and_process(max_items=20, output_file='RSS_FullText.xlsx'):
    wb = xlsxwriter.Workbook(output_file)
    ws = wb.add_worksheet()
    ws.write_row(0, 0, [
        'Source','Title','FullArticle','Link','Published'
    ])
    row = 1

    for source, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        taken = 0
        for entry in feed.entries:
            if taken >= max_items:
                break
            link = entry.get('link','')
            # skip video links
            if '/video' in link or 'video' in source.lower():
                continue
            media = entry.get('media_content', [])
            if any(m.get('type','').startswith('video/') for m in media):
                continue

            # download full article
            art = Article(link)
            try:
                art.download()
                art.parse()
                full = art.text
            except:
                continue

            ws.write_row(row, 0, [
                source,
                entry.get('title',''),
                full,
                link,
                entry.get('published','')
            ])
            row += 1
            taken += 1

    wb.close()

# ─────── DJANGO VIEW ───────
def index(request):
    print("Session started")

    # 1) Fetch full articles in background
    t = threading.Thread(target=fetch_and_process)
    t.start()
    t.join()

    # 2) Load into DataFrame
    df = pd.read_excel('RSS_FullText.xlsx')

    # 3) Preprocess & Predict
    news = []
    negative_news = []  # Store negative news for reporting

    # Prepare for Excel output
    output_rows = []

    for _, r in df.iterrows():
        raw = r['FullArticle'] or ''
        clean = preprocess(raw)
        cat_id = predict_category(clean)
        cat_name = _categories[cat_id]
        sent = predict_sentiment(clean)
        emo = predict_emotion(clean)
        dept = DEPARTMENT_MAPPING.get(cat_id, {}).get('name', '')

        # Check if negative sentiment is greater than 80%
        if sent[1] > 0.95:
            negative_news.append({
                'title': r['Title'],
                'url': r['Link'],
                'category': cat_name,
                'sentiment': sent,
                'published': r['Published'],
                'source': r['Source'],
                'description': raw[:1000] + '...' if len(raw) > 1000 else raw
            })

        news.append({
            'Source': r['Source'],
            'Title': r['Title'],
            'FullArticle': raw,
            'URL': r['Link'],
            'Published': r['Published'],
            'Category': cat_name,
            'Sentiment': sent,
            'Emotion': emo,
            'Department': dept,
        })

        # Prepare row for Excel
        output_rows.append([
            r['Source'],
            r['Title'],
            raw,
            r['Link'],
            r['Published'],
            f"Positive={sent[0]:.2f}, Negative={sent[1]:.2f}, Neutral={sent[2]:.2f}",
            cat_name,
            emo,
            dept
        ])

    # Write to Excel with all columns
    output_file = 'RSS_Processed.xlsx'
    wb = xlsxwriter.Workbook(output_file)
    ws = wb.add_worksheet()
    ws.write_row(0, 0, [
        'Source', 'Title', 'FullArticle', 'Link', 'Published', 'Sentiment', 'Category', 'Emotion', 'Department'
    ])
    for idx, row in enumerate(output_rows, 1):
        ws.write_row(idx, 0, row)
    wb.close()

    # Send alerts for negative news
    for item in negative_news:
        department = DEPARTMENT_MAPPING.get(predict_category(preprocess(item['description'])))
        
        if department:
            email_body = (
                f"A negative news article was detected.\n\n"
                f"Title: {item['title']}\n"
                f"URL: {item['url']}\n"
                f"Category: {item['category']}\n"
                f"Sentiment Score: Positive={item['sentiment'][0]:.2f}, "
                f"Negative={item['sentiment'][1]:.2f}, "
                f"Neutral={item['sentiment'][2]:.2f}\n"
                f"Published: {item['published']}\n"
                f"Source: {item['source']}\n\n"
                f"Article Description:\n{item['description']}\n\n"
                f"Please review this article for potential action."
            )
            
            subject = f"Negative News Alert: {item['category']} - {item['title'][:50]}..."
            
            # Send email to concerned department
            success = send_email(
                department['emails'],
                subject,
                email_body
            )
            
            if success:
                print(f"Alert sent to {department['name']} about: {item['url']}")
            else:
                print(f"Failed to send alert about: {item['url']}")

    print("Session ended")
    return JsonResponse(
        {'result':'success','news':news},
        safe=False,
        json_dumps_params={'ensure_ascii':False}
    )