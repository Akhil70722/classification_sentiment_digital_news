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
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.utils.decorators import method_decorator
import threading
import feedparser
import xlsxwriter
import pandas as pd
import re
import os
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
from deep_translator import GoogleTranslator

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
    'sender_email': 'putyourmail@gmail.com',  # Replace with your email
    'sender_password': 'bhsq enex bzah rouw',        # Replace with your password
    'smtp_server': 'smtp.gmail.com',          # Change if using different provider
    'smtp_port': 587
}

# ─────── NLP SETUP ───────
_nlp = spacy.load('en_core_web_sm')
stopwords = set(__import__('nltk').corpus.stopwords.words('english')) - {'not'}

# Sentiment: CardiffNLP Twitter-RoBERTa
sent_tok = AutoTokenizer.from_pretrained("tokenizer_roberta/sentiment_tokenizer/")
# Load model from Hugging Face Hub (will download and cache automatically)
try:
    sent_model = AutoModelForSequenceClassification.from_pretrained(
        "cardiffnlp/twitter-roberta-base-sentiment"
    )
except Exception as e:
    print(f"Error loading sentiment model: {e}")
    print("Attempting to download from Hugging Face Hub...")
    # Force download by clearing any incomplete cache
    import shutil
    cache_dir = os.path.expanduser("~/.cache/huggingface/hub")
    if os.path.exists(cache_dir):
        model_cache_path = None
        # Try to find the model in cache and remove if incomplete
        for root, dirs, files in os.walk(cache_dir):
            if "twitter-roberta-base-sentiment" in root:
                model_files = ['pytorch_model.bin', 'model.safetensors']
                has_model = any(f in files for f in model_files)
                if not has_model:
                    model_cache_path = root
                    break
        if model_cache_path:
            try:
                shutil.rmtree(model_cache_path)
                print(f"Removed incomplete cache: {model_cache_path}")
            except:
                pass
    # Retry loading
    sent_model = AutoModelForSequenceClassification.from_pretrained(
        "cardiffnlp/twitter-roberta-base-sentiment",
        force_download=False
    )
_label_map = {'negative':1,'neutral':2,'positive':0}

# Category: DistilBERT
cls_model = None
cls_tok = None
_max_len = 512
_categories = {
    0:"Entertainment",1:"Business",2:"Politics",3:"Judiciary",
    4:"Crime",5:"Culture",6:"Sports",7:"Science",
    8:"International",9:"Technology"
}

# Lazy load category model if file exists
def _load_category_model():
    global cls_model, cls_tok
    if cls_model is None and os.path.exists("distilbert_model.h5"):
        try:
            custom_objects = {'TFDistilBertModel': TFDistilBertModel}
            cls_model = tf.keras.models.load_model(
                "distilbert_model.h5",
                custom_objects=custom_objects
            )
            cls_tok = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
        except Exception as e:
            print(f"Warning: Could not load category model: {e}")
            cls_model = False  # Mark as failed
            cls_tok = False

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
    _load_category_model()
    if cls_model is None or cls_model is False or cls_tok is None or cls_tok is False:
        # Fallback: return a default category ID if model not available
        return 0  # Default to first category (Entertainment)
    try:
        inp = cls_tok(
            text,
            return_tensors='tf',
            truncation=True,
            padding='max_length',
            max_length=_max_len
        )
        preds = cls_model.predict([inp['input_ids'], inp['attention_mask']])[0]
        return int(preds.argmax())
    except Exception as e:
        print(f"Error predicting category: {e}")
        return 0  # Default to first category

def predict_emotion(text):
    return emotion_model(text[:1500])[0][0]['label']

# Global translator instance to reuse (faster)
_translator_instance = None

def get_translator(source='en', target='hi'):
    """Get or create translator instance"""
    global _translator_instance
    if _translator_instance is None:
        _translator_instance = GoogleTranslator(source=source, target=target)
    return _translator_instance

