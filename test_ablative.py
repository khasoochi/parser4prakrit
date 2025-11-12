from unified_parser import PrakritUnifiedParser

parser = PrakritUnifiedParser()

print("="*70)
print("Testing Ablative (5th case) Stem Reconstruction")
print("="*70)

test_forms = [
    ('rAmAo', 'Expected: rAma (masc/neut) OR rAmA (fem)'),
    ('ramAo', 'Expected: ramA (fem) - A-ending'),
    ('purisAo', 'Expected: purisa (masc)'),
    ('kaJJAo', 'Expected: kaJJA (fem)'),
]

for form, description in test_forms:
    print(f"\n\nForm: {form}")
    print(f"Description: {description}")
    print("-" * 70)

    result = parser.parse(form)

    if result['success'] and result.get('analyses'):
        # Show top 5 analyses
        for i, analysis in enumerate(result['analyses'][:5], 1):
            if analysis.get('type') == 'noun':
                print(f"\nAnalysis {i}:")
                print(f"  Stem: {analysis.get('stem')}")
                print(f"  Suffix: {analysis.get('suffix')}")
                print(f"  Gender: {analysis.get('gender')}")
                print(f"  Case: {analysis.get('case')}")
                print(f"  Number: {analysis.get('number')}")
                print(f"  Confidence: {analysis.get('confidence'):.2f}")
                print(f"  Ending Type: {analysis.get('stem_ending_type', 'N/A')}")
    else:
        print("  No analyses found")

print("\n" + "="*70)
print("Testing Gender Constraints")
print("="*70)

# Test that a-ending feminine is rejected
print("\nVerifying NO a-ending feminine words are suggested...")
result = parser.parse('rAmAo')
if result['success']:
    for analysis in result['analyses']:
        if analysis.get('type') == 'noun':
            stem = analysis.get('stem', '')
            gender = analysis.get('gender', '')
            if stem.endswith('a') and gender == 'feminine':
                print(f"  ✗ ERROR: Found invalid a-ending feminine: stem={stem}, gender={gender}")
            elif stem.endswith('a'):
                print(f"  ✓ OK: a-ending with {gender} gender (stem: {stem})")
            elif stem.endswith('A') or stem.endswith('ā'):
                print(f"  ✓ OK: A-ending with {gender} gender (stem: {stem})")

print("\n" + "="*70)
