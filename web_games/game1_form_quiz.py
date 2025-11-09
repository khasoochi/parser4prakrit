"""Game 1: Form Quiz - Streamlit version"""

import streamlit as st
import random


def update_score(points, correct=True):
    """Update score and streak."""
    st.session_state.score += points
    st.session_state.questions_answered += 1

    if correct:
        st.session_state.streak += 1
        st.session_state.correct_answers += 1
    else:
        st.session_state.streak = 0


def render(db, converter):
    """Render Game 1: Form Quiz."""
    st.markdown("## 📝 रूप प्रश्नोत्तरी (Form Quiz)")
    st.markdown("Type the correct inflected form based on the root word and grammatical specifications.")

    # Initialize game state
    if 'game1_question' not in st.session_state:
        st.session_state.game1_question = None
    if 'game1_answered' not in st.session_state:
        st.session_state.game1_answered = False
    if 'game1_user_answer' not in st.session_state:
        st.session_state.game1_user_answer = ''

    # Word type selection
    word_type = st.radio(
        "Select word type:",
        options=['Both', 'Verbs only', 'Nouns only'],
        horizontal=True
    )

    # Generate new question button
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🎲 New Question", use_container_width=True):
            st.session_state.game1_answered = False
            st.session_state.game1_user_answer = ''

            # Generate question
            script = st.session_state.script_preference
            term_script = st.session_state.grammar_terminology
            difficulty = st.session_state.difficulty

            if word_type == 'Verbs only' or (word_type == 'Both' and random.choice([True, False])):
                # Verb question
                data = db.get_random_verb_form(difficulty=difficulty, script=script)
                if data:
                    st.session_state.game1_question = {
                        'type': 'verb',
                        'data': data
                    }
            else:
                # Noun question
                data = db.get_random_noun_form(difficulty=difficulty, script=script)
                if data:
                    st.session_state.game1_question = {
                        'type': 'noun',
                        'data': data
                    }

            st.rerun()

    # Display question
    if st.session_state.game1_question:
        question = st.session_state.game1_question
        data = question['data']
        term_script = st.session_state.grammar_terminology

        st.markdown("---")

        # Root word
        st.markdown(f"""
        <div class="question-text">
        {converter.convert_term('root', term_script)}: <strong>{data['root']}</strong> ({data['meaning']})
        </div>
        """, unsafe_allow_html=True)

        # Grammar specifications
        if question['type'] == 'verb':
            grammar_parts = [
                f"{converter.convert_term('tense', term_script)}: {converter.convert_term(data['tense'], term_script)}",
                f"{converter.convert_term('person', term_script)}: {converter.convert_term(data['person'], term_script)}",
                f"{converter.convert_term('number', term_script)}: {converter.convert_term(data['number'], term_script)}"
            ]
        else:
            grammar_parts = [
                f"{converter.convert_term('case', term_script)}: {converter.convert_term(data['case'], term_script)}",
                f"{converter.convert_term('number', term_script)}: {converter.convert_term(data['number'], term_script)}",
                f"{converter.convert_term('gender', term_script)}: {converter.convert_term(data['gender'], term_script)}"
            ]

        st.markdown(f"**Required form:** {' | '.join(grammar_parts)}")

        # Answer input
        if not st.session_state.game1_answered:
            user_answer = st.text_input(
                "Your answer:",
                value=st.session_state.game1_user_answer,
                key="answer_input",
                placeholder="Type the inflected form here..."
            )

            col1, col2, col3 = st.columns([1, 1, 3])

            with col1:
                if st.button("✓ Check Answer", use_container_width=True):
                    if user_answer.strip():
                        st.session_state.game1_user_answer = user_answer.strip()
                        st.session_state.game1_answered = True
                        st.rerun()
                    else:
                        st.warning("Please type an answer first!")

            with col2:
                if st.button("💡 Hint", use_container_width=True):
                    correct = data['form']
                    hint_len = len(correct) // 2
                    st.info(f"**Hint:** Starts with '{correct[:hint_len]}...' (Length: {len(correct)} characters)")

        else:
            # Show result
            correct_answer = data['form']
            user_answer = st.session_state.game1_user_answer

            if user_answer == correct_answer:
                st.markdown(f'<div class="correct-answer">✓ Correct! The answer is: {correct_answer}</div>',
                           unsafe_allow_html=True)
                update_score(10, correct=True)
            else:
                st.markdown(f'<div class="incorrect-answer">✗ Incorrect.</div>', unsafe_allow_html=True)
                st.markdown(f"**Correct answer:** {correct_answer}")
                st.markdown(f"**Your answer:** {user_answer}")
                update_score(0, correct=False)

            st.markdown("---")
            if st.button("→ Next Question", use_container_width=True):
                st.session_state.game1_answered = False
                st.session_state.game1_user_answer = ''

                # Generate new question
                script = st.session_state.script_preference
                difficulty = st.session_state.difficulty

                if word_type == 'Verbs only' or (word_type == 'Both' and random.choice([True, False])):
                    data = db.get_random_verb_form(difficulty=difficulty, script=script)
                    if data:
                        st.session_state.game1_question = {'type': 'verb', 'data': data}
                else:
                    data = db.get_random_noun_form(difficulty=difficulty, script=script)
                    if data:
                        st.session_state.game1_question = {'type': 'noun', 'data': data}

                st.rerun()

    else:
        st.info("👆 Click 'New Question' to start!")