def translate_text(text, target_lang='hi', max_length=300):
    """Translate text to target language using Google Translator - optimized version"""
    try:
        if not text or len(text.strip()) == 0:
            return ''
        
        # Limit text length for faster translation (only translate what's needed)
        text_to_translate = text[:max_length] if len(text) > max_length else text
        
        if target_lang == 'hi':
            translator = get_translator(source='en', target='hi')
            translated = translator.translate(text_to_translate)
            if translated and translated.strip():
                print(f"Translated: '{text_to_translate[:30]}...' -> '{translated[:30]}...'")
                return translated
            else:
                print(f"Translation returned empty for: '{text_to_translate[:30]}...'")
                return ''
        else:
            # If target is English, return original (news is already in English)
            return text
    except Exception as e:
        print(f"Translation error for text '{text[:50]}...': {e}")
        import traceback
        traceback.print_exc()
        return ''  # Return empty on error so frontend falls back to English

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
        'Source','Title','FullArticle','Link','Published','ImageURL'
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
            image_url = ''
            try:
                art.download()
                art.parse()
                full = art.text
                # Extract image from article
                image_url = art.top_image or ''
            except:
                full = ''
            
            # Try to get image from RSS feed media content if article extraction failed
            if not image_url:
                media_content = entry.get('media_content', [])
                if media_content:
                    for media in media_content:
                        if media.get('type', '').startswith('image/'):
                            image_url = media.get('url', '')
                            break
                # Also check media_thumbnail
                if not image_url and 'media_thumbnail' in entry:
                    image_url = entry.get('media_thumbnail', [{}])[0].get('url', '') if isinstance(entry.get('media_thumbnail'), list) else entry.get('media_thumbnail', '')

            ws.write_row(row, 0, [
                source,
                entry.get('title',''),
                full,
                link,
                entry.get('published',''),
                image_url  # Include image URL in Excel
            ])
            row += 1
            taken += 1

    wb.close()

# ─────── HELPER FUNCTION FOR PROCESSING NEWS ───────
def _process_news_data(language='en'):
    """
    Helper function to process RSS feeds and analyze news articles.
    Returns processed news list and negative news list.
    """
    print(f"Processing news data for language: {language}")
    
    # 1) Fetch full articles in background
    t = threading.Thread(target=fetch_and_process)
    t.start()
    t.join()

    # 2) Load into DataFrame
    df = pd.read_excel('RSS_FullText.xlsx')

    # Reset translator instance for new request (to avoid issues)
    global _translator_instance
    if language == 'hi':
        _translator_instance = None  # Reset to create fresh instance
        print(f"Starting translation to Hindi for {len(df)} items (this may take 30-60 seconds)...")

    # 3) Preprocess & Predict
    news = []
    negative_news = []  # Store negative news for reporting
    output_rows = []

    for idx, r in df.iterrows():
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

        # Try to extract image from article if not already in Excel
        image_url = ''
        try:
            if 'ImageURL' in r and pd.notna(r['ImageURL']):
                image_url = str(r['ImageURL'])
            if not image_url or image_url == 'nan':
                art = Article(r['Link'])
                art.download()
                art.parse()
                image_url = art.top_image or ''
        except:
            image_url = ''
        
        # Prepare news item
        news_item = {
            'Source': r['Source'],
            'Title': r['Title'],
            'FullArticle': raw,
            'URL': r['Link'],
            'Published': r['Published'],
            'Category': cat_name,
            'Sentiment': sent,
            'Emotion': emo,
            'Department': dept,
            'ImageURL': image_url,
        }
        
        # Translate if Hindi is requested
        if language == 'hi':
            try:
                translated_title = translate_text(str(r['Title']), 'hi', max_length=200)
                news_item['TitleHindi'] = translated_title if translated_title and translated_title.strip() else ''
                
                description = str(raw)[:200] + '...' if len(str(raw)) > 200 else str(raw)
                translated_desc = translate_text(description, 'hi', max_length=200)
                news_item['DescriptionHindi'] = translated_desc if translated_desc and translated_desc.strip() else ''
                news_item['FullArticleHindi'] = ''
                
                if (idx + 1) % 10 == 0:
                    print(f"Translated {idx + 1}/{len(df)} items...")
            except Exception as e:
                print(f"Error translating news item {r['Title'][:50]}: {e}")
                news_item['TitleHindi'] = ''
                news_item['DescriptionHindi'] = ''
                news_item['FullArticleHindi'] = ''
        else:
            news_item['TitleHindi'] = ''
            news_item['DescriptionHindi'] = ''
            news_item['FullArticleHindi'] = ''
        
        news.append(news_item)

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
            
            success = send_email(
                department['emails'],
                subject,
                email_body
            )
            
            if success:
                print(f"Alert sent to {department['name']} about: {item['url']}")
            else:
                print(f"Failed to send alert about: {item['url']}")

    print(f"Total news items processed: {len(news)}")
    if language == 'hi':
        print(f"Translation completed for {len(news)} items")
    
    return news, negative_news

