# 🎯 Smart Goal Tracker with Notion

> AI-powered goal scheduling that automatically syncs with your Notion workspace

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![Notion](https://img.shields.io/badge/Notion-API-black.svg)](https://notion.so)

---

## ⚡ Quick Start

```bash
# Clone & setup
git clone https://github.com/JanaSamiAlsuhaibanai/SMART-GOAL-TRACKER-with-NOTION.git
cd SMART-GOAL-TRACKER-with-NOTION
pip install -r requirements.txt

# Configure (copy .env.example to .env and add your keys)
cp .env.example .env

# Run
streamlit run app.py
```

---

## 🌟 Features

- **🤖 AI Scheduling** - Cohere AI suggests optimal times based on your routine
- **📊 Visual Schedule** - See your day with interactive time blocks
- **🔄 Notion Sync** - Auto-creates tasks in your Notion database
- **⚙️ Customizable** - Set sleep, work hours, and energy patterns

---

## 🔧 Setup

### 1. Get API Keys

| Service | Link | Add to .env as |
|---------|------|----------------|
| Cohere | [dashboard.cohere.ai](https://dashboard.cohere.ai) | `COHERE_API_KEY` |
| Notion | [notion.so/my-integrations](https://notion.so/my-integrations) | `NOTION_TOKEN` |

### 2. Create Notion Database

1. Create a new database in Notion with these properties:

| Property | Type |
|----------|------|
| Name | Title |
| Suggested Time | Text |
| Duration | Number |
| Priority | Select (High/Medium/Low) |
| Status | Select (Not Started/In Progress/Done) |
| Category | Select (Work/Personal/Learning/Health) |

2. Share database with your integration
3. Copy database ID from URL → add to `.env` as `NOTION_DATABASE_ID`

---

## 📖 Usage

```python
# 1. Set your routine (first time)
Wake: 7:00 AM | Sleep: 11:00 PM | Work: 9-5 | Energy: Morning

# 2. Add a goal
Goal: "Study Arabic NLP"
Duration: 2 hours
Category: Learning

# 3. Get AI suggestions
✅ 7:30-9:30 AM (Peak energy, before work) - 95% score
⭐ 8:00-10:00 PM (Quiet time) - 75% score

# 4. Click "Add to Notion" → Done!
```

---

##  How It Works

```
User Input → AI Analysis (Cohere) → Time Suggestions → Notion Sync
```

**Tech Stack:** Streamlit + Cohere AI + Notion API + Python

---

##  Requirements

```txt
streamlit==1.28.0
cohere==4.37
notion-client==2.2.1
python-dotenv==1.0.0
pandas==2.1.0
plotly==5.17.0
```

---


**Made with ❤️ for productivity**


