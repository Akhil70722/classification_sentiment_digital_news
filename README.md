# 📡 News Intelligence & Alert System

> **📖 Setup Instructions:** See [SETUP.md](./SETUP.md) for detailed installation and configuration guide.

## 📌 Objective
This project is an end-to-end automated pipeline that:
- Extracts live digital news from major Indian news portals.
- Classifies news articles into relevant government ministries.
- Performs sentiment analysis to identify negative news.
- Sends real-time email alerts to the appropriate authorities.
- Provides a modern web-based interface for exploration and feedback.

## 🗞️ Data Collection
### 🔍 Dual Method: RSS Feeds + Web Crawlers
The project uses **both RSS feeds and web crawlers simultaneously** for comprehensive data collection:

#### 📡 RSS Feeds (Primary Method)
- ✅ **Legal & Compliant**: RSS feeds are officially provided by news websites
- ✅ **Reliable**: No blocking or bot detection issues
- ✅ **Fast**: Instant parsing without browser automation
- ✅ **Stable**: Standardized format that rarely changes

**RSS Feed Sources:**
- **News18 Latest**: Latest news feed
- **News18 India**: India-specific news
- **The Hindu**: National news
- **Times of India (TOI)**: Top stories

#### 🕷️ Web Crawlers (Secondary Method)
- **10+ News Sources**: News18, IndiaToday, AajTak, IndiaTV, Hindustan Times, Jagran, Bhaskar, Tribune, and more
- **Regional Coverage**: Includes Punjab/Chandigarh-specific news sources
- **Robust Selectors**: Multiple fallback HTML selectors for reliable extraction
- **Content Validation**: Ensures only valid articles are scraped

### 🛠️ Data Collection Tools:
- **feedparser**: For parsing RSS feed XML data
- **newspaper3k**: For extracting full article text from URLs
- **BeautifulSoup**: For web scraping and HTML parsing
- **requests**: For HTTP requests to news websites
- **Threading**: For concurrent processing of RSS feeds and crawlers
- **Timeout Protection**: Prevents crawlers from hanging indefinitely

> **Note**: Both RSS feeds and crawlers run simultaneously (not as fallback). Data from both sources is merged into a single dataset for analysis.

### 📄 Data Fields Extracted:
- Headline
- Full article text (extracted automatically by newspaper3k)
- Publish date
- News source
- Article image URL

## 🧾 Dataset Description
- Language: Primarily English, with optional Hindi translation support using Google Translate API.
- Format: Text-based articles extracted from RSS feeds.
- Processing: Real-time RSS feed parsing → Full article extraction using newspaper3k → NLP analysis.

## ⚙️ Description of Work Done
The full pipeline includes:
- **RSS Feed Processing** using feedparser (primary data collection method)
- **Article Extraction** using newspaper3k (automatically downloads and parses full article text from RSS feed URLs)
- **Text Preprocessing** using SpaCy, NLTK, contractions library
- **Category Classification** using fine-tuned DistilBERT model
- **Sentiment Analysis** with RoBERTa (CardiffNLP twitter-roberta-base-sentiment)
- **Emotion Detection** using DistilBERT-based emotion classifier
- **Multilingual Support** using deep-translator (Google Translate) for Hindi translation
- **Frontend** using Next.js + React + TypeScript + Tailwind CSS
- **Backend** using Django REST Framework with class-based views
- **Alert System** using Gmail SMTP for negative news notifications

## 🧹 Data Preprocessing
- Lowercasing
- Contraction expansion (e.g., "don't" → "do not")
- Removing punctuation, numbers, special characters
- Stopword removal (NLTK, excluding 'not' to preserve negative sentiment)
- Tokenization & Lemmatization using SpaCy (en_core_web_sm)
- Missing data handling:
  - Skipped empty articles
  - Fallback to RSS description if article extraction fails

## 🧠 Technologies & Tools Implemented

| Task                | Tools & Techniques                |
|---------------------|-----------------------------------|
| RSS Feed Parsing    | feedparser                        |
| Article Extraction  | newspaper3k (with BeautifulSoup internally) |
| Text Preprocessing  | SpaCy, NLTK, contractions         |
| Category Classification | DistilBERT (Fine-tuned TensorFlow model) |
| Sentiment Analysis  | RoBERTa (twitter-roberta-base-sentiment) |
| Emotion Detection   | DistilBERT-based emotion classifier |
| Translation         | deep-translator (Google Translate) |
| Email Alerts        | Gmail SMTP (smtplib)              |
| Data Storage        | Excel files (xlsxwriter, pandas) |
| Frontend Development| Next.js + React + TypeScript + Tailwind CSS |
| Backend API         | Django REST Framework (Class-based views) |

## 🎯 Model Training

### Ministry Classification:
- **Model:** Fine-tuned DistilBERT
- **Labels:** 10 Government Ministries

#### Training:
- Epochs: 4
- Batch Size: 32
- Optimizer: AdamW
- Loss: Cross-Entropy

#### Evaluation:

| Metric    | Score |
|-----------|-------|
| Accuracy  | 83.2% |
| Precision | 0.81  |
| Recall    | 0.76  |
| F1-Score  | 0.79  |

## 😡 Sentiment Analysis

- **Model:** RoBERTa (CardiffNLP twitter-roberta-base-sentiment) - PyTorch-based
- **Output:** Probability scores for [Positive, Negative, Neutral]
- **Alert Trigger:** Negative sentiment > 95% → Automatic email alert to relevant government department

## 📧 Alert System

### Workflow:
RSS Feed → Article Extraction → Classification → Sentiment Analysis → Email Alert (if negative > 95%)

