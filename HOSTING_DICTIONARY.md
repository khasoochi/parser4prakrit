# Dictionary Database Hosting Guide

## Problem

Your Prakrit dictionary SQLite database is still too large for GitHub's 100MB file size limit.

**Options for hosting:**

---

## Option 1: Dropbox Public Link ⭐ **RECOMMENDED**

### Pros
- ✅ Free for reasonable sizes
- ✅ Simple to set up
- ✅ Direct download URL
- ✅ You control the file
- ✅ Easy to update

### Setup

1. **Upload to Dropbox**
   - Upload `prakrit_dict.db` to your Dropbox
   - Right-click → Share → Create link
   - Change `?dl=0` to `?dl=1` in the URL for direct download

2. **Download on first run**

Create `download_dictionary.py`:

```python
#!/usr/bin/env python3
"""
Download dictionary database from Dropbox on first run
"""
import os
import urllib.request
import sys

DICT_URL = "https://www.dropbox.com/s/YOUR_LINK_HERE/prakrit_dict.db?dl=1"
DICT_PATH = "prakrit_dict.db"

def download_dictionary():
    """Download dictionary if not present"""
    if os.path.exists(DICT_PATH):
        print(f"Dictionary already exists: {DICT_PATH}")
        return True

    print(f"Downloading dictionary from Dropbox...")
    try:
        urllib.request.urlretrieve(DICT_URL, DICT_PATH)
        size_mb = os.path.getsize(DICT_PATH) / (1024 * 1024)
        print(f"✓ Dictionary downloaded successfully ({size_mb:.2f} MB)")
        return True
    except Exception as e:
        print(f"✗ Error downloading dictionary: {e}")
        return False

if __name__ == '__main__':
    success = download_dictionary()
    sys.exit(0 if success else 1)
```

3. **Integrate with unified_parser.py**

```python
# At the top of unified_parser.py
import os

# In __init__ or module level
DICT_DB_PATH = 'prakrit_dict.db'

# Check if dictionary exists, download if needed
if not os.path.exists(DICT_DB_PATH):
    print("Dictionary not found. Downloading...")
    try:
        from download_dictionary import download_dictionary
        download_dictionary()
    except Exception as e:
        print(f"Warning: Could not download dictionary: {e}")
```

4. **For Vercel deployment**

Add to `vercel.json`:

```json
{
  "build": {
    "env": {
      "DICTIONARY_URL": "https://www.dropbox.com/s/YOUR_LINK_HERE/prakrit_dict.db?dl=1"
    }
  }
}
```

Update build script to download during deployment.

---

## Option 2: GitHub Releases

### Pros
- ✅ Integrated with GitHub
- ✅ Version control for database
- ✅ Free
- ✅ No size limit on releases

### Setup

1. **Create a GitHub Release**
   ```bash
   git tag v1.0-dict
   git push origin v1.0-dict
   ```

2. **Upload database to release**
   - Go to GitHub → Releases → Create new release
   - Upload `prakrit_dict.db` as an asset
   - Get download URL

3. **Download URL format**:
   ```
   https://github.com/USER/REPO/releases/download/v1.0-dict/prakrit_dict.db
   ```

4. **Auto-download script**:

```python
DICT_URL = "https://github.com/khasoochi/parser4prakrit/releases/download/v1.0-dict/prakrit_dict.db"

def download_from_github():
    if os.path.exists('prakrit_dict.db'):
        return

    import urllib.request
    print("Downloading dictionary from GitHub Releases...")
    urllib.request.urlretrieve(DICT_URL, 'prakrit_dict.db')
```

---

## Option 3: AWS S3 / CloudFlare R2

### Pros
- ✅ Professional CDN delivery
- ✅ Very fast downloads
- ✅ Scalable
- ✅ Good for production

### Cons
- ⚠️ Requires AWS/CloudFlare account
- ⚠️ Small cost (usually <$1/month)

### Setup (CloudFlare R2 - Free tier)