# ─────── API VIEW CLASSES ───────

class CsrfExemptMixin:
    """Mixin to exempt CSRF verification for API endpoints"""
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class HealthCheckView(CsrfExemptMixin, View):
    """Health check endpoint - returns API status"""
    
    def get(self, request):
        """Handle GET request for health check"""
        return JsonResponse({
            'status': 'healthy',
            'service': 'News Intelligence & Alert System',
            'timestamp': pd.Timestamp.now().isoformat()
        })


class CategoriesView(CsrfExemptMixin, View):
    """Get list of all available news categories"""
    
    def get(self, request):
        """Handle GET request to retrieve categories"""
        categories = [
            {'id': 0, 'name': 'Entertainment', 'frontend_name': 'Information and Broadcasting'},
            {'id': 1, 'name': 'Business', 'frontend_name': 'Finance'},
            {'id': 2, 'name': 'Politics', 'frontend_name': 'Politics'},
            {'id': 3, 'name': 'Judiciary', 'frontend_name': 'Law and Justice'},
            {'id': 4, 'name': 'Crime', 'frontend_name': 'Internal Security'},
            {'id': 5, 'name': 'Culture', 'frontend_name': 'Culture'},
            {'id': 6, 'name': 'Sports', 'frontend_name': 'Youth Affairs and Sports'},
            {'id': 7, 'name': 'Science', 'frontend_name': 'Science and Technology'},
            {'id': 8, 'name': 'International', 'frontend_name': 'External Affairs'},
            {'id': 9, 'name': 'Technology', 'frontend_name': 'Electronics and Information Technology'},
        ]
        
        return JsonResponse({
            'result': 'success',
            'categories': categories,
            'total': len(categories)
        })


class NewsListView(CsrfExemptMixin, View):
    """GET endpoint to fetch all news articles"""
    
    def get(self, request):
        """Handle GET request to retrieve all news"""
        print("GET /api/news/ - Fetching all news")
        
        # Get language parameter from query string
        language = request.GET.get('language', 'en')
        
        try:
            news, negative_news = _process_news_data(language)
            
            if len(news) == 0:
                return JsonResponse(
                    {'result': 'success', 'news': [], 'message': 'No news items available', 'total': 0},
                    safe=False,
                    json_dumps_params={'ensure_ascii': False}
                )
            
            return JsonResponse(
                {'result': 'success', 'news': news, 'total': len(news)},
                safe=False,
                json_dumps_params={'ensure_ascii': False}
            )
        except Exception as e:
            print(f"Error in NewsListView: {e}")
            import traceback
            traceback.print_exc()
            return JsonResponse(
                {'result': 'error', 'message': str(e), 'news': []},
                safe=False,
                status=500
            )


