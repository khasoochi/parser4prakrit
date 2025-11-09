"""Game 4: Speed Drill - Streamlit version"""

import streamlit as st
import random
import time


def render(db, converter):
    """Render Game 4: Speed Drill."""
    st.markdown("## ⚡ द्रुत अभ्यास (Speed Drill)")
    st.markdown("Answer as many questions as you can in 2 minutes!")

    # Initialize state
    if 'game4_active' not in st.session_state:
        st.session_state.game4_active = False
    if 'game4_start_time' not in st.session_state:
        st.session_state.game4_start_time = None
    if 'game4_questions' not in st.session_state:
        st.session_state.game4_questions = 0
    if 'game4_correct' not in st.session_state:
        st.session_state.game4_correct = 0
    if 'game4_question' not in st.session_state:
        st.session_state.game4_question = None

    # Start button
    if not st.session_state.game4_active:
        if st.button("▶ Start 2-Minute Sprint", use_container_width=True, type="primary"):
            st.session_state.game4_active = True
            st.session_state.game4_start_time = time.time()
            st.session_state.game4_questions = 0
            st.session_state.game4_correct = 0

            # Generate first question
            script = st.session_state.script_preference
            difficulty = st.session_state.difficulty

            if random.choice([True, False]):
                data = db.get_random_verb_form(difficulty=difficulty, script=script)
            else:
                data = db.get_random_noun_form(difficulty=difficulty, script=script)

            st.session_state.game4_question = data
            st.rerun()

        st.info("Click 'Start' to begin the 2-minute challenge!")
        return

    # Active game
    elapsed = time.time() - st.session_state.game4_start_time
    remaining = max(0, 120 - int(elapsed))

    if remaining == 0:
        # Game over
        st.session_state.game4_active = False

        accuracy = (st.session_state.game4_correct / st.session_state.game4_questions * 100) if st.session_state.game4_questions > 0 else 0

        st.markdown(f"""
        ## 🏁 Game Over!

        **Questions answered:** {st.session_state.game4_questions}
        **Correct:** {st.session_state.game4_correct}
        **Accuracy:** {accuracy:.1f}%
        """)

        if st.button("Play Again"):
            st.rerun()
        return

    # Timer
    minutes = remaining // 60
    seconds = remaining % 60
    st.markdown(f"### ⏱️ Time Remaining: {minutes}:{seconds:02d}")

    st.markdown(f"**Questions:** {st.session_state.game4_questions} | **Correct:** {st.session_state.game4_correct}")

    st.markdown("---")

    # Display question
    if st.session_state.game4_question:
        data = st.session_state.game4_question
        term_script = st.session_state.grammar_terminology

        if 'tense' in data:  # verb
            question_text = (
                f"{data['root']} - "
                f"{converter.convert_term(data['tense'], term_script)}, "
                f"{converter.convert_term(data['person'], term_script)}, "
                f"{converter.convert_term(data['number'], term_script)}"
            )
        else:  # noun
            question_text = (
                f"{data['root']} - "
                f"{converter.convert_term(data['case'], term_script)}, "
                f"{converter.convert_term(data['number'], term_script)}"
            )

        st.markdown(f"**Question {st.session_state.game4_questions + 1}:**")
        st.markdown(f'<div class="question-text">{question_text}</div>', unsafe_allow_html=True)

        # Answer input
        user_answer = st.text_input("Your answer:", key=f"speed_answer_{st.session_state.game4_questions}")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Submit", use_container_width=True):
                if user_answer.strip():
                    st.session_state.game4_questions += 1

                    if user_answer.strip() == data['form']:
                        st.session_state.game4_correct += 1
                        st.session_state.score += 5
                        st.session_state.streak += 1
                        st.success("✓ Correct!")
                    else:
                        st.session_state.streak = 0
                        st.error(f"✗ Wrong! Answer: {data['form']}")

                    # Generate next question
                    script = st.session_state.script_preference
                    difficulty = st.session_state.difficulty

                    if random.choice([True, False]):
                        data = db.get_random_verb_form(difficulty=difficulty, script=script)
                    else:
                        data = db.get_random_noun_form(difficulty=difficulty, script=script)

                    st.session_state.game4_question = data
                    time.sleep(0.5)
                    st.rerun()

        with col2:
            if st.button("Skip (-5 pts)", use_container_width=True):
                st.session_state.score -= 5
                st.session_state.game4_questions += 1

                # Generate next question
                script = st.session_state.script_preference
                difficulty = st.session_state.difficulty

                if random.choice([True, False]):
                    data = db.get_random_verb_form(difficulty=difficulty, script=script)
                else:
                    data = db.get_random_noun_form(difficulty=difficulty, script=script)

                st.session_state.game4_question = data
                st.rerun()

        # Auto-refresh to update timer
        if remaining > 0:
            time.sleep(1)
            st.rerun()
