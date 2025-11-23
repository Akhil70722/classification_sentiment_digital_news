"""
Django views for News Intelligence & Alert System API.

This module handles:
- RSS feed processing and article extraction
- Sentiment analysis and category classification
- Email alerts for negative news
- RESTful API endpoints for frontend
"""

# Standard library imports
import os
import re
import shutil
import smtplib
import threading
import traceback
import math
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Third-party imports
import feedparser
import pandas as pd
import torch
import tensorflow as tf
import xlsxwriter
import contractions
import spacy
from deep_translator import GoogleTranslator
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from newspaper import Article
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TFDistilBertModel,
    pipeline,
    DistilBertTokenizer
)

# ============================================================================
# CONFIGURATION CONSTANTS
# ============================================================================

# RSS feed URLs for news sources
RSS_FEEDS = {
    'News18_Latest': 'https://www.news18.com/rss/news.xml',
    'News18_India': 'https://www.news18.com/rss/india.xml',
    'TheHindu': 'https://www.thehindu.com/news/national/?service=rss',
    'TOI': 'https://timesofindia.indiatimes.com/rssfeedstopstories.cms',
}

# Government department mapping for email alerts
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

# Email configuration for sending alerts
EMAIL_CONFIG = {
    'sender_email': 'putyourmail@gmail.com',  # Replace with your email
    'sender_password': 'bhsq enex bzah rouw',  # Replace with your password
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587
}

# ============================================================================
# NLP MODEL INITIALIZATION
# ============================================================================

# Load SpaCy model for text preprocessing
_nlp = spacy.load('en_core_web_sm')

# Load stopwords (excluding 'not' to preserve negative sentiment)
stopwords = set(
    __import__('nltk').corpus.stopwords.words('english')
) - {'not'}

# Initialize sentiment analysis tokenizer
sent_tok = AutoTokenizer.from_pretrained(
    "tokenizer_roberta/sentiment_tokenizer/"
)

# Load sentiment analysis model (RoBERTa)
try:
    sent_model = AutoModelForSequenceClassification.from_pretrained(
        "cardiffnlp/twitter-roberta-base-sentiment"
    )
except Exception as e:
    print(f"Error loading sentiment model: {e}")
    print("Attempting to download from Hugging Face Hub...")
    # Clear incomplete cache and retry
    import shutil
    cache_dir = os.path.expanduser("~/.cache/huggingface/hub")
    if os.path.exists(cache_dir):
        model_cache_path = None
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
            except Exception:
                pass
    # Retry loading
    sent_model = AutoModelForSequenceClassification.from_pretrained(
        "cardiffnlp/twitter-roberta-base-sentiment",
        force_download=False
    )

# Sentiment label mapping
_label_map = {'negative': 1, 'neutral': 2, 'positive': 0}

# Category classification model (lazy loaded)
cls_model = None
cls_tok = None
_max_len = 512

# Category ID to name mapping
_categories = {
    0: "Entertainment",
    1: "Business",
    2: "Politics",
    3: "Judiciary",
    4: "Crime",
    5: "Culture",
    6: "Sports",
    7: "Science",
    8: "International",
    9: "Technology"
}

# Initialize emotion detection model
emotion_model = pipeline(
    "sentiment-analysis",
    model='bhadresh-savani/distilbert-base-uncased-emotion',
    top_k=1
)

# Global translator instance (reused for performance)
_translator_instance = None

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def _load_category_model():
    """Lazy load category classification model if file exists."""
    global cls_model, cls_tok
    if cls_model is None and os.path.exists("distilbert_model.h5"):
        try:
            custom_objects = {'TFDistilBertModel': TFDistilBertModel}
            cls_model = tf.keras.models.load_model(
                "distilbert_model.h5",
                custom_objects=custom_objects
            )
            cls_tok = DistilBertTokenizer.from_pretrained(
                'distilbert-base-uncased'
            )
        except Exception as e:
            print(f"Warning: Could not load category model: {e}")
            cls_model = False  # Mark as failed
            cls_tok = False


def preprocess(text):
    """
    Preprocess text for NLP analysis.
    
    Args:
        text: Raw text string
        
    Returns:
        Preprocessed text string (lowercased, lemmatized, stopwords removed)
    """
    s = str(text).lower()
    s = contractions.fix(s)  # Expand contractions
    s = re.sub(r'[^a-z\s]', ' ', s)  # Remove special characters
    doc = _nlp(s)
    lemmas = [tok.lemma_ for tok in doc if tok.lemma_ != '-PRON-']
    return ' '.join(w for w in lemmas if w not in stopwords)


def sanitize_for_json(obj):
    """
    Recursively sanitize Python objects to be JSON-safe.
    Replaces NaN, INF, and None values with appropriate defaults.
    
    Args:
        obj: Any Python object (dict, list, scalar)
        
    Returns:
        JSON-safe version of the object
    """
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_json(item) for item in obj]
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return 0.0
        return obj
    elif pd.isna(obj) if hasattr(pd, 'isna') else (obj is None or (isinstance(obj, float) and math.isnan(obj))):
        return None
    elif obj is None:
        return None
    else:
        return obj


def predict_sentiment(text):
    """
    Predict sentiment of text using RoBERTa model.
    
    Args:
        text: Preprocessed text string
        
    Returns:
        List of [positive_score, negative_score, neutral_score]
    """
    inp = sent_tok(text[:514], return_tensors='pt')
    out = sent_model(**inp)
    scores = torch.softmax(out.logits[0], dim=0)
    result = [
        scores[_label_map['positive']].item(),
        scores[_label_map['negative']].item(),
        scores[_label_map['neutral']].item()
    ]
    # Sanitize NaN/INF values
    return [0.0 if (math.isnan(x) or math.isinf(x)) else x for x in result]


