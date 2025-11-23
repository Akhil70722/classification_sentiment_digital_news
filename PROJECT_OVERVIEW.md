# 📡 News Intelligence & Alert System - Complete End-to-End Overview

## 🎯 Project Purpose
This is an **automated news monitoring and alert system** designed for government ministries. It:
- Collects news from major Indian news portals
- Classifies articles into relevant government ministries
- Analyzes sentiment to identify negative news
- Sends automatic email alerts to appropriate authorities
- Provides a web interface for viewing and filtering news

---

## 📊 Complete Data Flow Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATA COLLECTION LAYER                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────┴─────────────────────┐
        │                                             │
        ▼                                             ▼
┌───────────────┐                          ┌──────────────────┐
│  RSS FEEDS    │                          │  WEB SCRAPERS    │
│  (Primary)   │                          │   (Legacy)       │
└───────────────┘                          └──────────────────┘
        │                                             │
        │ feedparser                                  │ BeautifulSoup
        │ newspaper3k                                 │ requests
        │                                             │
        ▼                                             ▼
┌──────────────────────────────────────────────────────────────┐
│              DATA STORAGE (data/rss/)                         │
│  - RSS_FullText.xlsx (Full article text from RSS)            │
│  - RSS_Processed.xlsx (After sentiment analysis)             │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│              DATA PREPROCESSING                                │
│  - Lowercasing, Contraction expansion                         │
│  - Stopword removal, Lemmatization                            │
│  - Special character removal                                  │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│              NLP ANALYSIS                                      │
│  1. Category Classification (DistilBERT)                      │
│  2. Sentiment Analysis (RoBERTa)                              │
│  3. Emotion Detection (DistilBERT Emotion)                    │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────┴─────────────────────┐
        │                                             │
        ▼                                             ▼
