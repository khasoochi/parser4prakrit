"""Game 2: Word Identification - Streamlit version"""

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
    """Render Game 2: Word Identification."""
    st.markdown("## 🔍 शब्द पहचान (Word Identification)")
    st.markdown("Identify the root word and grammatical features from the inflected form.")

    # Initialize state
    if 'game2_question' not in st.session_state:
        st.session_state.game2_question = None
    if 'game2_answered' not in st.session_state:
        st.session_state.game2_answered = False

    # New question button
    if st.button("🎲 New Question", use_container_width=True):
        st.session_state.game2_answered = False

        script = st.session_state.script_preference
        difficulty = st.session_state.difficulty

        # Random verb or noun
        if random.choice([True, False]):
            data = db.get_random_verb_form(difficulty=difficulty, script=script)
            if data:
                # Get all verbs for choices
                all_verbs = db.get_all_verbs(script=script)
                root_choices = [data['root']]
                others = [v['root'] for v in all_verbs if v['root'] != data['root']]
                root_choices.extend(random.sample(others, min(3, len(others))))
                random.shuffle(root_choices)

                st.session_state.game2_question = {
                    'type': 'verb',
                    'data': data,
                    'root_choices': root_choices
                }
        else:
            data = db.get_random_noun_form(difficulty=difficulty, script=script)
            if data:
                all_nouns = db.get_all_nouns(script=script)
                root_choices = [data['root']]
                others = [n['root'] for n in all_nouns if n['root'] != data['root']]
                root_choices.extend(random.sample(others, min(3, len(others))))
                random.shuffle(root_choices)

                st.session_state.game2_question = {
                    'type': 'noun',
                    'data': data,
                    'root_choices': root_choices
                }

        st.rerun()

    # Display question
    if st.session_state.game2_question:
        question = st.session_state.game2_question
        data = question['data']
        term_script = st.session_state.grammar_terminology

        st.markdown("---")

        # Show inflected form
        st.markdown(f"""
        <div class="question-text">
        Identify this form: <strong style="font-size: 2rem;">{data['form']}</strong>
        </div>
        """, unsafe_allow_html=True)

        if not st.session_state.game2_answered:
            # Root selection
            selected_root = st.radio(
                f"1. Select {converter.convert_term('root', term_script)}:",
                options=question['root_choices'],
                key="root_select"
            )

            # Feature selections based on type
            if question['type'] == 'verb':
                selected_tense = st.radio(
                    f"2. Select {converter.convert_term('tense', term_script)}:",
                    options=['present', 'past', 'future'],
                    format_func=lambda x: converter.convert_term(x, term_script),
                    key="tense_select"
                )

                selected_number = st.radio(
                    f"3. Select {converter.convert_term('number', term_script)}:",
                    options=['singular', 'plural'],
                    format_func=lambda x: converter.convert_term(x, term_script),
                    key="number_select"
                )

                if st.button("✓ Check Answer", use_container_width=True):
                    root_correct = (selected_root == data['root'])
                    tense_correct = (selected_tense == data['tense'])
                    number_correct = (selected_number == data['number'])
                    all_correct = root_correct and tense_correct and number_correct

                    st.session_state.game2_result = {
                        'all_correct': all_correct,
                        'root_correct': root_correct,
                        'tense_correct': tense_correct,
                        'number_correct': number_correct,
                        'selected_root': selected_root,
                        'selected_tense': selected_tense,
                        'selected_number': selected_number
                    }
                    st.session_state.game2_answered = True

                    update_score(15 if all_correct else 0, correct=all_correct)
                    st.rerun()

            else:  # noun
                selected_case = st.radio(
                    f"2. Select {converter.convert_term('case', term_script)}:",
                    options=['nominative', 'accusative', 'instrumental', 'genitive'],
                    format_func=lambda x: converter.convert_term(x, term_script),
                    key="case_select"
                )

                selected_number = st.radio(
                    f"3. Select {converter.convert_term('number', term_script)}:",
                    options=['singular', 'plural'],
                    format_func=lambda x: converter.convert_term(x, term_script),
                    key="number_select"
                )

                if st.button("✓ Check Answer", use_container_width=True):
                    root_correct = (selected_root == data['root'])
                    case_correct = (selected_case == data['case'])
                    number_correct = (selected_number == data['number'])
                    all_correct = root_correct and case_correct and number_correct

                    st.session_state.game2_result = {
                        'all_correct': all_correct,
                        'root_correct': root_correct,
                        'case_correct': case_correct,
                        'number_correct': number_correct,
                        'selected_root': selected_root,
                        'selected_case': selected_case,
                        'selected_number': selected_number
                    }
                    st.session_state.game2_answered = True

                    update_score(15 if all_correct else 0, correct=all_correct)
                    st.rerun()

        else:
            # Show results
            result = st.session_state.game2_result
            term_script = st.session_state.grammar_terminology

            if result['all_correct']:
                st.markdown('<div class="correct-answer">✓ Perfect! All answers correct!</div>',
                           unsafe_allow_html=True)
            else:
                st.markdown('<div class="incorrect-answer">✗ Some answers incorrect</div>',
                           unsafe_allow_html=True)

                if not result['root_correct']:
                    st.markdown(f"**Root:** {data['root']} (you selected: {result['selected_root']})")

                if question['type'] == 'verb':
                    if not result.get('tense_correct'):
                        correct_tense = converter.convert_term(data['tense'], term_script)
                        selected_tense = converter.convert_term(result['selected_tense'], term_script)
                        st.markdown(f"**Tense:** {correct_tense} (you selected: {selected_tense})")

                if question['type'] == 'noun':
                    if not result.get('case_correct'):
                        correct_case = converter.convert_term(data['case'], term_script)
                        selected_case = converter.convert_term(result['selected_case'], term_script)
                        st.markdown(f"**Case:** {correct_case} (you selected: {selected_case})")

                if not result['number_correct']:
                    correct_number = converter.convert_term(data['number'], term_script)
                    selected_number = converter.convert_term(result['selected_number'], term_script)
                    st.markdown(f"**Number:** {correct_number} (you selected: {selected_number})")

    else:
        st.info("👆 Click 'New Question' to start!")