def predict_category(text):
    """
    Predict news category using DistilBERT model.
    
    Args:
        text: Preprocessed text string
        
    Returns:
        Category ID (0-9) or 0 as default if model unavailable
    """
    _load_category_model()
    if (cls_model is None or cls_model is False or
            cls_tok is None or cls_tok is False):
        return 0  # Default to Entertainment
    try:
        inp = cls_tok(
            text,
            return_tensors='tf',
            truncation=True,
            padding='max_length',
            max_length=_max_len
        )
        preds = cls_model.predict(
            [inp['input_ids'], inp['attention_mask']]
        )[0]
        return int(preds.argmax())
    except Exception as e:
        print(f"Error predicting category: {e}")
        return 0  # Default to first category


def predict_emotion(text):
    """
    Predict emotion from text using DistilBERT emotion classifier.
    
    Args:
        text: Text string (first 1500 chars)
        
    Returns:
        Emotion label (e.g., 'joy', 'sadness', 'anger')
    """
    return emotion_model(text[:1500])[0][0]['label']


def get_translator(source='en', target='hi'):
    """
    Get or create translator instance (reused for performance).
    
    Args:
        source: Source language code
        target: Target language code
        
    Returns:
        GoogleTranslator instance
    """
    global _translator_instance
    if _translator_instance is None:
        _translator_instance = GoogleTranslator(source=source, target=target)
    return _translator_instance


def translate_text(text, target_lang='hi', max_length=300):
    """
    Translate text to target language.
    
    Args:
        text: Text to translate
        target_lang: Target language code ('hi' for Hindi)
        max_length: Maximum characters to translate
        
    Returns:
        Translated text or empty string on error
    """
    try:
        if not text or len(text.strip()) == 0:
            return ''
        
        # Limit text length for faster translation
        text_to_translate = (text[:max_length]
                           if len(text) > max_length else text)
        
        if target_lang == 'hi':
            translator = get_translator(source='en', target='hi')
            translated = translator.translate(text_to_translate)
            if translated and translated.strip():
                print(f"Translated: '{text_to_translate[:30]}...' "
                      f"-> '{translated[:30]}...'")
                return translated
            else:
                print(f"Translation returned empty for: "
                      f"'{text_to_translate[:30]}...'")
                return ''
        else:
            # Return original if target is English
            return text
    except Exception as e:
        print(f"Translation error for text '{text[:50]}...': {e}")
        traceback.print_exc()
        return ''  # Return empty on error


def send_email(to_emails, subject, body):
    """
    Send email alert to government department.
    
    Args:
        to_emails: List of recipient email addresses
        subject: Email subject line
        body: Email body text
        
    Returns:
        True if sent successfully, False otherwise
    """
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG['sender_email']
        msg['To'] = ", ".join(to_emails)
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(
            EMAIL_CONFIG['smtp_server'],
            EMAIL_CONFIG['smtp_port']
        )
        server.starttls()
        server.login(
            EMAIL_CONFIG['sender_email'],
            EMAIL_CONFIG['sender_password']
        )
        server.sendmail(
            EMAIL_CONFIG['sender_email'],
            to_emails,
            msg.as_string()
        )
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


def _process_crawler_data(crawler_file_name, function_name, source_name, ws, row, max_items=50, timeout=300):
    """
    Process data from crawler Excel files and add to main worksheet.
    
    Args:
        crawler_file_name: Name of the crawler file (without .py)
        function_name: Name of the function to call in the crawler file
        source_name: Source name to use in output
        ws: Worksheet to write to
        row: Current row number
        max_items: Maximum articles to process
        timeout: Maximum time in seconds to wait for crawler (default: 300 = 5 minutes)
        
    Returns:
        Updated row number
    """
    try:
        # Import crawler dynamically
        crawler_module = __import__(f'api.crawlers.{crawler_file_name}', fromlist=[function_name])
        crawler_func = getattr(crawler_module, function_name)
        
        # Run crawler to generate Excel file with timeout using threading
        print(f"[CRAWLER] Running {crawler_file_name} (timeout: {timeout}s)...")
        
        import threading
        crawler_exception = [None]
        
        def run_crawler():
            try:
                crawler_func()
            except Exception as e:
                crawler_exception[0] = e
        
        # Start crawler in a thread
        crawler_thread = threading.Thread(target=run_crawler)
        crawler_thread.daemon = True
        crawler_thread.start()
        crawler_thread.join(timeout=timeout)
        
        # Check if thread is still running (timed out)
        if crawler_thread.is_alive():
            print(f"[WARNING] {crawler_file_name} timed out after {timeout}s, skipping output")
            return row  # Return early without processing output
        
        # Check for exceptions
        if crawler_exception[0]:
            raise crawler_exception[0]
        
        # Read crawler output - check possible file names
        # Mapping of crawler file names to their actual output filenames
        OUTPUT_FILE_MAP = {
            'News18': 'News18.xlsx',
            'News18Punj': 'News18_Punjab.xlsx',
            'IndiaToday': 'IndiaToday.xlsx',
            'IndiaToday_Chandigarh': 'IndiaToday_Chandigarh.xlsx',
            'AajTak': 'AajTak.xlsx',
            'IndiaTv': 'IndiaTv.xlsx',
            'HindustanTime': 'HindustanTime_Chandigarh.xlsx',
            'JagranChandigarh': 'Jagran_Punjab.xlsx',
            'BhaskarChandigarh': 'Bhaskar_Chandigarh.xlsx',
            'TribuneChandigarh': 'Tribune_Chandigarh.xlsx',
        }
        
        # Check both the mapped filename and generic fallbacks
        output_filename = OUTPUT_FILE_MAP.get(crawler_file_name, f'{crawler_file_name}.xlsx')
        alt_files = [
            f'data/raw/{output_filename}',
            f'data/raw/{crawler_file_name}.xlsx',
            f'data/raw/{function_name}.xlsx',
        ]
        
        crawler_file_found = None
        for alt_file in alt_files:
            if os.path.exists(alt_file):
                crawler_file_found = alt_file
                break
        
        if crawler_file_found:
            df_crawler = pd.read_excel(crawler_file_found)
            taken = 0
            
            for idx, crawler_row in df_crawler.iterrows():
                if taken >= max_items:
                    break
                
                heading = str(crawler_row.get('Heading', '')).strip()
                body = str(crawler_row.get('Body', '')).strip()
                url = str(crawler_row.get('URL', '')).strip()
                
                # Skip empty entries
                if not heading or not body or not url:
                    continue
                
                # Write to main worksheet
                ws.write_row(row, 0, [
                    source_name,
                    heading,
                    body,
                    url,
                    '',  # Published date not available from crawler
                    ''   # Image URL not available from crawler
                ])
                row += 1
                taken += 1
            
            print(f"[CRAWLER] {crawler_file_name}: Added {taken} articles")
        else:
            print(f"[WARNING] {crawler_file_name}: Output file not found (checked: {', '.join(alt_files)})")
    except Exception as e:
        print(f"[ERROR] Failed to process {crawler_file_name}: {e}")
        import traceback
        traceback.print_exc()
    
    return row