┌───────────────┐                          ┌──────────────────┐
│ EMAIL ALERTS  │                          │  WEB FRONTEND    │
│ (if negative) │                          │  (Next.js)       │
└───────────────┘                          └──────────────────┘
```

---

## 1️⃣ DATA COLLECTION - Where News Comes From

### **Dual Method: RSS Feeds + Web Crawlers (Both Run Simultaneously)**

The system uses **both RSS feeds and web crawlers simultaneously** (not as fallback) for comprehensive news coverage.

---

### **Method 1: RSS Feeds (Primary)**

**Technology Stack:**
- **feedparser**: Python library for parsing RSS/Atom feeds
- **newspaper3k**: Automatic article extraction from URLs
- **Threading**: Background processing for faster execution

**How It Works:**
1. **RSS Feed URLs** (defined in `server/api/views.py`):
   ```python
   RSS_FEEDS = {
       'News18_Latest': 'https://www.news18.com/rss/news.xml',
       'News18_India': 'https://www.news18.com/rss/india.xml',
       'TheHindu': 'https://www.thehindu.com/news/national/?service=rss',
       'TOI': 'https://timesofindia.indiatimes.com/rssfeedstopstories.cms',
   }
   ```

2. **Processing Flow** (`fetch_and_process()` function):
   - Parses RSS XML using `feedparser.parse(url)`
   - Extracts article metadata (title, link, published date)
   - For each article URL:
     - Uses `newspaper3k.Article()` to download and parse full article text
     - Extracts article image URL
     - Skips video content
   - Saves to `data/rss/RSS_FullText.xlsx`

3. **Data Extracted:**
   - Source (News18, TheHindu, etc.)
   - Title (Headline)
   - FullArticle (Complete article text)
   - Link (Article URL)
   - Published date
   - Image URL

---

### **Method 2: Web Crawlers (Secondary - Runs Simultaneously)**

**Technology Stack:**
- **BeautifulSoup**: HTML parsing and content extraction
- **requests**: HTTP requests to news websites
- **Threading with Timeout**: Prevents crawlers from hanging
- **Robust Selectors**: Multiple fallback HTML selectors for reliability

**Crawler Sources** (10+ news sources):
- News18 (English)
- News18 Punjab (Punjabi)
- IndiaToday
- IndiaToday Chandigarh
- AajTak
- IndiaTV
- Hindustan Times (Chandigarh)
- Jagran (Punjab)
- Bhaskar (Chandigarh)
- Tribune (Chandigarh)

**How It Works:**
1. **Crawler Functions** (in `server/api/crawlers/*.py`):
   - Visit news website homepages
   - Extract article links
   - Visit each article URL
   - Extract heading and body content using multiple HTML selectors
   - Validate content (minimum paragraphs, length checks)
   - Save to `data/raw/{SourceName}.xlsx`

2. **Processing Flow** (`_process_crawler_data()` function):
   - Runs crawler function with timeout (5 minutes max)
   - Reads crawler output from `data/raw/*.xlsx`
   - Merges into main `data/rss/RSS_FullText.xlsx`
   - Handles errors gracefully (continues if one crawler fails)

3. **Data Extracted:**
   - Source (News18_Crawler, IndiaToday_Crawler, etc.)
   - Heading (Article title)
   - Body (Full article text)
   - URL (Article link)

**Content Validation:**
- Minimum 3 paragraphs per article
- Minimum 20 characters per paragraph
- Minimum 100 characters total content
- Minimum 10 characters for heading

---

### **Data Merging:**

Both RSS feeds and crawlers write to the **same Excel file** (`data/rss/RSS_FullText.xlsx`):
- RSS articles: Written first
- Crawler articles: Appended after RSS articles
- All articles are then processed together for sentiment analysis
   - Published (Publication date)
   - ImageURL (Article image)

**Why RSS Feeds?**
- ✅ Legal & Compliant (officially provided by news sites)
- ✅ No blocking or bot detection
- ✅ Fast (no browser automation needed)
- ✅ Reliable (standardized XML format)

### **Method 2: Web Scrapers (Legacy - Optional)**

**Technology Stack:**
- **BeautifulSoup**: HTML parsing
- **requests**: HTTP requests
- **xlsxwriter**: Excel file creation

**How It Works:**
1. **Crawler Scripts** (in `server/api/crawlers/`):
   - `News18.py`, `IndiaToday.py`, `IndiaTv.py`, etc.
   - Each script scrapes a specific news website

2. **Scraping Process** (Example: `News18.py`):
   ```python
   # 1. Fetch homepage HTML
   r = requests.get('https://www.news18.com', headers=HEADERS)
   
   # 2. Parse HTML with BeautifulSoup
   soup = BeautifulSoup(r.text, 'html.parser')
   
   # 3. Extract all article links
   for url in soup.findAll('a'):
       # Filter valid article URLs
       # Visit each URL and extract heading + body
   
   # 4. Save to Excel
   workbook = xlsxwriter.Workbook('data/raw/News18.xlsx')
   ```

3. **Data Extracted:**
   - Heading (Article title)
   - Body (Article content)
   - Category (from URL path)
   - URL (Article link)

4. **Storage Location:**
   - All scraped data saved to `data/raw/*.xlsx`
   - Files: `IndiaToday.xlsx`, `News18.xlsx`, `IndiaTv.xlsx`, etc.

**Note:** RSS feeds are the primary method. Web scrapers are legacy code that can be used for additional data collection if needed.

---

## 2️⃣ DATA STORAGE - Where Data is Stored

### **Current Active Folder Structure (data/):**

```
server/
├── data/                    ← ACTIVE (new data always goes here)
│   ├── raw/                 ← Crawler outputs (temporary)
│   │   ├── News18.xlsx
│   │   ├── IndiaToday.xlsx
│   │   ├── IndiaTv.xlsx
│   │   └── ... (10+ news sources)
│   └── rss/                 ← RSS & processed data (permanent)
│       ├── RSS_FullText.xlsx   ← Merged data from RSS + crawlers
│       └── RSS_Processed.xlsx  ← Sentiment analysis results
│
└── data1/                   ← ARCHIVE (old data preserved here)
    └── archive_YYYYMMDD_HHMMSS/
        ├── raw/             ← Archived crawler outputs
        └── rss/             ← Archived RSS data
```

### **Automatic Data Archiving:**

**How It Works:**
1. **Before each API run**: Old data from `data/` is automatically archived to `data1/archive_TIMESTAMP/`
2. **Fresh start**: `data/` folder is cleaned for new data collection
3. **No data loss**: All historical data is preserved with timestamps
4. **Automatic**: No manual intervention needed

**Archive Function:**
- Moves `data/raw/` → `data1/archive_TIMESTAMP/raw/`
- Moves `data/rss/` → `data1/archive_TIMESTAMP/rss/`
- Preserves folder structure
- Creates timestamped folders (e.g., `archive_20251123_163651/`)

### **Data Flow:**

1. **Archive**: Old `data/` → `data1/archive_TIMESTAMP/` (automatic)
2. **Collect**: RSS feeds + Crawlers → `data/rss/RSS_FullText.xlsx` (merged)
3. **Analyze**: Sentiment analysis → `data/rss/RSS_Processed.xlsx`
4. **Display**: Frontend reads from API (which reads from `RSS_Processed.xlsx`)

### **Legacy Folders (data1/ - Not Used by Current System):**

The following folders exist in `data1/` but are **NOT** created by the current Django application:
- `data1/processed/` - From old Jupyter notebook preprocessing (not used)
- `data1/embeddings/` - From old clustering notebooks (not used)
- `data1/results/` - From old analysis notebooks (not used)

**Note**: These folders are from model training phase. The current production system only uses `data/raw/` and `data/rss/`.

---

## 3️⃣ DATA PREPROCESSING - Cleaning the Data

**Location:** `models/preprocessing/Data Preprocessing.ipynb`

**Steps:**

1. **Load Raw Data:**
   - Reads Excel files from `data/raw/` (e.g., `IndiaToday.xlsx`)

2. **Text Preprocessing** (`preprocess()` function):
   ```python
   # a. Lowercasing
   text = text.lower()
   
   # b. Contraction Expansion
   text = contractions.fix(text)  # "don't" → "do not"
   
   # c. Remove Special Characters
   text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
   
   # d. Lemmatization (using SpaCy)
   nlp = spacy.load('en_core_web_sm')
   text = ' '.join([word.lemma_ for word in nlp(text)])
   
   # e. Stopword Removal (NLTK)
   # Removes common words like "the", "is", "a"
   # BUT keeps "not" to preserve negative sentiment
   ```

3. **Data Cleaning:**
   - Remove "Edited By:" text from articles
   - Filter out horoscope articles
   - Drop rows with missing data
   - Remove empty strings

4. **Output:**
   - Saves to `data/processed/Final_Prepped_Data.xlsx`
   - Converts to CSV: `data/processed/final_dataset_Preprocessed.csv`

**Purpose:** Clean, normalized text ready for machine learning models.

---

## 4️⃣ CLUSTERING - Grouping Similar News

### **K-Means Clustering** (`models/clustering/K_Means.ipynb`)

**Purpose:** Group news articles into clusters based on similarity

**Process:**
1. **Load Data:** `data/processed/dataset.csv`
2. **Generate Embeddings:**
   - Uses `SentenceTransformer('all-mpnet-base-v2')`
   - Converts text to 768-dimensional vectors
   - Saves to `data/embeddings/embeddings_headings.npy`
3. **Dimensionality Reduction (UMAP):**
   - Reduces 768D → 10D (for clustering)
   - Creates 2D version (for visualization)
4. **K-Means Clustering:**
   - Finds optimal number of clusters (elbow method)
   - Assigns each article to a cluster
5. **Cluster Naming (KeyBERT):**
   - Extracts keywords from each cluster
   - Names clusters based on top keywords
6. **Output:** `data/results/labelled.csv` (articles with cluster labels)

### **HDBSCAN Clustering** (`models/clustering/HDBSCAN.ipynb`)

**Purpose:** Density-based clustering (finds clusters of varying densities)

**Process:**
1. **Load Data:** `data/processed/final_dataset_Preprocessed.csv`
2. **Generate Embeddings:** Similar to K-Means
3. **UMAP Reduction:** 10D for clustering, 2D for visualization
4. **HDBSCAN Clustering:**
   - Hyperparameter tuning (min_cluster_size)
   - Identifies outliers (label = -1)
   - Finds natural clusters
5. **Cluster Naming:** KeyBERT keyword extraction
6. **Output:** Clustered data with outlier detection

**Note:** Clustering is used for exploratory analysis and grouping similar news. The main classification for ministries uses the DistilBERT model (see below).

---

## 5️⃣ SENTIMENT ANALYSIS - Detecting Negative News

### **Method 1: RoBERTa (Primary - Used in API)**

**Location:** `server/api/views.py` → `predict_sentiment()`

**Technology:**
- **Model:** `cardiffnlp/twitter-roberta-base-sentiment` (PyTorch)
- **Output:** Probability scores [Positive, Negative, Neutral]

**How It Works:**
```python
def predict_sentiment(text):
    # 1. Tokenize text
    inp = sent_tok(text[:514], return_tensors='pt')
    
    # 2. Get model prediction
    out = sent_model(**inp)
    
    # 3. Convert to probabilities
    scores = torch.softmax(out.logits[0], dim=0)
    
    # 4. Return [positive, negative, neutral] scores
    return [scores[0], scores[1], scores[2]]
```

**Alert Trigger:**
- If `negative_score > 0.95` (95% negative) → Send email alert

### **Method 2: TextBlob (Alternative - Used in Notebook)**

**Location:** `models/sentiment_analysis/TextBlob_analysis.ipynb`

**Technology:**
- **Library:** TextBlob
- **Output:** Sentiment polarity (-1 to +1) and class (positive/negative/neutral)

**How It Works:**
```python
from textblob import TextBlob

analysis = TextBlob(text)
sentiment_score = analysis.sentiment.polarity

if sentiment_score > 0:
    sentiment_class = "positive"
elif sentiment_score < 0:
    sentiment_class = "negative"
else:
    sentiment_class = "neutral"
```

**Output:** `data/results/news_data_with_sentiment_output_file.csv`

**Note:** The API uses RoBERTa (more accurate). TextBlob is used in notebooks for quick analysis.

---

## 6️⃣ MINISTRY CLASSIFICATION - Segregating by Government Department

**Location:** `server/api/views.py` → `predict_category()`

**Technology:**
- **Model:** Fine-tuned DistilBERT (TensorFlow)
- **Model File:** `distilbert_model.h5`
- **Accuracy:** 83.2%

**How It Works:**

1. **Text Preprocessing:**
   ```python
   clean = preprocess(raw_text)  # Lowercase, lemmatize, remove stopwords
   ```

2. **Category Prediction:**
   ```python
   def predict_category(text):
       # Tokenize text
       inp = cls_tok(text, return_tensors='tf', max_length=512)
       
       # Get model prediction
       preds = cls_model.predict([inp['input_ids'], inp['attention_mask']])
       
       # Return category ID (0-9)
       return int(preds.argmax())
   ```

3. **Category to Ministry Mapping:**
   ```python
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
   
   DEPARTMENT_MAPPING = {
       0: {'name': 'Ministry of Information & Broadcasting', 'emails': [...]},
       1: {'name': 'Ministry of Finance / DPIIT', 'emails': [...]},
       2: {'name': "Prime Minister's Office", 'emails': [...]},
       3: {'name': 'Ministry of Law & Justice', 'emails': [...]},
       4: {'name': 'Ministry of Home Affairs', 'emails': [...]},
       5: {'name': 'Ministry of Culture', 'emails': [...]},
       6: {'name': 'Ministry of Youth Affairs and Sports', 'emails': [...]},
       7: {'name': 'Department of Science & Technology (DST)', 'emails': [...]},
       8: {'name': 'Ministry of External Affairs (MEA)', 'emails': [...]},
       9: {'name': 'Ministry of Electronics and IT (MeitY)', 'emails': [...]}
   }
   ```

4. **Frontend Display:**
   - Categories shown as ministry names (e.g., "Information and Broadcasting" instead of "Entertainment")
   - Users can filter news by ministry

**Example Flow:**
```
Article: "Stock market crashes due to inflation"
    ↓
Category Prediction: 1 (Business)
    ↓
Ministry Mapping: "Ministry of Finance / DPIIT"
    ↓
Sentiment: [0.1, 0.92, 0.08] (92% negative)
    ↓
Alert: Email sent to fm@gov.in, dpiit@gov.in
```

---

## 7️⃣ EMAIL ALERT SYSTEM - Notifying Authorities

**Location:** `server/api/views.py` → `send_email()` and `_process_news_data()`

**Technology:**
- **SMTP:** Gmail SMTP (smtplib)
- **Trigger:** Negative sentiment > 95%

**How It Works:**

1. **During News Processing:**
   ```python
   for article in articles:
       sentiment = predict_sentiment(article_text)
       
       if sentiment[1] > 0.95:  # Negative > 95%
           # Get ministry email from DEPARTMENT_MAPPING
           dept = DEPARTMENT_MAPPING[category_id]
           
           # Send email alert
           send_email(
               to_emails=dept['emails'],
               subject=f"Negative News Alert: {article_title}",
               body=email_content
           )
   ```

2. **Email Content:**
   - Article headline
   - Article URL
   - Category classification
   - Sentiment scores (Positive, Negative, Neutral %)
   - Published date
   - News source
   - Article description (first 1000 characters)

3. **Configuration:**
   ```python
   EMAIL_CONFIG = {
       'sender_email': 'putyourmail@gmail.com',
       'sender_password': 'bhsq enex bzah rouw',
       'smtp_server': 'smtp.gmail.com',
       'smtp_port': 587
   }
   ```

**Email Recipients by Category:**
- Entertainment → info@mib.gov.in
- Business → fm@gov.in, dpiit@gov.in
- Politics → connect.pmo@gov.in
- Crime → jscpg-mha@gov.in, mha.web@gov.in
- And so on...

---

## 8️⃣ FRONTEND DISPLAY - Web Interface

**Technology Stack:**
- **Framework:** Next.js (React)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **Backend API:** Django REST Framework

### **Frontend Components:**

1. **Header** (`client/src/components/header.tsx`):
   - Language toggle (English/Hindi)
   - Logo and navigation

2. **Category Navigation** (`client/src/components/CategoryNav.tsx`):
   - Displays all 10 ministries
   - Click to filter news by ministry
   - Fetches from: `GET /api/categories/`

3. **Latest Posts** (`client/src/components/latestPosts.tsx`):
   - Main news feed
   - Shows article cards with:
     - Title (English/Hindi)
     - Image
     - Category (Ministry name)
     - Sentiment scores
     - Emotion
     - Description
   - Fetches from: `GET /api/news/` or `POST /api/news/filter/`

4. **News Cards** (`client/src/components/NewsCard.tsx`):
   - Displays news grouped by category
   - Shows 6 articles per category

5. **Image Gallery** (`client/src/components/ImageGallery.tsx`):
   - Static image carousel

### **API Endpoints (Backend):**

1. **GET `/api/health/`**
   - Health check

2. **GET `/api/categories/`**
   - Returns list of all categories with ministry names
   ```json
   {
     "result": "success",
     "categories": [
       {
         "id": 0,
         "name": "Entertainment",
         "frontend_name": "Information and Broadcasting"
       },
       ...
     ]
   }
   ```

3. **GET `/api/news/?language=en`**
   - Returns all news articles
   - Optional `language` parameter (en/hi)

4. **POST `/api/news/filter/`**
   - Filters news by category and language
   ```json
   {
     "category": "Information and Broadcasting",
     "language": "en"
   }
   ```

### **Data Flow (Frontend → Backend):**

```
User clicks category
    ↓
Frontend: POST /api/news/filter/ {category: "Information and Broadcasting"}
    ↓
Backend: _process_news_data()
    ↓
    1. fetch_and_process() → RSS feeds → data/rss/RSS_FullText.xlsx
    2. For each article:
       - preprocess() → Clean text
       - predict_category() → Ministry classification
       - predict_sentiment() → Sentiment scores
       - predict_emotion() → Emotion detection
       - translate_text() → Hindi translation (if needed)
    3. Check for negative news → Send email alerts
    ↓
Backend: Returns JSON with news articles
    ↓
Frontend: Displays news cards
```

### **Language Support:**

- **English:** Default language
- **Hindi:** Automatic translation using Google Translate API
  - Translates: Title, Description
  - Uses `deep-translator` library
  - Cached for performance

---

## 9️⃣ COMPLETE END-TO-END WORKFLOW

### **Scenario: User Views News on Frontend**

1. **User opens website** → `http://localhost:3000`

2. **Frontend loads:**
   - Fetches categories: `GET /api/categories/`
   - Fetches all news: `GET /api/news/?language=en`

3. **Backend processes request:**
   - Calls `_process_news_data('en')`
   - Triggers `fetch_and_process()` in background thread
   - Fetches RSS feeds (News18, TheHindu, TOI)
   - Extracts full article text using newspaper3k
   - Saves to `data/rss/RSS_FullText.xlsx`

4. **For each article:**
   ```
   Raw Article Text
       ↓
   preprocess() → Clean text
       ↓
   predict_category() → Category ID (0-9)
       ↓
   predict_sentiment() → [positive, negative, neutral] scores
       ↓
   predict_emotion() → Emotion label
       ↓
   DEPARTMENT_MAPPING → Ministry name
       ↓
   Check: negative_score > 0.95?
       YES → send_email() to ministry
       NO → Continue
       ↓
   translate_text() → Hindi (if language='hi')
       ↓
   Add to news list
   ```

5. **Backend returns JSON:**
   ```json
   {
     "result": "success",
     "news": [
       {
         "Source": "News18_Latest",
         "Title": "Stock market crashes",
         "Category": "Business",
         "Department": "Ministry of Finance / DPIIT",
         "Sentiment": [0.1, 0.92, 0.08],
         "Emotion": "sadness",
         "ImageURL": "...",
         ...
       },
       ...
     ]
   }
   ```

6. **Frontend displays:**
   - News cards with images, titles, categories
   - Filtered by selected ministry (if any)
   - Language toggle (English/Hindi)

### **Scenario: Negative News Detected**

1. **Article processed:**
   - Sentiment: [0.05, 0.96, 0.01] (96% negative)
   - Category: 4 (Crime)
   - Ministry: "Ministry of Home Affairs"

2. **Email alert triggered:**
   ```
   To: jscpg-mha@gov.in, mha.web@gov.in
   Subject: Negative News Alert: Crime rate increases in Delhi
   Body:
   - Article: "Crime rate increases in Delhi"
   - URL: https://...
   - Category: Crime
   - Sentiment: Positive=5%, Negative=96%, Neutral=1%
   - Published: 2025-01-15
   - Source: News18_Latest
   - Description: [First 1000 chars of article]
   ```

3. **Email sent via Gmail SMTP**

---

## 🔟 TECHNOLOGIES USED - Complete Stack

### **Data Collection:**
- `feedparser` - RSS feed parsing
- `newspaper3k` - Article extraction
- `BeautifulSoup` - HTML parsing (legacy scrapers)
- `requests` - HTTP requests

### **Data Processing:**
- `pandas` - Data manipulation
- `numpy` - Numerical operations
- `xlsxwriter` - Excel file creation

### **NLP & ML:**
- `spacy` - Text preprocessing, lemmatization
- `nltk` - Stopword removal
- `transformers` - Hugging Face models
- `torch` (PyTorch) - RoBERTa sentiment model
- `tensorflow` - DistilBERT classification model
- `sentence-transformers` - Embedding generation
- `umap-learn` - Dimensionality reduction
- `hdbscan` - Density-based clustering
- `scikit-learn` - K-Means clustering
- `keybert` - Keyword extraction
- `textblob` - Alternative sentiment analysis

### **Translation:**
- `deep-translator` - Google Translate API

### **Backend:**
- `Django` - Web framework
- `Django REST Framework` - API endpoints

### **Frontend:**
- `Next.js` - React framework
- `TypeScript` - Type-safe JavaScript
- `Tailwind CSS` - Styling

### **Email:**
- `smtplib` - SMTP email sending

---

## 📝 SUMMARY

### **Data Sources:**
1. **RSS Feeds** (Primary): News18, TheHindu, TOI (4 sources)
2. **Web Crawlers** (Secondary): News18, IndiaToday, AajTak, IndiaTV, Hindustan Times, Jagran, Bhaskar, Tribune, and regional variants (10+ sources)
3. **Both run simultaneously** and data is merged into a single dataset

### **Data Storage:**
- `data/rss/` - RSS feed data + processed results (ACTIVE)
- `data/raw/` - Crawler outputs (temporary, merged into RSS)
- `data1/archive_*/` - Archived historical data (automatic)

### **Processing Pipeline:**
```
Archive Old Data → RSS + Crawlers → Merge → Preprocessing → Classification → Sentiment → Email Alert
     (data1/)         (data/raw/)    (RSS_FullText.xlsx)                          ↓
                                                                          Frontend Display
                                                                          (RSS_Processed.xlsx)
```

### **JSON Sanitization:**
- **Automatic NaN/INF handling**: All sentiment scores and numeric values are sanitized
- **JSON-safe responses**: All API responses are validated for JSON compatibility
- **Frontend compatibility**: No parsing errors due to invalid values

### **Key Features:**
1. ✅ Automated news collection (RSS feeds)
2. ✅ Ministry classification (DistilBERT, 83.2% accuracy)
3. ✅ Sentiment analysis (RoBERTa)
4. ✅ Automatic email alerts (negative news > 95%)
5. ✅ Web interface (Next.js frontend)
6. ✅ Multilingual support (English/Hindi)
7. ✅ Category filtering by ministry

### **Ministry Segregation:**
- 10 categories mapped to 10 government ministries
- Automatic routing of negative news to relevant ministry emails
- Frontend displays news grouped by ministry

---

## 🚀 How to Run

1. **Backend (Django):**
   ```bash
   cd server
   python manage.py runserver
   ```

2. **Frontend (Next.js):**
   ```bash
   cd client
   npm install
   npm run dev
   ```

3. **Access:**
   - Frontend: `http://localhost:3000`
   - Backend API: `http://127.0.0.1:8000`

---

**This is a complete, production-ready news intelligence system for government ministries!** 🎉

