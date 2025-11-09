# 🚀 Deploy Prakrit Games Web App

## Step-by-Step Deployment to Vercel + Supabase

Follow this guide to deploy your Prakrit Games web application.

---

## 📋 Prerequisites

- Your 2 SQLite database files (60MB + 120MB)
- GitHub account
- Free Supabase account (sign up at https://supabase.com)
- Free Vercel account (sign up at https://vercel.com)

---

## PART 1: Setup Supabase Database (15-20 minutes)

### Step 1: Create Supabase Project

1. Go to https://supabase.com and sign in
2. Click "New Project"
3. Enter project details:
   - **Name:** `prakrit-games`
   - **Database Password:** (choose a strong password - SAVE THIS!)
   - **Region:** Choose closest to your users
4. Click "Create new project" (wait 2-3 minutes for setup)

### Step 2: Get Connection String

1. In your Supabase project, go to **Settings** → **Database**
2. Find "Connection string" → **URI** tab
3. Copy the connection string (looks like this):
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.xxx.supabase.co:5432/postgres
   ```
4. Replace `[YOUR-PASSWORD]` with your actual password
5. **Save this connection string** - you'll need it later!

### Step 3: Migrate Your Databases

#### Option A: Using the Migration Script (Recommended)

```bash
# 1. Export your SQLite databases to SQL format
python3 utils/migrate_to_postgres.py data/verb_forms.db verb_forms.sql
python3 utils/migrate_to_postgres.py data/noun_forms.db noun_forms.sql

# This creates two .sql files with all your data
```

#### Option B: Direct Upload via Supabase Dashboard

1. In Supabase, go to **SQL Editor**
2. Click **New Query**
3. Open `verb_forms.sql` in a text editor
4. Copy ALL contents
5. Paste into Supabase SQL Editor
6. Click **Run** (wait for completion)
7. Repeat steps 2-6 for `noun_forms.sql`

**Note:** If files are too large for copy-paste:

```bash
# Split large SQL files
split -l 50000 verb_forms.sql verb_forms_part_
split -l 50000 noun_forms.sql noun_forms_part_

# Upload each part separately in Supabase SQL Editor
```

### Step 4: Verify Database

In Supabase SQL Editor, run:

```sql
-- Check tables
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public';

-- Count records
SELECT 'verbs' as table_name, COUNT(*) FROM verbs
UNION ALL
SELECT 'verb_forms', COUNT(*) FROM verb_forms
UNION ALL
SELECT 'nouns', COUNT(*) FROM nouns
UNION ALL
SELECT 'noun_forms', COUNT(*) FROM noun_forms;
```

You should see all 4 tables with your data!

---

## PART 2: Deploy to Vercel (5-10 minutes)

### Step 1: Prepare Your Repository

```bash
# Make sure all changes are committed
git add -A
git commit -m "Add Streamlit web app for deployment"
git push origin claude/prakrit-games-unified-app-011CUwmGXktVM9YEBYn9QGfs
```

### Step 2: Deploy to Vercel

1. Go to https://vercel.com and sign in with GitHub
2. Click "Add New" → "Project"
3. Import your `prakrit-game` repository
4. Configure project:
   - **Framework Preset:** Other
   - **Build Command:** Leave empty
   - **Output Directory:** Leave empty
   - **Install Command:** `pip install -r requirements_web.txt`

### Step 3: Add Environment Variables

In Vercel project settings → Environment Variables:

1. Add variable:
   - **Key:** `DATABASE_URL`
   - **Value:** (paste your Supabase connection string from Part 1, Step 2)
   - **Environment:** Production, Preview, Development

2. Click "Save"

### Step 4: Deploy

1. Click "Deploy"
2. Wait 2-3 minutes for build to complete
3. Once done, click "Visit" to see your live app!

🎉 **Your app is now live!**

---

## PART 3: Configure Streamlit (for Streamlit Cloud - Alternative)

If you prefer Streamlit Cloud instead of Vercel:

### Deploy to Streamlit Cloud

1. Go to https://streamlit.io/cloud
2. Sign in with GitHub
3. Click "New app"
4. Select your repository: `prakrit-game`
5. Main file path: `streamlit_app.py`
6. Click "Advanced settings"
7. Add secrets:

```toml
# .streamlit/secrets.toml format
DATABASE_URL = "postgresql://postgres:[YOUR-PASSWORD]@db.xxx.supabase.co:5432/postgres"
```

8. Click "Deploy"

---

## 🧪 Testing Your Deployment

1. Visit your deployed URL
2. Try each game:
   - ✅ Form Quiz - can you answer questions?
   - ✅ Word Identification - multiple choice working?
   - ✅ Paradigm Completion - table displays correctly?
   - ✅ Speed Drill - timer works?
   - ✅ Matching Game - can you match items?

3. Test script switching:
   - Change from Devanagari → IAST → ISO → HK
   - Verify text updates correctly

4. Check performance:
   - Questions load quickly?
   - No errors in console?

---

## 🔧 Troubleshooting

### "Database connection failed"

**Fix:**
1. Check your `DATABASE_URL` in Vercel/Streamlit settings
2. Verify password is correct (no special characters that need escaping)
3. Test connection locally:

```bash
# Create .env file
echo "DATABASE_URL=your_connection_string_here" > .env

# Test locally
streamlit run streamlit_app.py
```

### "No data displaying"

**Fix:**
1. Verify database migration completed successfully
2. Run verification queries in Supabase SQL Editor (see Part 1, Step 4)
3. Check table names match exactly: `verbs`, `verb_forms`, `nouns`, `noun_forms`

### "Page not loading"

**Fix:**
1. Check Vercel build logs for errors
2. Verify all dependencies in `requirements_web.txt` are correct
3. Ensure Python version compatibility

### "Slow performance"

**Fix:**
1. Supabase free tier: Good for moderate traffic
2. Consider upgrading Supabase for better performance
3. Add database indexes:

```sql
-- In Supabase SQL Editor
CREATE INDEX IF NOT EXISTS idx_verb_forms_verb_id ON verb_forms(verb_id);
CREATE INDEX IF NOT EXISTS idx_noun_forms_noun_id ON noun_forms(noun_id);
CREATE INDEX IF NOT EXISTS idx_verbs_difficulty ON verbs(difficulty);
CREATE INDEX IF NOT EXISTS idx_nouns_difficulty ON nouns(difficulty);
```

---

## 📊 Monitoring

### Supabase Dashboard

- **Database → Tables:** View your data
- **Database → Logs:** Check query performance
- **Settings → Database:** Monitor size and connections

### Vercel Dashboard

- **Deployments:** See deployment history
- **Analytics:** Track visitors (upgrade for details)
- **Logs:** Debug errors

---

## 🎯 Custom Domain (Optional)

### Add Your Own Domain

**On Vercel:**
1. Go to Project Settings → Domains
2. Add your domain (e.g., `prakrit-games.com`)
3. Follow DNS configuration instructions
4. Wait for DNS propagation (up to 48 hours)

**On Streamlit Cloud:**
- Custom domains require Streamlit for Teams (paid)

---

## 🔐 Security Best Practices

1. **Never commit `.env` file:**
   ```bash
   # Already in .gitignore
   .env
   ```

2. **Use environment variables for all secrets**

3. **Enable Supabase Row Level Security (RLS):**
   ```sql
   -- In Supabase SQL Editor
   ALTER TABLE verbs ENABLE ROW LEVEL SECURITY;
   ALTER TABLE verb_forms ENABLE ROW LEVEL SECURITY;
   ALTER TABLE nouns ENABLE ROW LEVEL SECURITY;
   ALTER TABLE noun_forms ENABLE ROW LEVEL SECURITY;

   -- Allow public read access
   CREATE POLICY "Public read access" ON verbs FOR SELECT USING (true);
   CREATE POLICY "Public read access" ON verb_forms FOR SELECT USING (true);
   CREATE POLICY "Public read access" ON nouns FOR SELECT USING (true);
   CREATE POLICY "Public read access" ON noun_forms FOR SELECT USING (true);
   ```

---

## 💰 Cost Breakdown

All FREE for moderate usage:

| Service | Free Tier | Limits |
|---------|-----------|--------|
| **Supabase** | 500MB database | Enough for 180MB + indexes |
| **Vercel** | Unlimited bandwidth | 100GB bandwidth/month |
| **Streamlit Cloud** | 1GB resources | Good for small apps |

**Total Cost: $0/month** for most educational use cases!

---

## 📈 Scaling Up (When You Grow)

If you get thousands of users:

### Upgrade Supabase ($25/month)
- 8GB database
- Better performance
- Daily backups

### Upgrade Vercel (From $20/month)
- Custom domains
- Advanced analytics
- More bandwidth

---

## ✅ Deployment Checklist

- [ ] Supabase project created
- [ ] Database password saved securely
- [ ] Connection string obtained
- [ ] SQLite databases migrated to PostgreSQL
- [ ] Data verified in Supabase
- [ ] Code pushed to GitHub
- [ ] Vercel project created
- [ ] `DATABASE_URL` environment variable set
- [ ] App deployed successfully
- [ ] All 5 games tested
- [ ] Script switching works
- [ ] Performance acceptable

---

## 🆘 Need Help?

1. **Check build logs** in Vercel dashboard
2. **Test locally** first: `streamlit run streamlit_app.py`
3. **Verify database** connection in Supabase
4. **Check console** for JavaScript errors
5. Review this guide's troubleshooting section

---

## 🎉 Success!

Your Prakrit Games web app is now:
- ✅ Deployed globally
- ✅ Using cloud database
- ✅ Accessible from any device
- ✅ Free to host!

Share your app URL and start learning Prakrit! 🚀

---

**Next Steps:**
- Share the link with learners
- Monitor usage in dashboards
- Consider adding more features
- Collect feedback from users

Enjoy your deployed app! शुभं भवतु! ✨