def _archive_old_data():
    """
    Archive old data from 'data' folder to 'data1' folder with timestamp.
    This ensures old data is preserved and new data starts fresh.
    """
    data_dir = 'data'
    data1_dir = 'data1'
    
    # Check if data directory exists and has content
    if not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)
        return
    
    # Create data1 directory if it doesn't exist
    os.makedirs(data1_dir, exist_ok=True)
    
    # Create timestamped archive folder
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    archive_dir = os.path.join(data1_dir, f'archive_{timestamp}')
    os.makedirs(archive_dir, exist_ok=True)
    
    # Archive all files and subdirectories from data folder
    if os.path.exists(data_dir):
        try:
            # Archive raw folder if it exists
            raw_source = os.path.join(data_dir, 'raw')
            if os.path.exists(raw_source):
                raw_dest = os.path.join(archive_dir, 'raw')
                shutil.copytree(raw_source, raw_dest, dirs_exist_ok=True)
                print(f"[ARCHIVE] Archived raw/ folder to data1/archive_{timestamp}/raw/")
            
            # Archive rss folder if it exists
            rss_source = os.path.join(data_dir, 'rss')
            if os.path.exists(rss_source):
                rss_dest = os.path.join(archive_dir, 'rss')
                shutil.copytree(rss_source, rss_dest, dirs_exist_ok=True)
                print(f"[ARCHIVE] Archived rss/ folder to data1/archive_{timestamp}/rss/")
            
            # Archive processed folder if it exists
            processed_source = os.path.join(data_dir, 'processed')
            if os.path.exists(processed_source):
                processed_dest = os.path.join(archive_dir, 'processed')
                shutil.copytree(processed_source, processed_dest, dirs_exist_ok=True)
                print(f"[ARCHIVE] Archived processed/ folder to data1/archive_{timestamp}/processed/")
            
            # Archive embeddings folder if it exists
            embeddings_source = os.path.join(data_dir, 'embeddings')
            if os.path.exists(embeddings_source):
                embeddings_dest = os.path.join(archive_dir, 'embeddings')
                shutil.copytree(embeddings_source, embeddings_dest, dirs_exist_ok=True)
                print(f"[ARCHIVE] Archived embeddings/ folder to data1/archive_{timestamp}/embeddings/")
            
            # Archive results folder if it exists
            results_source = os.path.join(data_dir, 'results')
            if os.path.exists(results_source):
                results_dest = os.path.join(archive_dir, 'results')
                shutil.copytree(results_source, results_dest, dirs_exist_ok=True)
                print(f"[ARCHIVE] Archived results/ folder to data1/archive_{timestamp}/results/")
            
            # Archive any loose files in data directory
            for item in os.listdir(data_dir):
                item_path = os.path.join(data_dir, item)
                if os.path.isfile(item_path):
                    shutil.copy2(item_path, archive_dir)
                    print(f"[ARCHIVE] Archived {item} to data1/archive_{timestamp}/")
            
            # Clean up data directory (remove old files, keep structure)
            print(f"[ARCHIVE] Cleaning up data/ folder for fresh data collection...")
            try:
                if os.path.exists(raw_source):
                    shutil.rmtree(raw_source)
                    print(f"[ARCHIVE] Removed old data/raw/ folder")
            except Exception as e:
                print(f"[WARNING] Could not remove data/raw/: {e}")
            
            try:
                if os.path.exists(rss_source):
                    shutil.rmtree(rss_source)
                    print(f"[ARCHIVE] Removed old data/rss/ folder")
            except Exception as e:
                print(f"[WARNING] Could not remove data/rss/: {e}")
            
            try:
                if os.path.exists(processed_source):
                    shutil.rmtree(processed_source)
                    print(f"[ARCHIVE] Removed old data/processed/ folder")
            except Exception as e:
                print(f"[WARNING] Could not remove data/processed/: {e}")
            
            try:
                if os.path.exists(embeddings_source):
                    shutil.rmtree(embeddings_source)
                    print(f"[ARCHIVE] Removed old data/embeddings/ folder")
            except Exception as e:
                print(f"[WARNING] Could not remove data/embeddings/: {e}")
            
            try:
                if os.path.exists(results_source):
                    shutil.rmtree(results_source)
                    print(f"[ARCHIVE] Removed old data/results/ folder")
            except Exception as e:
                print(f"[WARNING] Could not remove data/results/: {e}")
            
            # Remove loose files
            try:
                for item in os.listdir(data_dir):
                    item_path = os.path.join(data_dir, item)
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                        print(f"[ARCHIVE] Removed {item}")
            except Exception as e:
                print(f"[WARNING] Could not remove loose files: {e}")
            
            print(f"[ARCHIVE] ✓ Old data archived to: data1/archive_{timestamp}/")
            print(f"[ARCHIVE] ✓ data/ folder cleaned and ready for new data")
        except Exception as e:
            print(f"[WARNING] Error archiving old data: {e}")
            print(f"[WARNING] Continuing with new data collection...")


