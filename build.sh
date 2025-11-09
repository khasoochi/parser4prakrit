#!/bin/bash
# Vercel build script - downloads databases before deployment

set -e  # Exit on error

echo "================================================"
echo "Prakrit Parser - Vercel Build Script"
echo "================================================"

# Download databases
echo ""
echo "📥 Downloading databases from Dropbox..."
python3 download_databases.py

# Check if at least dictionary downloaded
if [ ! -f "prakrit-dict.db" ]; then
    echo ""
    echo "⚠️  Warning: Dictionary database not downloaded"
    echo "   Parser will work but won't provide word meanings"
fi

# Check verb forms
if [ ! -f "verb_forms.db" ]; then
    echo "⚠️  Warning: Verb forms database not downloaded"
fi

# Check noun forms
if [ ! -f "noun_forms.db" ]; then
    echo "⚠️  Warning: Noun forms database not downloaded"
fi

echo ""
echo "✓ Build preparation complete"
echo "================================================"
