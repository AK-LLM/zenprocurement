# AI Procurement MVP

This is your AI-driven procurement MVP built with Streamlit, Supabase, and Replicate.

## 🚀 **Setup Instructions**

### ✅ **1. Clone the repository**
```bash
git clone https://github.com/yourusername/your-repo.git
cd your-repo
```

### ✅ **2. Create and activate a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
```

### ✅ **3. Install dependencies**
```bash
pip install -r requirements.txt
```

### ✅ **4. Create your `.env` file**
Duplicate `.env.example` as `.env` and fill in:

- Your Supabase URL
- Supabase anon key
- Replicate API key

### ✅ **5. Run the app locally**
```bash
streamlit run app.py
```

---

## 📦 **Deployment to Streamlit Cloud**

1. Push project to GitHub
2. Go to Streamlit Cloud and create a new app
3. Set **main file path** to `app.py`
4. Set **Secrets** using values from your `.env`

---

## 🔑 **Environment Variables**

| Variable | Description |
|----------|-------------|
| SUPABASE_URL | Your Supabase project URL |
| SUPABASE_ANON_KEY | Your Supabase anon public key |
| REPLICATE_API_KEY | Your Replicate API key for image generation |

---

## 📝 **Modules Overview**

- **app.py** – Main Streamlit application
- **image_gen.py** – AI image generation using Replicate
- **quote.py** – PDF quote generation with ReportLab

---

## 📄