def fetch_and_process(max_items=50, output_file='RSS_FullText.xlsx'):
    """
    Fetch articles from both RSS feeds AND crawlers simultaneously.
    
    Args:
        max_items: Maximum articles per feed/crawler (default: 50)
        output_file: Output Excel filename
        
    Saves:
        Excel file with columns: Source, Title, FullArticle, Link,
        Published, ImageURL
    """
    # Archive old data to data1 before processing new data
    print("\n" + "=" * 60)
    print("ARCHIVING OLD DATA")
    print("=" * 60)
    _archive_old_data()
    
    # Save to organized data structure (always use 'data' folder)
    rss_dir = 'data/rss'
    os.makedirs(rss_dir, exist_ok=True)
    output_path = os.path.join(rss_dir, output_file)
    wb = xlsxwriter.Workbook(output_path, {'nan_inf_to_errors': False})
    ws = wb.add_worksheet()
    ws.write_row(0, 0, [
        'Source', 'Title', 'FullArticle', 'Link', 'Published', 'ImageURL'
    ])
    row = 1
    
    # Mapping of crawler file names to (function_name, source_name) tuples
    # Format: 'filename': ('function_name', 'output_source_name')
    CRAWLER_SOURCES = {
        'News18': ('News18', 'News18_Crawler'),
        'News18Punj': ('News18Punj', 'News18Punj_Crawler'),
        'IndiaToday': ('IndiaToday', 'IndiaToday_Crawler'),
        'IndiaToday_Chandigarh': ('IndiaToday_Chandigarh', 'IndiaToday_Chandigarh_Crawler'),
        'AajTak': ('AajTak', 'AajTak_Crawler'),
        'IndiaTv': ('IndiaTv', 'IndiaTv_Crawler'),
        'HindustanTime': ('Hindustan', 'HindustanTime_Crawler'),
        'JagranChandigarh': ('JagranChandigarh', 'JagranChandigarh_Crawler'),
        'BhaskarChandigarh': ('Bhaskar', 'BhaskarChandigarh_Crawler'),
        'TribuneChandigarh': ('Tribune', 'TribuneChandigarh_Crawler'),
    }
    
    # ========================================================================
    # STEP 1: Process RSS Feeds
    # ========================================================================
    print("=" * 60)
    print("STEP 1: Processing RSS Feeds")
    print("=" * 60)
    
    for source, url in RSS_FEEDS.items():
        print(f"[RSS] Processing {source}...")
        feed = feedparser.parse(url)
        if not feed.entries:
            print(f"[WARNING] {source}: Feed has no entries!")
            continue
        
        print(f"[RSS] {source}: Found {len(feed.entries)} entries")
        taken = 0
        skipped_videos = 0
        
        for entry in feed.entries:
            if taken >= max_items:
                break
            
            link = entry.get('link', '')
            
            # Skip video links
            if '/video' in link or 'video' in source.lower():
                skipped_videos += 1
                continue
            
            # Skip video media content
            media = entry.get('media_content', [])
            if any(m.get('type', '').startswith('video/') for m in media):
                continue
            
            # Download and extract full article text
            art = Article(link)
            image_url = ''
            try:
                art.download()
                art.parse()
                full = art.text
                image_url = art.top_image or ''
            except Exception:
                full = ''
            
            # Try to get image from RSS feed if article extraction failed
            if not image_url:
                media_content = entry.get('media_content', [])
                if media_content:
                    for media_item in media_content:
                        if media_item.get('type', '').startswith('image/'):
                            image_url = media_item.get('url', '')
                            break
                # Check media_thumbnail
                if not image_url and 'media_thumbnail' in entry:
                    thumbnail = entry.get('media_thumbnail', [{}])
                    if isinstance(thumbnail, list) and thumbnail:
                        image_url = thumbnail[0].get('url', '')
                    else:
                        image_url = str(thumbnail) if thumbnail else ''
            
            # Write row to Excel
            ws.write_row(row, 0, [
                source,
                entry.get('title', ''),
                full,
                link,
                entry.get('published', ''),
                image_url
            ])
            row += 1
            taken += 1
        
        print(f"[RSS] {source}: Scraped {taken} articles, "
              f"Skipped {skipped_videos} videos")
    
    rss_total = row - 1
    print(f"[RSS] Total RSS articles saved: {rss_total}")
    
    # ========================================================================
    # STEP 2: Process Crawlers (with timeout to prevent hanging)
    # ========================================================================
    print("\n" + "=" * 60)
    print("STEP 2: Processing Web Crawlers")
    print("=" * 60)
    print("[NOTE] Crawlers may take several minutes. Each crawler visits multiple URLs.")
    
    for crawler_file_name, (function_name, source_name) in CRAWLER_SOURCES.items():
        print(f"\n[CRAWLER] Processing {crawler_file_name}...")
        try:
            # Set timeout to 5 minutes per crawler (300 seconds)
            row = _process_crawler_data(crawler_file_name, function_name, source_name, ws, row, max_items, timeout=300)
        except TimeoutError as e:
            print(f"[ERROR] {e}")
            print(f"[SKIP] Skipping {crawler_file_name} due to timeout")
            continue
        except Exception as e:
            print(f"[ERROR] Failed to process {crawler_file_name}: {e}")
            continue
    
    crawler_total = row - 1 - rss_total
    print(f"\n[CRAWLER] Total crawler articles saved: {crawler_total}")
    
    # ========================================================================
    # Final Summary
    # ========================================================================
    wb.close()
    total_articles = row - 1
    print("\n" + "=" * 60)
    print(f"SUMMARY: Total articles from all sources: {total_articles}")
    print(f"  - RSS Feeds: {rss_total} articles")
    print(f"  - Web Crawlers: {crawler_total} articles")
    print("=" * 60)


