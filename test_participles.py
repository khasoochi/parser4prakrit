from unified_parser import PrakritUnifiedParser

parser = PrakritUnifiedParser()

print("="*70)
print("Testing Participle Recognition with Sanskrit Terminology")
print("="*70)

test_forms = [
    ('pucchamANAo', 'Declined present participle'),
    ('pucchamANA', 'Present participle stem'),
    ('pucchittA', 'Absolutive participle'),
    ('pucchanta', 'Present participle stem (anta)'),
    ('pucchia', 'Past passive participle stem'),
]

for form, description in test_forms:
    print(f"\n\nForm: {form} ({description})")
    print("-" * 70)
    result = parser.parse(form)

    if result['success'] and result.get('analyses'):
        # Show top 3 analyses
        for i, analysis in enumerate(result['analyses'][:3], 1):
            print(f"\nAnalysis {i}:")
            print(f"  Type: {analysis.get('type')}")

            if analysis.get('type') == 'participle':
                print(f"  Root: {analysis.get('root')}")
                print(f"  Participle Type: {analysis.get('participle_type')}")
                print(f"  Sanskrit Term: {analysis.get('sanskrit_term', 'N/A')}")

                if analysis.get('source') == 'declined_participle':
                    print(f"  Stem: {analysis.get('stem')}")
                    print(f"  Participle Suffix: {analysis.get('participle_suffix')}")
                    print(f"  Noun Ending: {analysis.get('noun_ending')}")

                    # Case info
                    if analysis.get('case'):
                        print(f"  Case: {analysis.get('case')} ({analysis.get('sanskrit_case')})")
                    elif analysis.get('cases'):
                        print(f"  Possible Cases: {', '.join(analysis.get('cases'))}")

                    # Number info
                    if analysis.get('number'):
                        print(f"  Number: {analysis.get('number')} ({analysis.get('sanskrit_number')})")

                    # Gender info
                    if analysis.get('gender'):
                        print(f"  Gender: {analysis.get('gender')} ({analysis.get('sanskrit_gender')})")
                    elif analysis.get('genders'):
                        print(f"  Possible Genders: {', '.join(analysis.get('genders'))}")

                else:
                    print(f"  Suffix: {analysis.get('suffix')}")
                    if analysis.get('declined'):
                        print(f"  Note: This is a declinable form")

                print(f"  Confidence: {analysis.get('confidence'):.2f}")
                print(f"  Source: {analysis.get('source')}")

                if analysis.get('notes'):
                    print(f"  Notes:")
                    for note in analysis['notes']:
                        print(f"    - {note}")
    else:
        print("  No analyses found")

print("\n" + "="*70)
