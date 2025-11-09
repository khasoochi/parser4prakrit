"""Game 3: Paradigm Completion - Streamlit version"""

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
    """Render Game 3: Paradigm Completion."""
    st.markdown("## 📊 तालिका पूर्ति (Paradigm Completion)")
    st.markdown("Fill in the missing cells in the declension table.")

    # Initialize state
    if 'game3_paradigm' not in st.session_state:
        st.session_state.game3_paradigm = None
    if 'game3_answers' not in st.session_state:
        st.session_state.game3_answers = {}
    if 'game3_checked' not in st.session_state:
        st.session_state.game3_checked = False

    # New paradigm button
    if st.button("🎲 New Paradigm", use_container_width=True):
        script = st.session_state.script_preference
        difficulty = st.session_state.difficulty

        noun = db.get_random_noun(difficulty=difficulty, script=script)
        if noun:
            paradigm = db.get_noun_paradigm(noun['root_hk'], script=script)

            # Create hidden cells (50% random)
            hidden_cells = []
            for case_name, numbers in paradigm.items():
                for number, form in numbers.items():
                    if random.random() < 0.5 and form:
                        hidden_cells.append((case_name, number, form))

            st.session_state.game3_paradigm = {
                'noun': noun,
                'paradigm': paradigm,
                'hidden_cells': hidden_cells
            }
            st.session_state.game3_answers = {}
            st.session_state.game3_checked = False
            st.rerun()

    # Display paradigm
    if st.session_state.game3_paradigm:
        para = st.session_state.game3_paradigm
        noun = para['noun']
        paradigm = para['paradigm']
        hidden_cells = para['hidden_cells']
        term_script = st.session_state.grammar_terminology

        st.markdown(f"""
        **{converter.convert_term('root', term_script)}:** {noun['root']} ({noun['meaning']})
        **{converter.convert_term('gender', term_script)}:** {converter.convert_term(noun['gender'], term_script)}
        """)

        st.markdown("---")

        # Display table
        st.markdown("Fill in the yellow highlighted cells:")

        cases = list(paradigm.keys())
        numbers = ['singular', 'plural']

        # Create table header
        cols = st.columns([2, 2, 2])
        cols[0].markdown(f"**{converter.convert_term('case', term_script)}**")
        cols[1].markdown(f"**{converter.convert_term('singular', term_script)}**")
        cols[2].markdown(f"**{converter.convert_term('plural', term_script)}**")

        # Table rows
        for case in cases:
            cols = st.columns([2, 2, 2])

            # Case name
            cols[0].markdown(converter.convert_term(case, term_script))

            # Forms
            for idx, number in enumerate(numbers, start=1):
                form = paradigm[case].get(number, '')

                # Check if this cell is hidden
                is_hidden = (case, number, form) in hidden_cells

                if is_hidden and not st.session_state.game3_checked:
                    # Input field
                    key = f"{case}_{number}"
                    answer = cols[idx].text_input(
                        f"{case}_{number}",
                        key=key,
                        label_visibility="collapsed",
                        placeholder="Type here..."
                    )
                    if answer:
                        st.session_state.game3_answers[key] = answer
                elif is_hidden and st.session_state.game3_checked:
                    # Show result
                    key = f"{case}_{number}"
                    user_answer = st.session_state.game3_answers.get(key, '')

                    if user_answer == form:
                        cols[idx].markdown(f"✅ {form}")
                    else:
                        cols[idx].markdown(f"❌ {form}")
                        if user_answer:
                            cols[idx].caption(f"You: {user_answer}")
                else:
                    # Show prefilled
                    cols[idx].markdown(f"✓ {form}")

        st.markdown("---")

        # Check button
        if not st.session_state.game3_checked:
            if st.button("✓ Check Answers", use_container_width=True):
                if len(st.session_state.game3_answers) >= len(hidden_cells) * 0.5:
                    st.session_state.game3_checked = True

                    # Calculate score
                    correct = 0
                    for case, number, form in hidden_cells:
                        key = f"{case}_{number}"
                        if st.session_state.game3_answers.get(key) == form:
                            correct += 1

                    total = len(hidden_cells)
                    all_correct = (correct == total)

                    update_score(20 if all_correct else 5, correct=all_correct)
                    st.rerun()
                else:
                    st.warning("Please fill in at least half of the missing cells!")
        else:
            # Show results
            correct = sum(1 for case, number, form in hidden_cells
                         if st.session_state.game3_answers.get(f"{case}_{number}") == form)
            total = len(hidden_cells)

            if correct == total:
                st.success(f"✓ Perfect! All {total} cells correct!")
            else:
                st.info(f"You filled {correct}/{total} cells correctly ({correct/total*100:.1f}%)")

    else:
        st.info("👆 Click 'New Paradigm' to start!")
