# Supported URLs Guide

## ✅ Supported News Websites

The Fake News Detector works with most news article URLs. Here are some popular supported sites:

### **Major News Networks**
- **NDTV** - https://www.ndtv.com/
- **BBC News** - https://www.bbc.com/news
- **Reuters** - https://www.reuters.com
- **AP News** - https://apnews.com
- **The Guardian** - https://www.theguardian.com
- **NPR** - https://www.npr.org
- **CNN** - https://www.cnn.com
- **Times of India** - https://timesofindia.indiatimes.com
- **Indian Express** - https://indianexpress.com
- **The Hindu** - https://www.thehindu.com

### **How to Get the Best Results:**

1. **Use Direct Article URLs** (Best)
   ```
   ✅ https://www.ndtv.com/india/article-about-something-123456
   ✅ https://www.theguardian.com/world/2024/article-title
   ✅ https://apnews.com/hub/article-title-123456
   ```

2. **Avoid Homepage or Category URLs** (May not work)
   ```
   ❌ https://www.ndtv.com/ (homepage)
   ❌ https://www.ndtv.com/india (category page)
   ❌ https://www.theguardian.com/world (section page)
   ```

3. **Full Article URLs work best**
   - The article should have readable text
   - Should have a clear title
   - Must be publicly accessible

---

## ❌ NOT Supported (Won't Work)

### **Video Platforms**
- YouTube - https://www.youtube.com/channel/...
- TikTok - https://www.tiktok.com/
- Twitch - https://www.twitch.tv/

### **Social Media**
- Instagram - https://www.instagram.com/
- Facebook - https://www.facebook.com/
- Twitter/X - https://www.twitter.com/ or https://x.com/
- Reddit - https://www.reddit.com/
- LinkedIn - https://www.linkedin.com/
- Snapchat - https://www.snapchat.com/
- Pinterest - https://www.pinterest.com/

### **Why Not?**
These platforms contain:
- Video content (not text-based)
- Social media posts (not full articles)
- User-generated content
- Non-article formats

---

## 🔍 How to Find Article URLs

### **From NDTV:**
1. Go to https://www.ndtv.com/
2. Click on any news story/headline
3. Copy the full article URL
4. Paste it in the detector

Example: `https://www.ndtv.com/india/article-title-here-123456`

### **From Other News Sites:**
1. Visit the news website
2. Search for or browse to an article
3. Click on the article headline to open it fully
4. Copy the URL from address bar
5. Paste it in the detector

---

## 📋 Example URLs to Test

### **Legitimate News (Should show TRUE ✅)**
- https://www.ndtv.com/india/
- https://www.bbc.com/news
- https://apnews.com
- https://www.reuters.com

### **Satire Sites (Should show Intentional Satire 🎭)**
- https://www.theonion.com/
- https://babylonbee.com/

### **Conspiracy/Misinformation (Should show FAKE ❌)**
- https://www.infowars.com/
- https://davidicke.com/
- https://naturalnews.com/

---

## 🛠️ Troubleshooting

### **Error: "Could not fetch article"**
- **Solution:** Make sure you're using a direct article URL, not homepage
- **Example:** Instead of `ndtv.com`, use `ndtv.com/india/article-title-123`

### **Error: "Connection timeout"**
- **Solution:** The website may be blocking automated requests
- **Tip:** Wait a moment and try again, or try a different article

### **Error: "No article text found"**
- **Solution:** The URL doesn't contain readable article content
- **Tip:** Make sure you copied a full article link, not just a section page

### **Error: "YouTube URLs are not supported"**
- **Solution:** This tool is for news articles only, not videos
- **Tip:** If the video has a transcript, copy the text and use the "Check Text" tab instead

### **Error: "Access denied (403)"**
- **Solution:** The website is blocking automated access
- **Tip:** Try a different article from the same site, or use a different news source

---

## 💡 Pro Tips

1. **Bookmark News Sites** - Keep links to your favorite news sources handy

2. **Use Direct Links** - Always copy the full article URL, not category URLs

3. **Check Multiple Sources** - Compare results from different news outlets for the same story

4. **Text vs URL** - If URL doesn't work, copy the article text and use "Check Text" tab

5. **Recent Articles** - The model works best with current news (trained on recent articles)

---

## 📞 Still Not Working?

If you're still having issues:

1. Verify the URL starts with `http://` or `https://`
2. Make sure it's a text-based news article (not video/social media)
3. Try copying the article text manually and use the "Check Text" tab instead
4. Check if the website is accessible in your browser first
5. Try with a different news source

---

**Last Updated:** November 17, 2025  
**Supported URL Types:** News Articles, Blog Posts, Wikipedia  
**Not Supported:** Videos, Social Media, Paywalled Content