class NewsFilterView(CsrfExemptMixin, View):
    """POST endpoint to filter news by category"""
    
    def post(self, request):
        """Handle POST request to filter news by category"""
        print("POST /api/news/filter/ - Filtering news by category")
        
        try:
            import json
            
            # Parse request body
            if not request.body:
                return JsonResponse(
                    {'result': 'error', 'message': 'Request body is empty'},
                    status=400
                )
            
            body_str = request.body.decode('utf-8')
            if not body_str.strip():
                return JsonResponse(
                    {'result': 'error', 'message': 'Request body is empty'},
                    status=400
                )
            
            data = json.loads(body_str)
            category_filter = data.get('category', None)
            language = data.get('language', 'en')
            
            print(f"Category filter: {category_filter}, Language: {language}")
            
            # Process news data
            news, negative_news = _process_news_data(language)
            
            if len(news) == 0:
                return JsonResponse(
                    {'result': 'success', 'news': [], 'message': 'No news items available', 'total': 0, 'filtered': 0},
                    safe=False,
                    json_dumps_params={'ensure_ascii': False}
                )
            
            # Filter by category if provided
            if category_filter:
                filtered_news = self._filter_by_category(news, category_filter)
                
                print(f"Filtered news items: {len(filtered_news)}")
                
                return JsonResponse(
                    {'result': 'success', 'news': filtered_news, 'total': len(news), 'filtered': len(filtered_news)},
                    safe=False,
                    json_dumps_params={'ensure_ascii': False}
                )
            else:
                # No category filter, return all news
                return JsonResponse(
                    {'result': 'success', 'news': news, 'total': len(news)},
                    safe=False,
                    json_dumps_params={'ensure_ascii': False}
                )
                
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return JsonResponse(
                {'result': 'error', 'message': f'Invalid JSON: {str(e)}', 'news': []},
                status=400
            )
        except Exception as e:
            print(f"Error in NewsFilterView: {e}")
            import traceback
            traceback.print_exc()
            return JsonResponse(
                {'result': 'error', 'message': str(e), 'news': []},
                status=500
            )
    
    def _filter_by_category(self, news, category_filter):
        """Helper method to filter news by category"""
        # Map frontend category names to backend category names
        category_mapping = {
            'External Affairs': 'International',
            'Law and Justice': 'Judiciary',
            'Youth Affairs and Sports': 'Sports',
            'Finance': 'Business',
            'Internal Security': 'Crime',
            'Culture': 'Culture',
            'Information and Broadcasting': 'Entertainment',
            'Home Affairs': 'Crime',
            'Science and Technology': 'Science',
            'Electronics and Information Technology': 'Technology'
        }
        
        backend_category = category_mapping.get(category_filter, category_filter)
        print(f"Mapped category: {backend_category}")
        
        # Filter news by category (case-insensitive)
        filtered_news = [
            item for item in news 
            if item.get('Category') and 
            str(item.get('Category')).strip().lower() == str(backend_category).strip().lower()
        ]
        
        # Try partial matching if no exact match
        if len(filtered_news) == 0:
            filtered_news = [
                item for item in news 
                if item.get('Category') and 
                str(backend_category).strip().lower() in str(item.get('Category')).strip().lower()
            ]
        
        return filtered_news

