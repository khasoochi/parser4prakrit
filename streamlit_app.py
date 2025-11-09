#!/usr/bin/env python3
"""
Prakrit Word Games - Streamlit Web Application
A unified web app for learning Prakrit through 5 integrated games.
"""

import streamlit as st
import os
import sys
from dotenv import load_dotenv

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.db_handler_web import PrakritDatabaseWeb
from core.script_converter import ScriptConverter

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="प्राकृत शब्द खेल - Prakrit Word Games",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better appearance
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .game-card {
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        margin: 1rem 0;
        background-color: #f8f9fa;
    }
    .correct-answer {
        color: #28a745;
        font-weight: bold;
        font-size: 1.2rem;
    }
    .incorrect-answer {
        color: #dc3545;
        font-weight: bold;
        font-size: 1.2rem;
    }
    .stats-box {
        padding: 1rem;
        background-color: #e3f2fd;
        border-radius: 8px;
        border-left: 4px solid #2196f3;
    }
    .question-text {
        font-size: 1.5rem;
        font-weight: 500;
        padding: 1rem;
        background-color: #fff3cd;
        border-radius: 8px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def init_database():
    """Initialize database connection (cached)."""
    db_url = os.getenv('DATABASE_URL')

    try:
        if db_url:
            db = PrakritDatabaseWeb(db_url=db_url)
        else:
            # Fallback to SQLite
            db = PrakritDatabaseWeb(use_sqlite=True)
        return db
    except Exception as e:
        st.error(f"Database initialization failed: {e}")
        return None


@st.cache_resource
def init_converter():
    """Initialize script converter (cached)."""
    return ScriptConverter()


def initialize_session_state():
    """Initialize session state variables."""
    if 'current_game' not in st.session_state:
        st.session_state.current_game = None
    if 'score' not in st.session_state:
        st.session_state.score = 0
    if 'streak' not in st.session_state:
        st.session_state.streak = 0
    if 'questions_answered' not in st.session_state:
        st.session_state.questions_answered = 0
    if 'correct_answers' not in st.session_state:
        st.session_state.correct_answers = 0
    if 'script_preference' not in st.session_state:
        st.session_state.script_preference = 'devanagari'
    if 'difficulty' not in st.session_state:
        st.session_state.difficulty = 'medium'
    if 'grammar_terminology' not in st.session_state:
        st.session_state.grammar_terminology = 'devanagari'


def sidebar_settings(converter):
    """Render sidebar with settings."""
    st.sidebar.markdown("### ⚙️ Settings")

    # Script preference
    script_options = {
        'Devanagari (देवनागरी)': 'devanagari',
        'IAST': 'iast',
        'ISO 15919': 'iso15919',
        'Harvard-Kyoto': 'hk'
    }

    selected_script = st.sidebar.selectbox(
        "📜 Script for Prakrit Text:",
        options=list(script_options.keys()),
        index=0
    )
    st.session_state.script_preference = script_options[selected_script]

    # Grammatical terminology
    term_options = {
        'Sanskrit (Devanagari)': 'devanagari',
        'Sanskrit (Roman)': 'iast',
        'English': 'english'
    }

    selected_term = st.sidebar.selectbox(
        "📖 Grammatical Terms:",
        options=list(term_options.keys()),
        index=0
    )
    st.session_state.grammar_terminology = term_options[selected_term]

    # Difficulty
    difficulty_map = {'Easy': 'easy', 'Medium': 'medium', 'Hard': 'hard'}
    selected_diff = st.sidebar.selectbox(
        "🎯 Difficulty:",
        options=list(difficulty_map.keys()),
        index=1
    )
    st.session_state.difficulty = difficulty_map[selected_diff]

    st.sidebar.markdown("---")

    # Statistics
    st.sidebar.markdown("### 📊 Statistics")

    if st.session_state.questions_answered > 0:
        accuracy = (st.session_state.correct_answers / st.session_state.questions_answered) * 100
    else:
        accuracy = 0

    st.sidebar.metric("Score", st.session_state.score)
    st.sidebar.metric("Streak", f"{st.session_state.streak} 🔥")
    st.sidebar.metric("Questions", st.session_state.questions_answered)
    st.sidebar.metric("Accuracy", f"{accuracy:.1f}%")

    st.sidebar.markdown("---")

    # Reset button
    if st.sidebar.button("🔄 Reset Progress"):
        st.session_state.score = 0
        st.session_state.streak = 0
        st.session_state.questions_answered = 0
        st.session_state.correct_answers = 0
        st.rerun()


def main():
    """Main application."""
    initialize_session_state()

    # Initialize components
    db = init_database()
    converter = init_converter()

    if db is None:
        st.error("Failed to initialize database. Please check configuration.")
        return

    # Header
    st.markdown('<div class="main-header">🎮 प्राकृत शब्द खेल<br>Prakrit Word Games</div>',
                unsafe_allow_html=True)

    # Sidebar
    sidebar_settings(converter)

    # Game selection
    st.markdown("### Select a Game:")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        if st.button("📝 Form Quiz", use_container_width=True):
            st.session_state.current_game = 'game1'

    with col2:
        if st.button("🔍 Word ID", use_container_width=True):
            st.session_state.current_game = 'game2'

    with col3:
        if st.button("📊 Paradigm", use_container_width=True):
            st.session_state.current_game = 'game3'

    with col4:
        if st.button("⚡ Speed Drill", use_container_width=True):
            st.session_state.current_game = 'game4'

    with col5:
        if st.button("🎯 Matching", use_container_width=True):
            st.session_state.current_game = 'game5'

    st.markdown("---")

    # Display selected game
    if st.session_state.current_game == 'game1':
        from web_games import game1_form_quiz
        game1_form_quiz.render(db, converter)

    elif st.session_state.current_game == 'game2':
        from web_games import game2_identification
        game2_identification.render(db, converter)

    elif st.session_state.current_game == 'game3':
        from web_games import game3_paradigm
        game3_paradigm.render(db, converter)

    elif st.session_state.current_game == 'game4':
        from web_games import game4_speed_drill
        game4_speed_drill.render(db, converter)

    elif st.session_state.current_game == 'game5':
        from web_games import game5_matching
        game5_matching.render(db, converter)

    else:
        # Welcome screen
        st.markdown("""
        <div class="game-card">
        <h2>Welcome to Prakrit Word Games! 🎉</h2>

        <p style="font-size: 1.1rem;">
        Learn Prakrit language through 5 interactive games designed to help you master
        verb conjugations and noun declensions.
        </p>

        <h3>📚 Available Games:</h3>
        <ul style="font-size: 1.05rem;">
            <li><strong>Form Quiz (रूप प्रश्नोत्तरी)</strong> - Type correct inflected forms</li>
            <li><strong>Word Identification (शब्द पहचान)</strong> - Identify roots and features</li>
            <li><strong>Paradigm Completion (तालिका पूर्ति)</strong> - Fill declension tables</li>
            <li><strong>Speed Drill (द्रुत अभ्यास)</strong> - Rapid-fire timed practice</li>
            <li><strong>Matching Game (मिलान खेल)</strong> - Match forms with descriptions</li>
        </ul>

        <h3>✨ Features:</h3>
        <ul style="font-size: 1.05rem;">
            <li>🔤 <strong>Multi-script support:</strong> Devanagari, IAST, ISO 15919, Harvard-Kyoto</li>
            <li>📈 <strong>Progress tracking:</strong> Score, streak, and accuracy</li>
            <li>🎯 <strong>Difficulty levels:</strong> Easy, Medium, Hard</li>
            <li>🌐 <strong>Web-based:</strong> Play anywhere, on any device</li>
        </ul>

        <p style="font-size: 1.1rem; margin-top: 2rem;">
        <strong>👆 Select a game above to begin learning!</strong>
        </p>
        </div>
        """, unsafe_allow_html=True)


if __name__ == '__main__':
    main()
