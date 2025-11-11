#!/usr/bin/env python3
"""
Command-line interface for providing feedback to the Prakrit parser
"""

import sys
from unified_parser import PrakritUnifiedParser

def main():
    if len(sys.argv) < 2:
        print("Usage: python feedback_cli.py <word>")
        print("Example: python feedback_cli.py muNinti")
        sys.exit(1)

    word = sys.argv[1]

    # Initialize parser
    parser = PrakritUnifiedParser()

    # Parse the word
    result = parser.parse(word)

    if not result.get('success', True):
        print(f"Error: {result.get('error')}")
        sys.exit(1)

    analyses = result.get('analyses', [])

    if not analyses:
        print(f"No analyses found for '{word}'")
        sys.exit(1)

    # Display analyses
    print(f"\n=== Analyses for: {word} ===\n")
    for i, analysis in enumerate(analyses[:10], 1):  # Show top 10
        atype = analysis.get('type', 'unknown')
        confidence = analysis.get('confidence', 0)

        print(f"{i}. [{confidence:.2f}] {atype.upper()}")

        if atype == 'verb':
            root = analysis.get('root', '?')
            ending = analysis.get('ending', '?')
            tense = analysis.get('tense', '?')
            person = analysis.get('person', '?')
            number = analysis.get('number', '?')
            print(f"   Root: {root}, Ending: {ending}")
            print(f"   {tense} tense, {person} person, {number} number")
        elif atype == 'noun':
            stem = analysis.get('stem', '?')
            suffix = analysis.get('suffix', '?')
            case = analysis.get('case', '?')
            number = analysis.get('number', '?')
            gender = analysis.get('gender', '?')
            print(f"   Stem: {stem}, Suffix: {suffix}")
            print(f"   {case} case, {number} number, {gender} gender")

        source = analysis.get('source', '')
        if source:
            print(f"   Source: {source}")

        notes = analysis.get('notes', [])
        if notes:
            print(f"   Notes: {notes[0]}")

        print()

    # Ask for feedback
    print("Which analysis is correct? (Enter number, or 0 to skip)")
    try:
        choice = input("Your choice: ").strip()
        if not choice or choice == '0':
            print("Skipped feedback")
            return

        choice_num = int(choice)
        if choice_num < 1 or choice_num > len(analyses):
            print(f"Invalid choice. Must be between 1 and {len(analyses)}")
            return

        # Record feedback
        correct_index = choice_num - 1  # Convert to 0-based
        correct_analysis = analyses[correct_index]

        feedback_result = parser.record_feedback(word, correct_analysis, analyses)

        if feedback_result.get('success'):
            print(f"\n✓ Feedback recorded successfully!")
            print(f"Total feedback submissions: {feedback_result.get('total_feedback', 0)}")

            # Show what was learned
            suffix_or_ending = correct_analysis.get('suffix') or correct_analysis.get('ending')
            if suffix_or_ending:
                suffix_stats = parser.feedback_data['suffix_accuracy'].get(suffix_or_ending, {})
                correct_count = suffix_stats.get('correct', 0)
                incorrect_count = suffix_stats.get('incorrect', 0)
                total = correct_count + incorrect_count
                if total > 0:
                    accuracy = correct_count / total * 100
                    print(f"\nSuffix '{suffix_or_ending}' stats:")
                    print(f"  Accuracy: {accuracy:.1f}% ({correct_count}/{total} correct)")
        else:
            print(f"\n✗ Error recording feedback: {feedback_result.get('error')}")

    except ValueError:
        print("Invalid input. Please enter a number.")
    except KeyboardInterrupt:
        print("\n\nCancelled")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
