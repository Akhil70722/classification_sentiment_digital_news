# 📡 News Intelligence & Alert System - API Documentation

## Base URL
```
http://127.0.0.1:8000
```

---

## 🏥 Health Check

### GET `/api/health/`

Check if the API is running and healthy.

**Response:**
```json
{
  "status": "healthy",
  "service": "News Intelligence & Alert System",
  "timestamp": "2025-11-04T23:00:00"
}
```

**Example:**
```bash
curl http://127.0.0.1:8000/api/health/
```

---

## 📂 Categories

### GET `/api/categories/`

Get list of all available news categories.

**Response:**
```json
{
  "result": "success",
  "categories": [
    {
      "id": 0,
      "name": "Entertainment",
      "frontend_name": "Information and Broadcasting"
    },
    {
      "id": 1,
      "name": "Business",
      "frontend_name": "Finance"
    },
    // ... more categories
  ],
  "total": 10
}
```

**Example:**
```bash
curl http://127.0.0.1:8000/api/categories/
```

---

## 📰 News Endpoints

### GET `/api/news/`

Fetch all news articles.

**Query Parameters:**
- `language` (optional): `en` or `hi` (default: `en`)

**Response:**
```json
{
  "result": "success",
  "news": [
    {
      "Source": "News18_Latest",
      "Title": "Article Title",
      "TitleHindi": "लेख का शीर्षक",
      "FullArticle": "Full article text...",
      "URL": "https://example.com/article",
      "Published": "2025-11-04",
      "Category": "Politics",
      "Sentiment": [0.7, 0.2, 0.1],
      "Emotion": "joy",
      "Department": "Prime Minister's Office",
      "ImageURL": "https://example.com/image.jpg",
      "DescriptionHindi": "लेख का विवरण"
    }
    // ... more news items
  ],
  "total": 50
}
```

**Examples:**
```bash
# Get all news in English
curl http://127.0.0.1:8000/api/news/

# Get all news in Hindi
curl http://127.0.0.1:8000/api/news/?language=hi
```

---

### POST `/api/news/filter/`

Filter news articles by category.

**Request Body:**
```json
{
  "category": "External Affairs",
  "language": "en"
}
```

**Category Mapping:**
- `External Affairs` → `International`
- `Law and Justice` → `Judiciary`
- `Youth Affairs and Sports` → `Sports`
- `Finance` → `Business`
- `Internal Security` → `Crime`
- `Culture` → `Culture`
- `Information and Broadcasting` → `Entertainment`
- `Home Affairs` → `Crime`
- `Science and Technology` → `Science`
- `Electronics and Information Technology` → `Technology`

**Response:**
```json
{
  "result": "success",
  "news": [
    // ... filtered news items
  ],
  "total": 50,
  "filtered": 5
}
```

**Example:**
```bash
curl -X POST http://127.0.0.1:8000/api/news/filter/ \
  -H "Content-Type: application/json" \
  -d '{"category": "External Affairs", "language": "en"}'
```

---

## 🔄 Legacy Endpoint (Backward Compatibility)

### GET `/` or POST `/`

The old endpoint still works for backward compatibility but is deprecated.

**GET `/`:**
- Same as `GET /api/news/`
- Supports `?language=hi` query parameter

**POST `/`:**
- Same as `POST /api/news/filter/`
- Accepts JSON body with `category` and `language`

---

## 📊 Response Format

All endpoints return JSON with the following structure:

**Success Response:**
```json
{
  "result": "success",
  "data": { ... },
  "message": "Optional message"
}
```

**Error Response:**
```json
{
  "result": "error",
  "message": "Error description",
  "news": []
}
```

---

## 🚨 Error Codes

- `400` - Bad Request (invalid JSON, missing parameters)
- `405` - Method Not Allowed (wrong HTTP method)
- `500` - Internal Server Error (server-side error)

---

## 📝 Notes

1. **First Request:** The first request may take 30-60 seconds as it processes RSS feeds and analyzes articles.

2. **Hindi Translation:** Requests with `language=hi` will take longer as articles are translated.

3. **Email Alerts:** Negative news articles (sentiment > 95%) automatically trigger email alerts to relevant government departments.

4. **Caching:** RSS feeds are fetched fresh on each request. Consider adding caching for production.

---

## 🔗 Frontend Integration

The frontend automatically uses these endpoints:

- **All News:** `GET /api/news/?language={lang}`
- **Filtered News:** `POST /api/news/filter/` with category filter

No changes needed in the frontend code - it's already updated!

---

## 🔧 Technical Details

### Data Archiving:
- Old data is automatically archived to `data1/archive_TIMESTAMP/` before each API call
- Fresh data is collected in `data/` folder
- No data loss - all historical data is preserved

### JSON Sanitization:
- All API responses are automatically sanitized for NaN/INF values
- Sentiment scores are validated before JSON serialization
- Frontend-compatible JSON format guaranteed

### Data Sources:
- **RSS Feeds**: News18, TheHindu, TOI (primary)
- **Web Crawlers**: 10+ news sources including regional (secondary)
- Both sources run simultaneously and are merged into a single dataset

---

**Last Updated:** November 2025