### Email Technology:
Gmail SMTP (Python smtplib)

### Email Content:
- Article headline
- Article URL
- Category classification
- Sentiment scores (Positive, Negative, Neutral percentages)
- Published date
- News source
- Article description (first 1000 characters)

### Department Mapping:
- **Entertainment** → Ministry of Information & Broadcasting
- **Business** → Ministry of Finance / DPIIT
- **Politics** → Prime Minister's Office
- **Judiciary** → Ministry of Law & Justice
- **Crime** → Ministry of Home Affairs
- **Culture** → Ministry of Culture
- **Sports** → Ministry of Youth Affairs and Sports
- **Science** → Department of Science & Technology
- **International** → Ministry of External Affairs
- **Technology** → Ministry of Electronics and IT (MeitY)

## 🌐 Web Interface

### Frontend (Next.js + React + TypeScript):
- **Latest Posts**: Dynamic news feed with real-time updates
- **Category Navigation**: Filter news by government departments
- **Language Toggle**: Switch between English and Hindi (with automatic translation)
- **News Cards**: Display article title, image, category, sentiment, and emotion
- **Responsive Design**: Modern UI with Tailwind CSS
- **Image Gallery**: Static image carousel

### Backend API (Django REST Framework):
- **GET `/api/health/`**: Health check endpoint
- **GET `/api/categories/`**: List all available news categories
- **GET `/api/news/`**: Fetch all news articles (with optional language parameter)
- **POST `/api/news/filter/`**: Filter news by category and language
- **Class-Based Views**: RESTful API design following Python best practices

## 🖼️ Screenshots

### Dashboard Example:
![Dashboard Screenshot 1](./dashboard1.jpg)

![Dashboard Screenshot 2](./dashboard2.jpg)

### Email Alert Example:
![Email Screenshot 1](./email1.jpg)

![Email Screenshot 2](./email2.jpg)

## 📁 Data Storage & Archiving

### Folder Structure:
```
server/
├── data/                    ← ACTIVE (new data always goes here)
│   ├── raw/                 ← Crawler outputs (temporary)
│   │   ├── News18.xlsx
│   │   ├── IndiaToday.xlsx
│   │   └── ...
│   └── rss/                 ← RSS & processed data (permanent)
│       ├── RSS_FullText.xlsx   ← Merged data from RSS + crawlers
│       └── RSS_Processed.xlsx  ← Sentiment analysis results
│
└── data1/                   ← ARCHIVE (old data preserved here)
    └── archive_YYYYMMDD_HHMMSS/
        ├── raw/
        └── rss/
```

### Automatic Data Archiving:
- **Old data preservation**: Every API run automatically archives old data to `data1/archive_TIMESTAMP/`
- **Fresh start**: `data/` folder is cleaned before new data collection
- **No data loss**: All historical data is preserved with timestamps
- **Automatic**: No manual intervention needed

### Data Flow:
1. **Archive**: Old `data/` → `data1/archive_TIMESTAMP/`
2. **Collect**: RSS feeds + Crawlers → `data/rss/RSS_FullText.xlsx`
3. **Analyze**: Sentiment analysis → `data/rss/RSS_Processed.xlsx`
4. **Display**: Frontend reads from API (which reads from `RSS_Processed.xlsx`)

## 📊 System Performance

| Parameter              | Value         |
|------------------------|---------------|
| Classification Model   | DistilBERT (Fine-tuned) |
| Sentiment Model        | RoBERTa (CardiffNLP) |
| Emotion Detection      | DistilBERT-based emotion classifier |
| Article Extraction     | newspaper3k (automatic) |
| Translation Support    | Google Translate API (Hindi) |
| Email Delivery Time    | < 5 seconds   |
| Data Collection        | Real-time (RSS + Crawlers on API request) |
| Data Storage           | Excel files (RSS_FullText.xlsx, RSS_Processed.xlsx) |
| Data Archiving         | Automatic (timestamped archives in data1/) |
| JSON Sanitization      | Automatic (NaN/INF handling) |

## ✅ Results & Discussions
- **Dual Data Collection**: RSS feeds + Web crawlers working simultaneously for comprehensive coverage
- **Automated RSS Feed Processing**: Real-time news extraction from major Indian news portals using official RSS feeds
- **Web Crawler Integration**: 10+ news sources with robust HTML selectors and content validation
- **Full Article Extraction**: Using newspaper3k to get complete article text (not just RSS summaries)
- **Automatic Data Archiving**: Old data preserved in timestamped archives, fresh data collection every run
- **JSON Sanitization**: Automatic handling of NaN/INF values for frontend compatibility
- **ML-Powered Analysis**: Category classification, sentiment analysis, and emotion detection
- **Multilingual Support**: Hindi translation for broader accessibility
- **Alert System**: Automated email notifications to relevant government departments for negative news
- **Modern Web Interface**: Responsive Next.js frontend with real-time data updates
- **RESTful API**: Clean, class-based Django REST Framework endpoints with error handling

## 🚀 Future Enhancements
- Database integration (PostgreSQL/MySQL) for persistent data storage
- Scheduled RSS feed processing (cron jobs / Celery)
- More RSS feed sources (Indian Express, Zee News, Aaj Tak, etc.)
- Social media integration (Twitter, Facebook) via official APIs
- Weekly insight reports for policy-makers
- Fake news detection module
- Android/iOS app for field use
- Enhanced multilingual support (Hinglish, regional languages)
- Caching mechanism for faster API responses
- RSS feed health monitoring and automatic failover
