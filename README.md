# 🎓 GapMentorAI - AI-Powered Learning Gap Identifier

An intelligent study companion that identifies learning gaps through AI-generated tests and provides personalized study plans.

## 🌟 Features

- **AI-Powered Tests**: Generate custom tests on any topic with adjustable difficulty
- **Learning Gap Analysis**: Automatically identify weak areas
- **Personalized Study Plans**: AI creates tailored study schedules
- **Interactive Chat Mentor**: Get instant help with difficult concepts
- **Progress Tracking**: Visualize your learning journey
- **Smart Notifications**: Stay on track with timely reminders

## 🚀 Quick Start

1. **Clone the repository**
```bash
   git clone https://github.com/yourusername/GapMentorAI.git
   cd GapMentorAI
```

2. **Create virtual environment**
```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
   pip install -r requirements.txt
```

4. **Set up API key**
   Create `.streamlit/secrets.toml`:
```toml
   GEMINI_API_KEY = "your-api-key-here"
```

5. **Run the app**
```bash
   streamlit run app.py
```

## 📂 Project Structure
```
GapMentorAI/
├── .venv/                      # Virtual environment
├── pages/                      # Streamlit pages
│   ├── Login_Signup.py
│   ├── Home.py
│   ├── Test.py
│   ├── Chat.py
│   ├── Progress.py
│   ├── Notification.py
│   ├── StudyPlan.py
│   └── User_Profile.py
├── utils/                      # Utility modules
│   ├── __init__.py
│   ├── database.py
│   ├── auth.py
│   ├── test_generator.py
│   ├── chat_analyser.py
│   └── studyPlan_generator.py
├── app.py                      # Main entry point
├── requirements.txt            # Dependencies
├── .gitignore
├── README.md
└── gapMentorAI.db             # SQLite database
```

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **AI**: Google Gemini API
- **Database**: SQLite
- **Auth**: bcrypt
- **Visualization**: Plotly

## 📊 Database Schema

- **users**: User accounts and profiles
- **tests**: Test records and scores
- **questions**: Individual questions and answers
- **gaps**: Identified learning gaps
- **study_plans**: Generated study plans
- **chat_sessions**: Chat history
- **notifications**: User notifications

## 🎯 Key Features

### Test Generation
- Case-insensitive topic matching
- Difficulty levels: Easy, Medium, Hard
- Optional descriptive questions
- No duplicate questions

### Learning Analytics
- Performance tracking over time
- Topic-wise gap identification
- Progress visualization

### Study Plans
- AI-generated personalized plans
- Task management with priorities
- Calendar integration

## 🤝 Contributing

Contributions welcome! Please open an issue or submit a pull request.

## 📄 License

MIT License - feel free to use for your projects!

## 👥 Team

Created for AI Innovation Challenge 2026 | IBM SkillsBuild

---

**Happy Learning! 🚀**