def _process_news_data(language='en'):
    """
    Process RSS feeds and analyze news articles.
    
    Args:
        language: Language code ('en' or 'hi')
        
    Returns:
        Tuple of (news_list, negative_news_list)
    """
    print(f"Processing news data for language: {language}")
    
    # Fetch full articles in background thread
    thread = threading.Thread(target=fetch_and_process)
    thread.start()
    thread.join()
    
    # Load data from organized data structure
    rss_file = None
    for path in ['data/rss/RSS_FullText.xlsx', '../data/rss/RSS_FullText.xlsx', 'RSS_FullText.xlsx']:
        if os.path.exists(path):
            rss_file = path
            break
    if rss_file is None:
        raise FileNotFoundError("Could not find RSS_FullText.xlsx. Expected in data/rss/")
    df = pd.read_excel(rss_file)
    
    # Reset translator instance for new request
    global _translator_instance
    if language == 'hi':
        _translator_instance = None
        print(f"Starting translation to Hindi for {len(df)} items "
              f"(this may take 30-60 seconds)...")
    
    # Process each article
    news = []
    negative_news = []
    output_rows = []
    total_articles = len(df)
    
    print(f"\nProcessing {total_articles} articles for sentiment analysis and categorization...")
    print("This may take 2-5 minutes. Progress will be shown every 10 articles.")
    
    for idx, row in df.iterrows():
        # Show progress every 10 articles
        if (idx + 1) % 10 == 0:
            print(f"  ✓ Processed {idx + 1}/{total_articles} articles...")
        
        try:
            raw = row['FullArticle'] or ''
            if not raw or len(raw.strip()) < 50:
                # Skip articles with very little content
                continue
                
            clean = preprocess(raw)
            cat_id = predict_category(clean)
            cat_name = _categories[cat_id]
            sent = predict_sentiment(clean)
            emo = predict_emotion(clean)
            dept = DEPARTMENT_MAPPING.get(cat_id, {}).get('name', '')
            
            # Check for negative sentiment (>95%)
            # Use sanitized sentiment for check
            sent_safe_check = [
                0.0 if (math.isnan(x) or math.isinf(x)) else float(x)
                for x in sent
            ]
            if sent_safe_check[1] > 0.95:
                negative_news.append({
                    'title': str(row['Title']) if pd.notna(row['Title']) else '',
                    'url': str(row['Link']) if pd.notna(row['Link']) else '',
                    'category': str(cat_name) if cat_name else '',
                    'sentiment': sent_safe_check,
                    'published': str(row['Published']) if pd.notna(row['Published']) else '',
                    'source': str(row['Source']) if pd.notna(row['Source']) else '',
                    'description': (str(raw)[:1000] + '...'
                                  if len(str(raw)) > 1000 else str(raw))
                })
            
            # Extract image URL - use existing, skip slow downloads
            image_url = ''
            try:
                if 'ImageURL' in row and pd.notna(row['ImageURL']):
                    img_val = str(row['ImageURL']).strip()
                    if img_val and img_val != 'nan' and img_val != '':
                        image_url = img_val
            except Exception:
                image_url = ''
            # NOTE: Removed slow Article() download/parse to speed up processing
            
            # Sanitize sentiment scores (replace NaN/INF with 0.0)
            sent_safe = [
                0.0 if (math.isnan(x) or math.isinf(x)) else float(x)
                for x in sent
            ]
            
            # Prepare news item
            news_item = {
                'Source': str(row['Source']) if pd.notna(row['Source']) else '',
                'Title': str(row['Title']) if pd.notna(row['Title']) else '',
                'FullArticle': str(raw) if raw else '',
                'URL': str(row['Link']) if pd.notna(row['Link']) else '',
                'Published': str(row['Published']) if pd.notna(row['Published']) else '',
                'Category': str(cat_name) if cat_name else '',
                'Sentiment': sent_safe,  # Use sanitized sentiment
                'Emotion': str(emo) if emo else '',
                'Department': str(dept) if dept else '',
                'ImageURL': str(image_url) if image_url else '',
            }
            
            # Sanitize entire news_item for JSON safety
            news_item = sanitize_for_json(news_item)
            
            # Translate if Hindi requested
            if language == 'hi':
                try:
                    translated_title = translate_text(
                        str(row['Title']), 'hi', max_length=200
                    )
                    news_item['TitleHindi'] = (
                        translated_title if translated_title and
                        translated_title.strip() else ''
                    )
                    
                    description = (str(raw)[:200] + '...'
                                 if len(str(raw)) > 200 else str(raw))
                    translated_desc = translate_text(
                        description, 'hi', max_length=200
                    )
                    news_item['DescriptionHindi'] = (
                        translated_desc if translated_desc and
                        translated_desc.strip() else ''
                    )
                    news_item['FullArticleHindi'] = ''
                    
                    if (idx + 1) % 10 == 0:
                        print(f"Translated {idx + 1}/{len(df)} items...")
                except Exception as e:
                    print(f"Error translating news item "
                          f"{row['Title'][:50]}: {e}")
                    news_item['TitleHindi'] = ''
                    news_item['DescriptionHindi'] = ''
                    news_item['FullArticleHindi'] = ''
            else:
                news_item['TitleHindi'] = ''
                news_item['DescriptionHindi'] = ''
                news_item['FullArticleHindi'] = ''
            
            news.append(news_item)
            
            # Sanitize sentiment scores for Excel (handle NaN/INF)
            sent_safe = [
                0.0 if (math.isnan(x) or math.isinf(x)) else x 
                for x in sent
            ]
            
            # Prepare Excel output row (convert all to strings to avoid NaN issues)
            output_rows.append([
                str(row['Source']) if pd.notna(row['Source']) else '',
                str(row['Title']) if pd.notna(row['Title']) else '',
                str(raw) if raw else '',
                str(row['Link']) if pd.notna(row['Link']) else '',
                str(row['Published']) if pd.notna(row['Published']) else '',
                (f"Positive={sent_safe[0]:.2f}, Negative={sent_safe[1]:.2f}, "
                 f"Neutral={sent_safe[2]:.2f}"),
                str(cat_name) if cat_name else '',
                str(emo) if emo else '',
                str(dept) if dept else ''
            ])
        except Exception as e:
            # Skip articles that fail processing, log error
            print(f"  ⚠ Error processing article {idx + 1} ({row.get('Title', 'Unknown')[:50]}): {str(e)[:100]}")
            continue
    
    print(f"\n✓ Finished processing: {len(news)} articles successfully processed out of {total_articles}")
    
    # Write processed data to Excel in organized data structure
    rss_dir = 'data/rss'
    os.makedirs(rss_dir, exist_ok=True)
    output_file = os.path.join(rss_dir, 'RSS_Processed.xlsx')
    wb = xlsxwriter.Workbook(output_file, {'nan_inf_to_errors': False})
    ws = wb.add_worksheet()
    ws.write_row(0, 0, [
        'Source', 'Title', 'FullArticle', 'Link', 'Published',
        'Sentiment', 'Category', 'Emotion', 'Department'
    ])
    for idx, row_data in enumerate(output_rows, 1):
        ws.write_row(idx, 0, row_data)
    wb.close()
    
    # Send email alerts for negative news
    for item in negative_news:
        department = DEPARTMENT_MAPPING.get(
            predict_category(preprocess(item['description']))
        )
        
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
            
            subject = (f"Negative News Alert: {item['category']} - "
                      f"{item['title'][:50]}...")
            
            success = send_email(
                department['emails'],
                subject,
                email_body
            )
            
            if success:
                print(f"Alert sent to {department['name']} about: "
                      f"{item['url']}")
            else:
                print(f"Failed to send alert about: {item['url']}")
    
    print(f"Total news items processed: {len(news)}")
    if language == 'hi':
        print(f"Translation completed for {len(news)} items")
    
    return news, negative_news

