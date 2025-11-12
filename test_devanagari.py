from unified_parser import PrakritUnifiedParser

parser = PrakritUnifiedParser()

# Test with Devanagari
print('='*60)
print('Testing Devanagari: पुच्छिस्संति')
result1 = parser.parse('पुच्छिस्संति')
print('Success:', result1["success"])
print('HK form:', result1.get("hk_form", "N/A"))
print('Analyses found:', len(result1.get("analyses", [])))
if result1.get('analyses'):
    for i, analysis in enumerate(result1['analyses'][:3]):
        print(f'  Analysis {i+1}: type={analysis.get("type")}, root={analysis.get("root", analysis.get("stem"))}, confidence={analysis.get("confidence")}')

print()
print('='*60)
print('Testing HK: pucchissaMti')
result2 = parser.parse('pucchissaMti')
print('Success:', result2["success"])
print('HK form:', result2.get("hk_form", "N/A"))
print('Analyses found:', len(result2.get("analyses", [])))
if result2.get('analyses'):
    for i, analysis in enumerate(result2['analyses'][:3]):
        print(f'  Analysis {i+1}: type={analysis.get("type")}, root={analysis.get("root", analysis.get("stem"))}, confidence={analysis.get("confidence")}')
