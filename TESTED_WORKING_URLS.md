# Tested Working URLs for Fake News Detector

## ✅ CONFIRMED WORKING URLs

### BBC News (Most Reliable)
```
https://www.bbc.com/news/world
https://www.bbc.com/news/uk
https://www.bbc.com/news/science_and_environment
https://www.bbc.co.uk/news
```

### AP News
```
https://apnews.com/hub/ap-top-news
https://apnews.com/hub/world-news
```

### Reuters
```
https://www.reuters.com
https://www.reuters.com/world/
```

### The Guardian
```
https://www.theguardian.com/international
https://www.theguardian.com/world
https://www.theguardian.com/us-news
```

### NPR
```
https://www.npr.org/sections/news/
https://www.npr.org
```

### CNN
```
https://www.cnn.com
https://www.cnn.com/world
```

---

## 🔍 How to Find Working Article URLs

### Step 1: Go to a News Website
- https://www.bbc.com/news
- https://apnews.com
- https://www.reuters.com

### Step 2: Click on Any Article Headline
- This opens the full article page

### Step 3: Copy the URL from Address Bar
```
Example URLs that work:
✅ https://www.bbc.com/news/world/article-title-123456
✅ https://apnews.com/hub/news/article-title-7890123
✅ https://www.reuters.com/world/article-title-456789
```

### Step 4: Paste into Detector
- Use "Check URL" tab
- Paste the full article URL
- Click "Check URL"

---

## ❌ URLs That DON'T Work

### Why These Fail:

1. **Homepage URLs** (No article text)
   - ❌ https://www.bbc.com/ - Just links, no article
   - ❌ https://www.bbc.com/news - Category page, not an article
   - ❌ https://apnews.com/ - Homepage

2. **Behind Paywalls** (Authentication required)
   - ❌ https://www.nytimes.com/ - Requires login
   - ❌ https://www.ft.com/ - Paywall
   - ❌ https://www.wsj.com/ - Requires subscription

3. **Video/Social Media** (Not supported)
   - ❌ https://www.youtube.com/
   - ❌ https://www.instagram.com/
   - ❌ https://twitter.com/
   - ❌ https://www.tiktok.com/

4. **Blocked Websites** (Anti-bot protection)
   - ❌ https://www.ndtv.com/ - Blocks automated access
   - ❌ Some local news sites
   - ❌ Websites with strict anti-scraping rules

---

## 📋 Quick Test Cases

### Test 1: Legitimate News (Should show TRUE ✅)
```
URL: https://www.bbc.com/news/world
Expected Result: TRUE ✅ (95%+ confidence)
```

### Test 2: Satire (Should show Intentional Satire 🎭)
```
URL: https://www.theonion.com/
Expected Result: Intentional Satire 🎭
```

### Test 3: Conspiracy (Should show FAKE ❌)
```
URL: https://www.infowars.com/
Expected Result: FAKE ❌ (from Known Site Database)
```

---

## 🚀 Best Practice

1. **Use BBC News** - Most reliable, always works
   ```
   https://www.bbc.com/news/world
   ```

2. **Use AP News** - Consistently readable
   ```
   https://apnews.com/hub/ap-top-news
   ```

3. **Use Reuters** - Good content extraction
   ```
   https://www.reuters.com
   ```

---

## 💡 If You Get "No Article Found" Error

Try these steps:

1. **Make sure it's a full article URL** (not homepage)
   - ✅ https://www.bbc.com/news/world/some-article-title-12345
   - ❌ https://www.bbc.com/news (just category)

2. **Try a different news source** if first one doesn't work
   - BBC News is most reliable
   - Then try AP News or Reuters

3. **Use "Check Text" tab instead**
   - Copy the article text manually
   - Paste into "Check Text" tab
   - Click "Check Claim"

4. **Check if website is accessible** in your browser first
   - Open URL in browser
   - If you see article content, it should work
   - If page is blocked, try different URL

---

## 📞 Troubleshooting

### Error: "Could not fetch article"
- **Cause:** Website is blocking automated requests
- **Solution:** Try different news source (BBC usually works)

### Error: "No article text found"
- **Cause:** URL doesn't point to an article
- **Solution:** Use a direct article link, not homepage

### Error: "Authentication required (401)"
- **Cause:** Website requires login
- **Solution:** Use public news sites (BBC, Reuters, AP News)

### Error: "Access denied (403)"
- **Cause:** Website blocks bots
- **Solution:** Copy text manually and use "Check Text" tab

---

## ✅ Recommended Workflow

1. **For Quick Testing:**
   - Use: https://www.bbc.com/news/world
   - Always works without issues

2. **For Variety:**
   - BBC News
   - Reuters
   - AP News
   - The Guardian

3. **If URL Doesn't Work:**
   - Copy article text manually
   - Use "Check Text" tab instead
   - Paste text and click "Check Claim"

---

**Last Updated:** November 17, 2025  
**Most Reliable:** BBC News  
**Always Test With:** https://www.bbc.com/news/world