# ============================================================================
# API VIEW CLASSES
# ============================================================================


class CsrfExemptMixin:
    """Mixin to exempt CSRF verification for API endpoints."""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class HealthCheckView(CsrfExemptMixin, View):
    """Health check endpoint - returns API status."""
    
    def get(self, request):
        """
        Handle GET request for health check.
        
        Returns:
            JSON response with API status and timestamp
        """
        return JsonResponse({
            'status': 'healthy',
            'service': 'News Intelligence & Alert System',
            'timestamp': pd.Timestamp.now().isoformat()
        })


class CategoriesView(CsrfExemptMixin, View):
    """Get list of all available news categories."""
    
    def get(self, request):
        """
        Handle GET request to retrieve categories.
        
        Returns:
            JSON response with list of categories
        """
        categories = [
            {'id': 0, 'name': 'Entertainment',
             'frontend_name': 'Information and Broadcasting'},
            {'id': 1, 'name': 'Business', 'frontend_name': 'Finance'},
            {'id': 2, 'name': 'Politics', 'frontend_name': 'Politics'},
            {'id': 3, 'name': 'Judiciary',
             'frontend_name': 'Law and Justice'},
            {'id': 4, 'name': 'Crime',
             'frontend_name': 'Internal Security'},
            {'id': 5, 'name': 'Culture', 'frontend_name': 'Culture'},
            {'id': 6, 'name': 'Sports',
             'frontend_name': 'Youth Affairs and Sports'},
            {'id': 7, 'name': 'Science',
             'frontend_name': 'Science and Technology'},
            {'id': 8, 'name': 'International',
             'frontend_name': 'External Affairs'},
            {'id': 9, 'name': 'Technology',
             'frontend_name': 'Electronics and Information Technology'},
        ]
        
        return JsonResponse({
            'result': 'success',
            'categories': categories,
            'total': len(categories)
        })


class NewsListView(CsrfExemptMixin, View):
    """GET endpoint to fetch all news articles."""
    
    def get(self, request):
        """
        Handle GET request to retrieve all news.
        
        Query params:
            language: Language code ('en' or 'hi', default: 'en')
            
        Returns:
            JSON response with news articles
        """
        print("GET /api/news/ - Fetching all news")
        
        language = request.GET.get('language', 'en')
        
        try:
            news, negative_news = _process_news_data(language)
            
            if len(news) == 0:
                return JsonResponse(
                    {
                        'result': 'success',
                        'news': [],
                        'message': 'No news items available',
                        'total': 0
                    },
                    safe=False,
                    json_dumps_params={'ensure_ascii': False}
                )
            
            # Final sanitization of news list before JSON serialization
            news_sanitized = sanitize_for_json(news)
            
            return JsonResponse(
                {
                    'result': 'success',
                    'news': news_sanitized,
                    'total': len(news_sanitized)
                },
                safe=False,
                json_dumps_params={'ensure_ascii': False}
            )
        except Exception as e:
            print(f"Error in NewsListView: {e}")
            traceback.print_exc()
            return JsonResponse(
                {
                    'result': 'error',
                    'message': str(e),
                    'news': []
                },
                safe=False,
                status=500
            )


class NewsFilterView(CsrfExemptMixin, View):
    """POST endpoint to filter news by category."""
    
    def post(self, request):
        """
        Handle POST request to filter news by category.
        
        Request body (JSON):
            category: Category name to filter by
            language: Language code ('en' or 'hi', default: 'en')
            
        Returns:
            JSON response with filtered news articles
        """
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
                    {
                        'result': 'success',
                        'news': [],
                        'message': 'No news items available',
                        'total': 0,
                        'filtered': 0
                    },
                    safe=False,
                    json_dumps_params={'ensure_ascii': False}
                )
            
            # Filter by category if provided
            if category_filter:
                filtered_news = self._filter_by_category(news, category_filter)
                
                print(f"Filtered news items: {len(filtered_news)}")
                
                return JsonResponse(
                    {
                        'result': 'success',
                        'news': filtered_news,
                        'total': len(news),
                        'filtered': len(filtered_news)
                    },
                    safe=False,
                    json_dumps_params={'ensure_ascii': False}
                )
            else:
                # No category filter, return all news
                news_sanitized = sanitize_for_json(news)
                return JsonResponse(
                    {
                        'result': 'success',
                        'news': news_sanitized,
                        'total': len(news_sanitized)
                    },
                    safe=False,
                    json_dumps_params={'ensure_ascii': False}
                )
                
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return JsonResponse(
                {
                    'result': 'error',
                    'message': f'Invalid JSON: {str(e)}',
                    'news': []
                },
                status=400
            )
        except Exception as e:
            print(f"Error in NewsFilterView: {e}")
            traceback.print_exc()
            return JsonResponse(
                {
                    'result': 'error',
                    'message': str(e),
                    'news': []
                },
                status=500
            )
    
    def _filter_by_category(self, news, category_filter):
        """
        Helper method to filter news by category.
        
        Args:
            news: List of news items
            category_filter: Category name to filter by
            
        Returns:
            Filtered list of news items
        """
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
        
        backend_category = category_mapping.get(
            category_filter, category_filter
        )
        print(f"Mapped category: {backend_category}")
        
        # Filter news by category (case-insensitive)
        filtered_news = [
            item for item in news
            if item.get('Category') and
            str(item.get('Category')).strip().lower() ==
            str(backend_category).strip().lower()
        ]
        
        # Try partial matching if no exact match
        if len(filtered_news) == 0:
            filtered_news = [
                item for item in news
                if item.get('Category') and
                str(backend_category).strip().lower() in
                str(item.get('Category')).strip().lower()
            ]
        
        return filtered_news

