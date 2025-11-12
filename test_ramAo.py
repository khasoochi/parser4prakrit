from unified_parser import PrakritUnifiedParser

parser = PrakritUnifiedParser()

print("="*70)
print("Testing ramAo - should show ramA (feminine A-ending)")
print("="*70)

result = parser.parse('ramAo')

if result['success'] and result.get('analyses'):
    # Show ALL noun analyses
    noun_analyses = [a for a in result['analyses'] if a.get('type') == 'noun']
    print(f"\nFound {len(noun_analyses)} noun analyses total")
    print("\nAll noun analyses:")
    for i, analysis in enumerate(noun_analyses, 1):
        stem = analysis.get('stem', '')
        gender = analysis.get('gender', '')
        case = analysis.get('case', '')
        print(f"{i}. Stem: {stem:15s} Gender: {gender:10s} Case: {case:15s} Suffix: {analysis.get('suffix', 'N/A')}")

        # Check if we have ramA feminine
        if stem == 'ramA' and gender == 'feminine':
            print(f"   ✓ Found correct ramA feminine analysis!")

print("\n" + "="*70)
