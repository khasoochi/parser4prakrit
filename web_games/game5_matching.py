"""Game 5: Matching Game - Streamlit version"""

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
    """Render Game 5: Matching Game."""
    st.markdown("## 🎯 मिलान खेल (Matching Game)")
    st.markdown("Match the inflected forms with their grammatical descriptions.")

    # Initialize state
    if 'game5_items' not in st.session_state:
        st.session_state.game5_items = None
    if 'game5_matches' not in st.session_state:
        st.session_state.game5_matches = {}
    if 'game5_checked' not in st.session_state:
        st.session_state.game5_checked = False

    # New set button
    if st.button("🎲 New Matching Set", use_container_width=True):
        script = st.session_state.script_preference
        difficulty = st.session_state.difficulty
        term_script = st.session_state.grammar_terminology

        # Generate 4-5 items
        num_items = random.randint(4, 5)
        items = []

        for _ in range(num_items):
            if random.choice([True, False]):
                data = db.get_random_noun_form(difficulty=difficulty, script=script)
                if data:
                    desc = (
                        f"{data['root']} - "
                        f"{converter.convert_term(data['case'], term_script)}, "
                        f"{converter.convert_term(data['number'], term_script)}"
                    )
                    items.append((data['form'], desc))
            else:
                data = db.get_random_verb_form(difficulty=difficulty, script=script)
                if data:
                    desc = (
                        f"{data['root']} - "
                        f"{converter.convert_term(data['tense'], term_script)}, "
                        f"{converter.convert_term(data['person'], term_script)}, "
                        f"{converter.convert_term(data['number'], term_script)}"
                    )
                    items.append((data['form'], desc))

        if len(items) >= 3:
            # Shuffle descriptions
            forms = [item[0] for item in items]
            descriptions = [item[1] for item in items]
            shuffled_descriptions = descriptions.copy()
            random.shuffle(shuffled_descriptions)

            # Create correct matches
            correct_matches = {}
            for i, form in enumerate(forms):
                correct_desc = descriptions[i]
                correct_idx = shuffled_descriptions.index(correct_desc)
                correct_matches[i] = correct_idx

            st.session_state.game5_items = {
                'forms': forms,
                'descriptions': shuffled_descriptions,
                'correct_matches': correct_matches
            }
            st.session_state.game5_matches = {}
            st.session_state.game5_checked = False
            st.rerun()

    # Display matching game
    if st.session_state.game5_items:
        items = st.session_state.game5_items
        forms = items['forms']
        descriptions = items['descriptions']
        correct_matches = items['correct_matches']

        st.markdown("---")
        st.markdown("Match each inflected form (left) with its description (right):")

        # Create matching interface
        for i, form in enumerate(forms):
            col1, col2 = st.columns([1, 2])

            with col1:
                st.markdown(f"**{i+1}. {form}**")

            with col2:
                if not st.session_state.game5_checked:
                    # Selection dropdown
                    selected = st.selectbox(
                        f"Match for {form}",
                        options=range(len(descriptions)),
                        format_func=lambda x: descriptions[x],
                        key=f"match_{i}",
                        label_visibility="collapsed"
                    )
                    st.session_state.game5_matches[i] = selected
                else:
                    # Show result
                    selected = st.session_state.game5_matches.get(i, 0)
                    is_correct = (selected == correct_matches[i])

                    if is_correct:
                        st.success(f"✓ {descriptions[selected]}")
                    else:
                        st.error(f"✗ {descriptions[correct_matches[i]]}")
                        st.caption(f"You selected: {descriptions[selected]}")

        st.markdown("---")

        # Check button
        if not st.session_state.game5_checked:
            if st.button("✓ Check Matches", use_container_width=True):
                st.session_state.game5_checked = True

                # Calculate score
                correct = sum(1 for i in range(len(forms))
                             if st.session_state.game5_matches.get(i) == correct_matches[i])
                total = len(forms)
                all_correct = (correct == total)

                update_score(15 if all_correct else 5, correct=all_correct)
                st.rerun()
        else:
            # Show results
            correct = sum(1 for i in range(len(forms))
                         if st.session_state.game5_matches.get(i) == correct_matches[i])
            total = len(forms)

            if correct == total:
                st.success(f"✓ Perfect! All {total} matches correct!")
            else:
                st.info(f"You matched {correct}/{total} correctly ({correct/total*100:.1f}%)")

    else:
        st.info("👆 Click 'New Matching Set' to start!")