# ============================================================================
# LEGACY ENDPOINT (for backward compatibility)
# ============================================================================


@csrf_exempt
def index(request):
    """
    Legacy endpoint for backward compatibility.
    
    Supports both GET and POST requests.
    GET: Returns all news
    POST: Can filter by category and language
    
    Returns:
        JSON response with news articles
    """
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
        except Exception:
            pass
    
    print(f"Requested language: {language}")
    
    # Fetch full articles in background thread
    thread = threading.Thread(target=fetch_and_process)
    thread.start()
    thread.join()
    
    # Load data from organized data structure
    rss_file = None
    for path in ['data/rss/RSS_FullText.xlsx', '../data/rss/RSS_FullText.xlsx', 'RSS_FullText.xlsx']:
        if os.path.exists(path):
            rss_file = path
            break
    if rss_file is None:
        raise FileNotFoundError("Could not find RSS_FullText.xlsx. Expected in data/rss/")
    df = pd.read_excel(rss_file)
    
    # Reset translator instance for new request
    global _translator_instance
    if language == 'hi':
        _translator_instance = None
        print(f"Starting translation to Hindi for {len(df)} items "
              f"(this may take 30-60 seconds)...")
    
    # Process each article
    news = []
    negative_news = []
    output_rows = []
    
    for idx, row in df.iterrows():
        raw = row['FullArticle'] or ''
        clean = preprocess(raw)
        cat_id = predict_category(clean)
        cat_name = _categories[cat_id]
        sent = predict_sentiment(clean)
        emo = predict_emotion(clean)
        dept = DEPARTMENT_MAPPING.get(cat_id, {}).get('name', '')
        
        # Check for negative sentiment (>95%)
        # Use sanitized sentiment for check
        sent_safe_check = [
            0.0 if (math.isnan(x) or math.isinf(x)) else float(x)
            for x in sent
        ]
        if sent_safe_check[1] > 0.95:
            negative_news.append({
                'title': str(row['Title']) if pd.notna(row['Title']) else '',
                'url': str(row['Link']) if pd.notna(row['Link']) else '',
                'category': str(cat_name) if cat_name else '',
                'sentiment': sent_safe_check,
                'published': str(row['Published']) if pd.notna(row['Published']) else '',
                'source': str(row['Source']) if pd.notna(row['Source']) else '',
                'description': (str(raw)[:1000] + '...'
                              if len(str(raw)) > 1000 else str(raw))
            })
        
        # Extract image URL
        image_url = ''
        try:
            if 'ImageURL' in row and pd.notna(row['ImageURL']):
                image_url = str(row['ImageURL'])
            if not image_url or image_url == 'nan':
                art = Article(row['Link'])
                art.download()
                art.parse()
                image_url = art.top_image or ''
        except Exception:
            image_url = ''
        
        # Sanitize sentiment scores (replace NaN/INF with 0.0)
        sent_safe = [
            0.0 if (math.isnan(x) or math.isinf(x)) else float(x)
            for x in sent
        ]
        
        # Prepare news item
        news_item = {
            'Source': str(row['Source']) if pd.notna(row['Source']) else '',
            'Title': str(row['Title']) if pd.notna(row['Title']) else '',
            'FullArticle': str(raw) if raw else '',
            'URL': str(row['Link']) if pd.notna(row['Link']) else '',
            'Published': str(row['Published']) if pd.notna(row['Published']) else '',
            'Category': str(cat_name) if cat_name else '',
            'Sentiment': sent_safe,  # Use sanitized sentiment
            'Emotion': str(emo) if emo else '',
            'Department': str(dept) if dept else '',
            'ImageURL': str(image_url) if image_url else '',
        }
        
        # Sanitize entire news_item for JSON safety
        news_item = sanitize_for_json(news_item)
        
        # Translate if Hindi requested
        if language == 'hi':
            try:
                translated_title = translate_text(
                    str(row['Title']), 'hi', max_length=200
                )
                news_item['TitleHindi'] = (
                    translated_title if translated_title and
                    translated_title.strip() else ''
                )
                
                description = (str(raw)[:200] + '...'
                             if len(str(raw)) > 200 else str(raw))
                translated_desc = translate_text(
                    description, 'hi', max_length=200
                )
                news_item['DescriptionHindi'] = (
                    translated_desc if translated_desc and
                    translated_desc.strip() else ''
                )
                news_item['FullArticleHindi'] = ''
                
                if (idx + 1) % 10 == 0:
                    print(f"Translated {idx + 1}/{len(df)} items...")
                    print(f"Sample translation - Title: "
                          f"{translated_title[:50]}...")
            except Exception as e:
                print(f"Error translating news item "
                      f"{row['Title'][:50]}: {e}")
                traceback.print_exc()
                news_item['TitleHindi'] = ''
                news_item['DescriptionHindi'] = ''
                news_item['FullArticleHindi'] = ''
        else:
            news_item['TitleHindi'] = ''
            news_item['DescriptionHindi'] = ''
            news_item['FullArticleHindi'] = ''
        
        news.append(news_item)
        
        # Sanitize sentiment scores for Excel (handle NaN/INF)
        sent_safe = [
            0.0 if (math.isnan(x) or math.isinf(x)) else x 
            for x in sent
        ]
        
        # Prepare Excel output row (convert all to strings to avoid NaN issues)
        output_rows.append([
            str(row['Source']) if pd.notna(row['Source']) else '',
            str(row['Title']) if pd.notna(row['Title']) else '',
            str(raw) if raw else '',
            str(row['Link']) if pd.notna(row['Link']) else '',
            str(row['Published']) if pd.notna(row['Published']) else '',
            (f"Positive={sent_safe[0]:.2f}, Negative={sent_safe[1]:.2f}, "
             f"Neutral={sent_safe[2]:.2f}"),
            str(cat_name) if cat_name else '',
            str(emo) if emo else '',
            str(dept) if dept else ''
        ])
    
    # Write processed data to Excel in organized data structure
    rss_dir = 'data/rss'
    os.makedirs(rss_dir, exist_ok=True)
    output_file = os.path.join(rss_dir, 'RSS_Processed.xlsx')
    wb = xlsxwriter.Workbook(output_file, {'nan_inf_to_errors': False})
    ws = wb.add_worksheet()
    ws.write_row(0, 0, [
        'Source', 'Title', 'FullArticle', 'Link', 'Published',
        'Sentiment', 'Category', 'Emotion', 'Department'
    ])
    for idx, row_data in enumerate(output_rows, 1):
        ws.write_row(idx, 0, row_data)
    wb.close()
    
    # Send email alerts for negative news
    for item in negative_news:
        department = DEPARTMENT_MAPPING.get(
            predict_category(preprocess(item['description']))
        )
        
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
            
            subject = (f"Negative News Alert: {item['category']} - "
                      f"{item['title'][:50]}...")
            
            success = send_email(
                department['emails'],
                subject,
                email_body
            )
            
            if success:
                print(f"Alert sent to {department['name']} about: "
                      f"{item['url']}")
            else:
                print(f"Failed to send alert about: {item['url']}")
    
    print(f"Total news items processed: {len(news)}")
    if language == 'hi':
        print(f"Translation completed for {len(news)} items")
    
    # Handle empty news list
    if len(news) == 0:
        print("WARNING: No news items were processed!")
        return JsonResponse(
            {
                'result': 'success',
                'news': [],
                'message': 'No news items available'
            },
            safe=False,
            json_dumps_params={'ensure_ascii': False}
        )
    
    # Handle POST request for category filtering
    if request.method == 'POST':
        try:
            import json
            if not request.body:
                print("POST request body is empty, returning all news")
                return JsonResponse(
                    {'result': 'success', 'news': news},
                    safe=False,
                    json_dumps_params={'ensure_ascii': False}
                )
            
            body_str = request.body.decode('utf-8')
            print(f"POST request body: {body_str}")
            
            if not body_str.strip():
                print("POST request body is empty after decode, "
                      "returning all news")
                return JsonResponse(
                    {'result': 'success', 'news': news},
                    safe=False,
                    json_dumps_params={'ensure_ascii': False}
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
                
                backend_category = category_mapping.get(
                    category_filter, category_filter
                )
                print(f"Mapped category: {backend_category}")
                print(f"Total news items: {len(news)}")
                
                # Get unique categories for debugging
                unique_categories = list(
                    set([item.get('Category') for item in news])
                )
                print(f"Available categories in news: {unique_categories}")
                
                # Filter news by category (case-insensitive)
                filtered_news = [
                    item for item in news
                    if item.get('Category') and
                    str(item.get('Category')).strip().lower() ==
                    str(backend_category).strip().lower()
                ]
                print(f"Filtered news items: {len(filtered_news)}")
                
                # Try partial matching if no exact match
                if len(filtered_news) == 0:
                    print(f"Trying partial match for category: "
                          f"{backend_category}")
                    filtered_news = [
                        item for item in news
                        if item.get('Category') and
                        str(backend_category).strip().lower() in
                        str(item.get('Category')).strip().lower()
                    ]
                    print(f"Partial match results: {len(filtered_news)}")
                
                # Try reverse partial matching
                if len(filtered_news) == 0:
                    print(f"Trying reverse partial match for category: "
                          f"{backend_category}")
                    filtered_news = [
                        item for item in news
                        if item.get('Category') and
                        str(item.get('Category')).strip().lower() in
                        str(backend_category).strip().lower()
                    ]
                    print(f"Reverse partial match results: "
                          f"{len(filtered_news)}")
                
                print(f"Final filtered news count: {len(filtered_news)}")
                if len(filtered_news) > 0:
                    print(f"Sample filtered item category: "
                          f"{filtered_news[0].get('Category')}")
                
                return JsonResponse(
                    {
                        'result': 'success',
                        'news': filtered_news,
                        'total': len(news),
                        'filtered': len(filtered_news)
                    },
                    safe=False,
                    json_dumps_params={'ensure_ascii': False}
                )
            else:
                print("No category filter provided in POST request, "
                      "returning all news")
                news_sanitized = sanitize_for_json(news)
                return JsonResponse(
                    {
                        'result': 'success',
                        'news': news_sanitized,
                        'total': len(news_sanitized)
                    },
                    safe=False,
                    json_dumps_params={'ensure_ascii': False}
                )
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print(f"Request body (raw): {request.body}")
            traceback.print_exc()
            return JsonResponse(
                {
                    'result': 'error',
                    'message': f'Invalid JSON: {str(e)}',
                    'news': []
                },
                safe=False
            )
        except Exception as e:
            print(f"ERROR filtering by category: {e}")
            traceback.print_exc()
            news_sanitized = sanitize_for_json(news)
            return JsonResponse(
                {
                    'result': 'error',
                    'message': str(e),
                    'news': news_sanitized,
                    'total': len(news_sanitized)
                },
                safe=False,
                json_dumps_params={'ensure_ascii': False}
            )
    
    # Default GET request returns all news
    print(f"GET request: Returning all {len(news)} news items")
    news_sanitized = sanitize_for_json(news)
    return JsonResponse(
        {
            'result': 'success',
            'news': news_sanitized,
            'total': len(news_sanitized)
        },
        safe=False,
        json_dumps_params={'ensure_ascii': False}
    )
