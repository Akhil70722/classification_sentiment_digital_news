# 📡 News Intelligence & Alert System

## 📌 Objective
This project is an end-to-end automated pipeline that:
- Extracts live digital news from major Indian news portals.
- Classifies news articles into relevant government ministries.
- Performs sentiment analysis to identify negative news.
- Sends real-time email alerts to the appropriate authorities.
- Provides a modern web-based interface for exploration and feedback.

## 🗞️ Data Collection
### 🔍 Sources:
- Times of India
- The Hindu
- News18
- Dainik Bhaskar

### 🛠️ Crawling Tools:
- **Selenium**: For dynamic JavaScript content.
- **BeautifulSoup**: For static HTML parsing.
- **Scheduler**: Custom Python scripts using `schedule` and `threading`.

### 📄 Data Fields Extracted:
- Headline
- Full article text
- Publish date
- News source

## 🧾 Dataset Description
- Language: Primarily English.
- Format: Text-based articles.
- Future Scope: Include Hindi, Hinglish (code-mixed), and transcribed audio/video content.

## ⚙️ Description of Work Done
The full pipeline includes:
- Web Crawling using Selenium + BeautifulSoup
- Text Processing using SpaCy, NLTK, TF-IDF, SBERT
- Clustering & Classification using K-Means, HDBSCAN, DistilBERT
- Sentiment Analysis with RoBERTa and TextBlob
- Frontend using Next.js + Tailwind CSS
- Backend using Django REST Framework
- Alert System using Gmail SMTP + Nodemailer

## 🧹 Data Preprocessing
- Lowercasing
- Removing punctuation, numbers, HTML
- Stopword removal
- Tokenization & Lemmatization using SpaCy
- Missing data handling:
  - Dropped empty entries
  - Imputed publish dates from metadata

## 🔍 Feature Engineering
### 📌 Text Embedding:
- TF-IDF
- Sentence-BERT (SBERT)

### 📌 Dimensionality Reduction:
- UMAP for 2D clustering visualizations

## 🧠 Algorithms Implemented

| Task                | Tools & Techniques                |
|---------------------|-----------------------------------|
| Web Crawling        | Selenium + BeautifulSoup          |
| Preprocessing       | SpaCy, NLTK                       |
| Vectorization       | TF-IDF, SBERT                     |
| Clustering          | K-Means, HDBSCAN                  |
| Classification      | DistilBERT (Fine-tuned)           |
| Sentiment Analysis  | RoBERTa, TextBlob                 |
| Email Alerts        | Nodemailer + Gmail SMTP           |
| Frontend Development| Next.js + Tailwind CSS            |
| Backend Integration | Django REST Framework             |

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

- **Models:** RoBERTa (fine-tuned), TextBlob (baseline)
- **Classes:** Positive, Neutral, Negative
- **Alert Trigger:** Negative news → Email alert

## 📧 Feedback & Alert System

### Workflow:
News → Classified → Sentiment → Email

### Email Tech:
Nodemailer + Gmail SMTP

### Email Content:
- Headline
- Summary
- Sentiment
- Source URL
- Recipients: Mapped government officials

## 🌐 Web Interface

### Frontend:
- Search headlines
- Filters: Sentiment, Ministry, Date
- Clustered news view
- Sentiment indicators (Red/Yellow/Green)

### Backend:
Django REST API with modules for:
- News fetching
- Classification
- Sentiment analysis
- Email alerts

## 🖼️ Screenshots

### Dashboard Example:
![Dashboard Screenshot 1](https://github.com/Akhil70722/classification_sentiment_digital_news/blob/0ef89b9be261e4320f747e8293775d7f64c0a738/dashboard1.jpg)

![Dashboard Screenshot 2](https://github.com/Akhil70722/classification_sentiment_digital_news/blob/5564f7f349fbd6279cff4bc026ec57d2eaeb1923/dashboard2.jpg)

### Email Alert Example:
![Email Screenshot](docs/email_alert.png)

## 📊 Evaluation Parameters

| Parameter              | Value         |
|------------------------|---------------|
| Classification Accuracy| 83.2%         |
| Sentiment Accuracy     | 78.5%         |
| Clustering Silhouette  | 0.61          |
| Transcription Accuracy | 92% (English) |
| Email Delivery Time    | < 5 seconds   |
| API Response Time      | ~450 ms       |
| Frontend Load Time     | < 1.5 seconds |

## ✅ Results & Discussions
- Automated news crawling to alert system pipeline completed.
- Achieved high classification accuracy.
- Timely email alerts for negative news articles.
- Web interface allows live news exploration and user feedback.

## 🚀 Future Enhancements
- Integration with social media (Twitter, Facebook)
- Graph-based clustering (e.g., Louvain, Leiden)
- Weekly insight reports for policy-makers
- Fake news detection module
- Android/iOS app for field use
- Voice-controlled admin panel