# ─────── LEGACY ENDPOINT (for backward compatibility) ───────
@csrf_exempt
def index(request):
    """Legacy endpoint for backward compatibility - kept as function-based view"""
    print("Session started")
    
    # Get language parameter from request
    language = request.GET.get('language', 'en')
    if request.method == 'POST':
        try:
            import json
            if request.body:
                body_str = request.body.decode('utf-8')
                if body_str.strip():
                    data = json.loads(body_str)
                    language = data.get('language', language)
        except:
            pass
    
    print(f"Requested language: {language}")

    # 1) Fetch full articles in background
    t = threading.Thread(target=fetch_and_process)
    t.start()
    t.join()

    # 2) Load into DataFrame
    df = pd.read_excel('RSS_FullText.xlsx')

    # Reset translator instance for new request (to avoid issues)
    global _translator_instance
    if language == 'hi':
        _translator_instance = None  # Reset to create fresh instance
        print(f"Starting translation to Hindi for {len(df)} items (this may take 30-60 seconds)...")

    # 3) Preprocess & Predict
    news = []
    negative_news = []  # Store negative news for reporting

    # Prepare for Excel output
    output_rows = []

    for idx, r in df.iterrows():
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

        # Try to extract image from article if not already in Excel
        image_url = ''
        try:
            # Try to get image from RSS feed media content first
            if 'ImageURL' in r and pd.notna(r['ImageURL']):
                image_url = str(r['ImageURL'])
            # If no image in Excel, try to extract from article URL
            if not image_url or image_url == 'nan':
                art = Article(r['Link'])
                art.download()
                art.parse()
                image_url = art.top_image or ''
        except:
            image_url = ''
        
        # Prepare news item
        news_item = {
            'Source': r['Source'],
            'Title': r['Title'],
            'FullArticle': raw,
            'URL': r['Link'],
            'Published': r['Published'],
            'Category': cat_name,
            'Sentiment': sent,
            'Emotion': emo,
            'Department': dept,
            'ImageURL': image_url,  # Add actual article image URL
        }
        
        # Translate if Hindi is requested (only translate what's displayed in UI)
        if language == 'hi':
            try:
                # Only translate title and short description for performance
                # Skip full article translation since it's not shown in cards
                translated_title = translate_text(str(r['Title']), 'hi', max_length=200)
                news_item['TitleHindi'] = translated_title if translated_title and translated_title.strip() else ''
                
                # Translate only first 200 chars for description (what's shown in card)
                description = str(raw)[:200] + '...' if len(str(raw)) > 200 else str(raw)
                translated_desc = translate_text(description, 'hi', max_length=200)
                news_item['DescriptionHindi'] = translated_desc if translated_desc and translated_desc.strip() else ''
                
                # Don't translate full article - too slow and not needed
                news_item['FullArticleHindi'] = ''  # Empty since we don't need it
                
                # Show progress every 10 items
                if (idx + 1) % 10 == 0:
                    print(f"Translated {idx + 1}/{len(df)} items...")
                    print(f"Sample translation - Title: {translated_title[:50]}...")
            except Exception as e:
                print(f"Error translating news item {r['Title'][:50]}: {e}")
                import traceback
                traceback.print_exc()
                # If translation fails, don't set Hindi fields (will fall back to English)
                # Don't set them to English text, leave empty or unset
                news_item['TitleHindi'] = ''
                news_item['DescriptionHindi'] = ''
                news_item['FullArticleHindi'] = ''
        else:
            # For English, ensure Hindi fields are not present (or empty)
            news_item['TitleHindi'] = ''
            news_item['DescriptionHindi'] = ''
            news_item['FullArticleHindi'] = ''
        
        news.append(news_item)

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

    print(f"Total news items processed: {len(news)}")
    if language == 'hi':
        print(f"Translation completed for {len(news)} items")
    
    # If no news was processed, return early with empty list
    if len(news) == 0:
        print("WARNING: No news items were processed!")
        return JsonResponse(
            {'result':'success','news':[], 'message':'No news items available'},
            safe=False,
            json_dumps_params={'ensure_ascii':False}
        )
    
    # Handle POST request for category filtering BEFORE returning
    if request.method == 'POST':
        try:
            import json
            # Decode request body for Python 3
            if not request.body:
                print("POST request body is empty, returning all news")
                return JsonResponse(
                    {'result':'success','news':news},
                    safe=False,
                    json_dumps_params={'ensure_ascii':False}
                )
            
            body_str = request.body.decode('utf-8')
            print(f"POST request body: {body_str}")
            
            if not body_str.strip():
                print("POST request body is empty after decode, returning all news")
                return JsonResponse(
                    {'result':'success','news':news},
                    safe=False,
                    json_dumps_params={'ensure_ascii':False}
                )
            
            data = json.loads(body_str)
            category_filter = data.get('category', None)
            request_language = data.get('language', 'en')
            if request_language:
                language = request_language
            print(f"Category filter received: {category_filter}")
            print(f"Language from POST: {request_language}")
            
            if category_filter:
                # Map frontend category names to backend category names
                category_mapping = {
                    'External Affairs': 'International',
                    'Law and Justice': 'Judiciary',
                    'Youth Affairs and Sports': 'Sports',
                    'Finance': 'Business',
                    'Internal Security': 'Crime',
                    'Culture': 'Culture',
                    'Information and Broadcasting': 'Entertainment',
                    'Home Affairs': 'Crime',
                    'Science and Technology': 'Science',
                    'Electronics and Information Technology': 'Technology'
                }
                
                backend_category = category_mapping.get(category_filter, category_filter)
                print(f"Mapped category: {backend_category}")
                print(f"Total news items: {len(news)}")
                
                # Get unique categories from news for debugging
                unique_categories = list(set([item.get('Category') for item in news]))
                print(f"Available categories in news: {unique_categories}")
                
                # Filter news by category (case-insensitive comparison)
                filtered_news = [
                    item for item in news 
                    if item.get('Category') and 
                    str(item.get('Category')).strip().lower() == str(backend_category).strip().lower()
                ]
                print(f"Filtered news items: {len(filtered_news)}")
                
                # If no matches found, try partial matching
                if len(filtered_news) == 0:
                    print(f"Trying partial match for category: {backend_category}")
                    filtered_news = [
                        item for item in news 
                        if item.get('Category') and 
                        str(backend_category).strip().lower() in str(item.get('Category')).strip().lower()
                    ]
                    print(f"Partial match results: {len(filtered_news)}")
                
                # If still no matches, try reverse partial matching
                if len(filtered_news) == 0:
                    print(f"Trying reverse partial match for category: {backend_category}")
                    filtered_news = [
                        item for item in news 
                        if item.get('Category') and 
                        str(item.get('Category')).strip().lower() in str(backend_category).strip().lower()
                    ]
                    print(f"Reverse partial match results: {len(filtered_news)}")
                
                print(f"Final filtered news count: {len(filtered_news)}")
                if len(filtered_news) > 0:
                    print(f"Sample filtered item category: {filtered_news[0].get('Category')}")
                
                return JsonResponse(
                    {'result':'success','news':filtered_news, 'total':len(news), 'filtered':len(filtered_news)},
                    safe=False,
                    json_dumps_params={'ensure_ascii':False}
                )
            else:
                print("No category filter provided in POST request, returning all news")
                return JsonResponse(
                    {'result':'success','news':news, 'total':len(news)},
                    safe=False,
                    json_dumps_params={'ensure_ascii':False}
                )
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print(f"Request body (raw): {request.body}")
            import traceback
            traceback.print_exc()
            return JsonResponse(
                {'result':'error','message':f'Invalid JSON: {str(e)}', 'news':[]},
                safe=False
            )
        except Exception as e:
            print(f"ERROR filtering by category: {e}")
            import traceback
            traceback.print_exc()
            # Return all news as fallback on error
            return JsonResponse(
                {'result':'error','message':str(e), 'news':news, 'total':len(news)},
                safe=False,
                json_dumps_params={'ensure_ascii':False}
            )
    
    # Default GET request returns all news
    print(f"GET request: Returning all {len(news)} news items")
    return JsonResponse(
        {'result':'success','news':news, 'total':len(news)},
        safe=False,
        json_dumps_params={'ensure_ascii':False}
    )