1. **Create CloudFlare R2 bucket**
   - Go to CloudFlare Dashboard → R2
   - Create bucket: `prakrit-dictionary`
   - Upload `prakrit_dict.db`

2. **Get public URL**:
   ```
   https://YOUR_ACCOUNT.r2.cloudflarestorage.com/prakrit-dictionary/prakrit_dict.db
   ```

3. **Same download script as above**

**Cost**: Free for 10GB storage, 1M reads/month

---

## Option 4: Google Drive

### Pros
- ✅ Free
- ✅ Large storage
- ✅ Familiar interface

### Cons
- ⚠️ Download links can change
- ⚠️ Rate limiting

### Setup

1. **Upload to Google Drive**
   - Upload `prakrit_dict.db`
   - Right-click → Share → Anyone with link can view
   - Get share link

2. **Extract file ID** from URL:
   ```
   https://drive.google.com/file/d/FILE_ID_HERE/view
   ```

3. **Download URL**:
   ```python
   FILE_ID = "YOUR_FILE_ID"
   DICT_URL = f"https://drive.google.com/uc?export=download&id={FILE_ID}"
   ```

---

## Option 5: Vercel Blob Storage

### Pros
- ✅ Integrated with Vercel
- ✅ Fast CDN delivery
- ✅ Easy deployment

### Cons
- ⚠️ Paid feature ($0.15/GB/month)

### Setup

1. **Install Vercel Blob**:
   ```bash
   npm install @vercel/blob
   ```

2. **Upload via CLI**:
   ```bash
   vercel blob upload prakrit_dict.db
   ```

3. **Get download URL** from output

4. **Use in code**:
   ```python
   import os
   DICT_URL = os.environ.get('BLOB_URL_DICTIONARY')
   ```

---

## Option 6: Git LFS (Large File Storage)

### Pros
- ✅ Integrated with Git workflow
- ✅ Version controlled

### Cons
- ⚠️ GitHub LFS: 1GB storage free, then $5/month per 50GB
- ⚠️ Slower clones

### Setup

```bash
# Install Git LFS
git lfs install

# Track database file
git lfs track "*.db"
git add .gitattributes

# Add and commit
git add prakrit_dict.db
git commit -m "Add dictionary via LFS"
git push
```

**Cost**: Free for 1GB, $5/month for 50GB data pack

---

## Comparison Table

| Option | Cost | Setup Time | Speed | Reliability |
|--------|------|------------|-------|-------------|
| **Dropbox** | Free | 5 min | Fast | ⭐⭐⭐⭐⭐ |
| GitHub Releases | Free | 10 min | Fast | ⭐⭐⭐⭐⭐ |
| CloudFlare R2 | Free tier | 15 min | Very Fast | ⭐⭐⭐⭐⭐ |
| Google Drive | Free | 5 min | Medium | ⭐⭐⭐ |
| Vercel Blob | $0.15/GB/mo | 10 min | Very Fast | ⭐⭐⭐⭐⭐ |
| Git LFS | $5/mo (>1GB) | 5 min | Slow | ⭐⭐⭐⭐ |

---

## Recommended Approach

### For Development:
**Use Dropbox** - Simple, free, reliable

### For Production:
**Use CloudFlare R2 or GitHub Releases** - Professional, fast, scalable

---

## Implementation Example (Dropbox)

### 1. Create `download_dictionary.py`

