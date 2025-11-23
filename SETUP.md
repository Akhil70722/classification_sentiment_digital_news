# 🚀 Setup Guide - News Intelligence & Alert System

This guide will help you set up the project from scratch after cloning from GitHub.

## ⚠️ Prerequisites

- **Python 3.10+** (3.10.11 recommended)
- **Node.js 16+** (for frontend)
- **Git** (for cloning)
- **Internet connection** (for downloading models and dependencies)

---

## 📋 Step-by-Step Setup

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd sentiment-analysis
```

### 2. Backend Setup (Django)

#### 2.1 Create Virtual Environment

**Windows:**
```powershell
cd server
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
cd server
python3 -m venv .venv
source .venv/bin/activate
```

#### 2.2 Install Dependencies

```bash
pip install --upgrade pip
pip install -r ../requirements.txt
```

**Note:** This will take 10-15 minutes as it downloads:
- TensorFlow (~500MB)
- PyTorch (~1GB)
- Transformers models
- Other ML libraries

#### 2.3 Download NLTK Data

```python
python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt')"
```

#### 2.4 Verify Spacy Model

The `en_core_web_sm` model should be installed automatically via requirements.txt. If not:

```bash
python -m spacy download en_core_web_sm
```

#### 2.5 Download ML Models (Automatic)

The models will be downloaded automatically on first run:
- **Sentiment Model**: `cardiffnlp/twitter-roberta-base-sentiment` (downloaded from HuggingFace)
- **Emotion Model**: `bhadresh-savani/distilbert-base-uncased-emotion` (downloaded from HuggingFace)

#### 2.6 Download Category Model (Manual - if needed)

If `distilbert_model.h5` is missing, you have two options:

**Option A:** Train it yourself (if you have training data):
```bash
cd server
python train_distilbert.py
```

**Option B:** Download from a shared location (if available):
- Place `distilbert_model.h5` in the `server/` directory

**Note:** The app will work without this model, but category classification will use a fallback.

#### 2.7 Configure Email Settings

Edit `server/api/views.py` (lines 560-564):

```python
EMAIL_CONFIG = {
    'sender_email': 'your-email@gmail.com',  # Your Gmail address
    'sender_password': 'your-app-password',  # Gmail App Password (not regular password)
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587
}
```

**To get Gmail App Password:**
1. Enable 2-Factor Authentication on your Google account
2. Go to: https://myaccount.google.com/apppasswords
3. Generate an app password for "Mail"
4. Use that 16-character password

#### 2.8 Run Database Migrations (Optional)

```bash
cd server
python manage.py migrate
```

#### 2.9 Start Django Server

**Windows:**
```powershell
cd server
.\run_server.ps1
# OR
.venv\Scripts\python.exe manage.py runserver
```

**Linux/Mac:**
```bash
cd server
source .venv/bin/activate
python manage.py runserver
```

Server will start at: `http://127.0.0.1:8000/`

---

### 3. Frontend Setup (Next.js)

#### 3.1 Install Dependencies

```bash
cd client
npm install
# OR
yarn install
```

#### 3.2 Start Development Server

```bash
npm run dev
# OR
yarn dev
```

Frontend will start at: `http://localhost:3000/`

---

## ✅ Verification Checklist

After setup, verify:

- [ ] Backend server runs without errors
- [ ] Frontend connects to backend API
- [ ] Models download successfully (check console logs)
- [ ] Email configuration is set (if using email alerts)
- [ ] RSS feeds are accessible
- [ ] No import errors in console

---

## 🔧 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'X'"

**Solution:** Make sure virtual environment is activated and run:
```bash
pip install -r requirements.txt
```

### Issue: "distilbert_model.h5 not found"

**Solution:** The app will work with a fallback. For full functionality, train or download the model.

### Issue: "Spacy model not found"

**Solution:**
```bash
python -m spacy download en_core_web_sm
```

### Issue: "NLTK data not found"

**Solution:**
```python
python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt')"
```

### Issue: "Email sending fails"

**Solution:**
- Check Gmail App Password is correct
- Ensure 2FA is enabled on Gmail account
- Verify SMTP settings

### Issue: "Models download slowly"

**Solution:** This is normal on first run. Models are cached, so subsequent runs are faster.

### Issue: "JSON parsing error: NaN values"

**Solution:** This has been fixed. The system now automatically sanitizes all NaN/INF values before sending JSON responses. If you still see this error, restart the server to load the latest code.

### Issue: "Data folder keeps growing"

**Solution:** This is normal. The system automatically archives old data to `data1/archive_TIMESTAMP/` before each run. Old data is preserved but not used for new analysis.

---

## 📁 Important Files to Check

### Must be in Repository:
- ✅ `requirements.txt` - Python dependencies
- ✅ `server/tokenizer_roberta/` - Tokenizer files
- ✅ `server/api/views.py` - Main application code
- ✅ `client/package.json` - Frontend dependencies

### Optional (may be large):
- ⚠️ `server/distilbert_model.h5` - Category classification model (~500MB)
- ⚠️ Model cache files (auto-downloaded)

### Should NOT be in Repository:
- ❌ `.venv/` - Virtual environment
- ❌ `node_modules/` - Frontend dependencies
- ❌ `db.sqlite3` - Database (if containing sensitive data)
- ❌ `.env` - Environment variables with secrets

---

## 🔐 Security Notes

### Before Pushing to GitHub:

1. **Change Email Credentials:**
   - Edit `server/api/views.py` line 561-562
   - Replace with placeholder: `'putyourmail@gmail.com'`
   - Add instructions for users to configure their own

2. **Change Django Secret Key:**
   - Edit `server/sih/settings.py` line 23
   - Generate new key: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`

3. **Use Environment Variables (Recommended):**
   - Create `.env.example` file
   - Use `python-decouple` or `django-environ` package
   - Never commit `.env` file

---

## 🎯 Quick Start (After 1 Month)

If you've already set this up before:

1. **Pull latest changes:**
   ```bash
   git pull origin main
   ```

2. **Update dependencies:**
   ```bash
   cd server
   .venv\Scripts\Activate.ps1  # Windows
   pip install -r ../requirements.txt --upgrade
   
   cd ../client
   npm install  # or yarn install
   ```

3. **Verify models are cached:**
   - Check `~/.cache/huggingface/` for cached models
   - Models should auto-load if cached

4. **Start servers:**
   ```bash
   # Terminal 1 - Backend
   cd server
   python manage.py runserver
   
   # Terminal 2 - Frontend
   cd client
   npm run dev
   ```

---

## 📝 Notes

- **First run will be slow** (downloading models ~5-10 minutes)
- **Subsequent runs are fast** (models are cached)
- **Internet required** for:
  - RSS feed fetching
  - Model downloads (first time)
  - Email sending
- **Large disk space needed** (~3-5GB for all dependencies and models)

---

## 🆘 Still Having Issues?

1. Check Python version: `python --version` (should be 3.10+)
2. Check Node version: `node --version` (should be 16+)
3. Verify all dependencies installed: `pip list`
4. Check server logs for specific error messages
5. Ensure ports 8000 (backend) and 3000 (frontend) are available

---

**Last Updated:** November 2025

