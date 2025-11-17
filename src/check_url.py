import argparse
import sys
import os
import logging
import time

# try to import newspaper for robust article extraction; fall back to requests+bs4
try:
    from newspaper import Article
    _HAS_NEWSPAPER = True
except Exception:
    _HAS_NEWSPAPER = False

import requests
from bs4 import BeautifulSoup

# Ensure predict module can be imported when running from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from predict import predict

logging.basicConfig(level=logging.INFO)

# Multiple user agents to rotate
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
]

def extract_with_newspaper(url):
    a = Article(url)
    a.download()
    a.parse()
    return a.title or '', a.text or ''

def extract_with_bs4(url, retries=3):
    """Extract article using BeautifulSoup with simple retry logic"""
    headers = {
        'User-Agent': USER_AGENTS[0],
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }
    
    last_error = None
    for attempt in range(retries):
        try:
            resp = requests.get(url, timeout=15, headers=headers, allow_redirects=True)
            resp.raise_for_status()
            break
        except Exception as e:
            last_error = e
            if attempt < retries - 1:
                logging.warning(f'Attempt {attempt + 1} failed, retrying... ({e})')
                time.sleep(2)
            continue
    else:
        raise last_error if last_error else Exception("Failed to fetch URL after retries")
    
    soup = BeautifulSoup(resp.content, 'html.parser')
    
    # Try multiple content extraction strategies
    # Strategy 1: Look for article tag
    article = soup.find('article')
    if article:
        text = ' '.join(p.get_text(separator=' ', strip=True) for p in article.find_all('p'))
        title_el = soup.find('title')
        title = title_el.get_text() if title_el else ''
        if text.strip():
            return title, text

    # Strategy 2: Look for main content area
    main = soup.find('main')
    if main:
        text = ' '.join(p.get_text(separator=' ', strip=True) for p in main.find_all('p'))
        title_el = soup.find('title')
        title = title_el.get_text() if title_el else ''
        if text.strip():
            return title, text
    
    # Strategy 3: Look for divs with content class
    for div_class in ['content', 'article-content', 'post-content', 'story-content', 'news-content', 'body']:
        content_div = soup.find('div', class_=div_class)
        if content_div:
            text = ' '.join(p.get_text(separator=' ', strip=True) for p in content_div.find_all('p'))
            title_el = soup.find('title')
            title = title_el.get_text() if title_el else ''
            if text.strip():
                return title, text
    
    # Strategy 4: Fallback - gather all paragraphs
    p_texts = [p.get_text(separator=' ', strip=True) for p in soup.find_all('p')]
    if not p_texts:
        return '', ''
    
    combined = ' '.join(p_texts)
    title_el = soup.find('title')
    title = title_el.get_text() if title_el else ''
    return title, combined

def fetch_article(url):
    if _HAS_NEWSPAPER:
        try:
            return extract_with_newspaper(url)
        except Exception as e:
            logging.warning('newspaper extraction failed (%s), falling back to bs4', e)
    # fallback
    try:
        return extract_with_bs4(url)
    except Exception as e:
        logging.error(f'Both newspaper and bs4 extraction failed for {url}: {e}')
        raise

def main():
    parser = argparse.ArgumentParser(description='Fetch a URL or accept text and run the fake-news detector')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--url', help='URL of the news article to check')
    group.add_argument('--text', help='Raw article text to check (enclose in quotes)')
    parser.add_argument('--api', action='store_true', help='Also call the fact-check API')
    args = parser.parse_args()

    if args.url:
        title, article_text = fetch_article(args.url)
        if not article_text.strip():
            print('Could not extract article text from URL')
            return
        print(f'Fetched article title: {title}\n')
        text_to_check = title + '\n' + article_text if title else article_text
    else:
        text_to_check = args.text

    result = predict(text_to_check, use_api=args.api)

    # Pretty print results
    print('\n--- Prediction result ---')
    print(f"Predicted label: {result['predicted_label']} (0=fake,1=true)")
    if result['probabilities']:
        print(f"Probabilities: {result['probabilities']}")
    print(f"WordNet matches: {result['wordnet_hits']}/{result['wordnet_total_tokens']}")
    if args.api:
        print('\nFact-check API result:')
        print(result['factcheck_api'])

if __name__ == '__main__':
    main()