```python
#!/usr/bin/env python3
import os
import urllib.request
import sys

# Replace with your Dropbox link (change ?dl=0 to ?dl=1)
DROPBOX_URL = "https://www.dropbox.com/scl/fi/YOUR_LINK/prakrit_dict.db?rlkey=YOUR_KEY&dl=1"
DICT_PATH = "prakrit_dict.db"

def download_dictionary():
    """Download dictionary if not present"""
    if os.path.exists(DICT_PATH):
        print(f"✓ Dictionary found: {DICT_PATH}")
        return True

    print(f"Downloading dictionary from Dropbox...")
    print(f"URL: {DROPBOX_URL[:50]}...")

    try:
        # Download with progress
        def reporthook(count, block_size, total_size):
            percent = int(count * block_size * 100 / total_size)
            sys.stdout.write(f"\rDownloading: {percent}%")
            sys.stdout.flush()

        urllib.request.urlretrieve(DROPBOX_URL, DICT_PATH, reporthook)
        print()

        size_mb = os.path.getsize(DICT_PATH) / (1024 * 1024)
        print(f"✓ Dictionary downloaded successfully ({size_mb:.2f} MB)")
        return True

    except Exception as e:
        print(f"\n✗ Error downloading dictionary: {e}")
        print("Please download manually from:")
        print(DROPBOX_URL.replace('?dl=1', '?dl=0'))
        return False

if __name__ == '__main__':
    success = download_dictionary()
    sys.exit(0 if success else 1)
```

### 2. Update `unified_parser.py`

```python
# At the top
import os

# Initialize parser
def initialize_parser():
    """Initialize parser with dictionary download if needed"""
    # Check for dictionary
    if not os.path.exists('prakrit_dict.db'):
        try:
            from download_dictionary import download_dictionary
            if not download_dictionary():
                print("Warning: Dictionary not available. Parser will work without meanings.")
        except ImportError:
            print("Warning: download_dictionary.py not found")

    # Create parser
    dict_path = 'prakrit_dict.db' if os.path.exists('prakrit_dict.db') else None
    return PrakritUnifiedParser(dict_db_path=dict_path)

# Use this instead of direct initialization
parser = initialize_parser()
```

### 3. Add to README

```markdown
## Dictionary Setup

The Prakrit dictionary is hosted externally due to size.

**Option 1: Auto-download (Recommended)**
```bash
python3 download_dictionary.py
```

**Option 2: Manual download**
1. Download from: [Dropbox Link](https://www.dropbox.com/...)
2. Place in repository root as `prakrit_dict.db`

## Running without dictionary

The parser works without the dictionary but won't provide word meanings.
```

### 4. Add to `.gitignore`

```
# Dictionary database (too large for Git)
prakrit_dict.db
```

### 5. For Vercel Deployment

Create `build.sh`:

```bash
#!/bin/bash
echo "Downloading dictionary..."
python3 download_dictionary.py

if [ ! -f "prakrit_dict.db" ]; then
    echo "Warning: Dictionary download failed"
    exit 0  # Don't fail build
fi

echo "Dictionary ready for deployment"
```

Update `vercel.json`:

```json
{
  "buildCommand": "bash build.sh"
}
```

---

## Testing

```bash
# Test download
python3 download_dictionary.py

# Verify
ls -lh prakrit_dict.db

# Test parser with dictionary
python3 unified_parser.py ghāya
# Should show dictionary meanings if available
```

---

## Troubleshooting

### "Download failed"
- Check URL is correct
- Verify `?dl=1` at end (not `?dl=0`)
- Check internet connection
- Try manual download

### "Dictionary not loading"
- Check file size: `ls -lh prakrit_dict.db`
- Test with: `python3 dictionary_lookup.py prakrit_dict.db ghāya`
- Verify not corrupted: `file prakrit_dict.db` should show "SQLite 3.x database"

### "Vercel deployment fails"
- Check build timeout (default 45s, may need upgrade)
- Pre-download dictionary and include in deployment
- Use smaller dictionary subset for deployment

---

## Your Next Steps

1. **Choose hosting**: Dropbox (easiest) or GitHub Releases
2. **Upload** your `prakrit_dict.db`
3. **Get download URL**
4. **Create** `download_dictionary.py` with your URL
5. **Test** locally: `python3 download_dictionary.py`
6. **Update** `.gitignore` to exclude `prakrit_dict.db`
7. **Deploy** to Vercel with auto-download

---

*Once you provide the Dropbox link, I can create the complete download script for you.*
