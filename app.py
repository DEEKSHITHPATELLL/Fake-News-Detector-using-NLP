"""
Flask Web Application for Fake News Detector
Provides REST API endpoints for the frontend to use
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import sys
import os
import traceback
import logging

# Enable detailed logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from predict import predict, explain_prediction
from check_url import fetch_article

app = Flask(__name__)
CORS(app)

# Configure upload folder
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Special categories for known sites
SATIRE_SITES = {
    'theonion.com': 'Intentional Satire 🎭',
    'babylonbee.com': 'Intentional Satire 🎭',
    'thepoke.co.uk': 'Intentional Satire 🎭',
    'betoota.com.au': 'Intentional Satire 🎭',
}

HACKER_WEBSITES = {
    'infowars.com': 'FAKE ❌',
    'davidicke.com': 'FAKE ❌',
    'naturalnews.com': 'FAKE ❌',
    'beforeitsnews.com': 'FAKE ❌',
    'zerohedge.com': 'FAKE ❌',
    'breitbart.com': 'FAKE ❌',
}

# Combine all known problematic sites
KNOWN_SITES = {**SATIRE_SITES, **HACKER_WEBSITES}

# Combine all known problematic sites
KNOWN_SITES = {**SATIRE_SITES, **HACKER_WEBSITES}

def extract_domain(url):
    """Extract domain from URL for site classification"""
    from urllib.parse import urlparse
    try:
        domain = urlparse(url).netloc.lower()
        domain = domain.replace('www.', '')
        return domain
    except:
        return None

def check_known_site(url):
    """Check if URL is a known satire or problematic site"""
    domain = extract_domain(url)
    if domain in KNOWN_SITES:
        return KNOWN_SITES[domain]
    return None

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/predict', methods=['POST'])
def api_predict():
    """
    API endpoint to predict fake news
    PRIMARY: Uses NLP model for prediction (98.4% accurate)
    SECONDARY: Uses fact-check API only if model is uncertain (confidence < 70%) or as verification
    Expected JSON: {"text": "..."}
    """
    try:
        data = request.json
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({'error': 'Empty text provided'}), 400
        
        if len(text) > 5000:
            return jsonify({'error': 'Text too long (max 5000 characters)'}), 400
        
        # PRIMARY: Get prediction from NLP model (without API)
        result = predict(text, use_api=False)
        
        model_confidence = result['probabilities'][result['final_label']] * 100
        
        # SECONDARY: Only call API if model confidence is low (< 70%) OR to verify
        api_matches = []
        api_used_for_verdict = False
        
        if model_confidence < 70:  # Model is uncertain, check API
            api_result = predict(text, use_api=True)
            if api_result['decision_source'] == 'api' and api_result['api_label'] is not None:
                # API found a confident match, use it
                result = api_result
                api_used_for_verdict = True
            if api_result['factcheck_api']:
                matched_claims = api_result['factcheck_api'].get('matched_claims', [])
                if matched_claims:
                    for claim in matched_claims[:5]:
                        api_matches.append({
                            'text': claim.get('text', '')[:150],
                            'verdict': claim.get('verdict', 'No verdict'),
                            'url': claim.get('url', '')
                        })
        else:
            # Model is confident, still fetch API data for reference (non-blocking)
            try:
                api_result = predict(text, use_api=True)
                if api_result['factcheck_api']:
                    matched_claims = api_result['factcheck_api'].get('matched_claims', [])
                    if matched_claims:
                        for claim in matched_claims[:3]:  # Only top 3 for reference
                            api_matches.append({
                                'text': claim.get('text', '')[:150],
                                'verdict': claim.get('verdict', 'No verdict'),
                                'url': claim.get('url', '')
                            })
            except:
                pass  # API error doesn't affect model prediction
        
        # Simplify result for frontend
        response = {
            'text': result['text'],
            'prediction': 'FAKE ❌' if result['final_label'] == 0 else 'TRUE ✅',
            'label': result['final_label'],
            'confidence': round(result['probabilities'][result['final_label']] * 100, 1),
            'probabilities': {
                'fake': round(result['probabilities'][0] * 100, 1),
                'true': round(result['probabilities'][1] * 100, 1)
            },
            'decision_source': 'NLP Model' if not api_used_for_verdict else 'API Verification (Model uncertain)',
            'wordnet_hits': result['wordnet_hits'],
            'wordnet_total': result['wordnet_total_tokens'],
            'model_confidence': round(model_confidence, 1),
            'api_matches': api_matches,
            'api_count': len(api_matches),
        }
        
        return jsonify(response), 200
    
    except Exception as e:
        logger.error(f"Error in /api/predict: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/api/explain', methods=['POST'])
def api_explain():
    """
    API endpoint to explain prediction
    Expected JSON: {"text": "..."}
    """
    try:
        data = request.json
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({'error': 'Empty text provided'}), 400
        
        # Get explanation
        explanation = explain_prediction(text, top_n=10)
        
        return jsonify(explanation), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/url', methods=['POST'])
def api_url():
    """
    API endpoint to fetch and predict from URL
    PRIMARY: Uses NLP model for prediction
    SECONDARY: Uses fact-check API only if model is uncertain
    Expected JSON: {"url": "..."}
    """
    try:
        logger.info(f"Received /api/url request")
        logger.info(f"Content-Type: {request.content_type}")
        logger.info(f"Raw data: {request.get_data()[:200]}")
        
        try:
            data = request.json
            logger.info(f"Parsed JSON: {data}")
        except Exception as json_err:
            logger.error(f"JSON parse error: {json_err}")
            return jsonify({'error': 'Invalid JSON format. Please send {"url": "your-url-here"}'}), 400
        
        if data is None:
            return jsonify({'error': 'No JSON data provided. Please send {"url": "your-url-here"}'}), 400
            
        url = data.get('url', '').strip()
        logger.info(f"URL received: {url}")
        
        if not url:
            return jsonify({'error': 'Empty URL provided. Please provide a URL.'}), 400
        
        # Validate URL format
        if not (url.startswith('http://') or url.startswith('https://')):
            return jsonify({'error': f'Invalid URL format. URL must start with http:// or https://. You provided: {url[:50]}...'}), 400
        
        # CHECK: Known satire or problematic sites first
        known_site_category = check_known_site(url)
        if known_site_category:
            # Determine if it's satire or fake content
            is_satire = any(url.lower().find(site) != -1 for site in SATIRE_SITES.keys())
            verdict_type = 'satire' if is_satire else 'fake'
            
            return jsonify({
                'url': url,
                'prediction': known_site_category,
                'label': -1 if is_satire else 0,  # -1 for satire, 0 for fake
                'confidence': 100.0,
                'probabilities': {'fake': 0 if is_satire else 100, 'true': 0},
                'decision_source': 'Known Site Database 🗂️',
                'api_matches': [],
                'api_count': 0,
                'is_known_site': True,
                'verdict_type': verdict_type,
            }), 200
        
        # Fetch article (returns tuple: title, text)
        try:
            title, article_text = fetch_article(url)
        except Exception as fetch_error:
            logger.error(f"Error fetching article from {url}: {str(fetch_error)}")
            error_msg = str(fetch_error).lower()
            
            # Provide helpful error messages based on error type
            if 'youtube' in url.lower() or 'youtu.be' in url.lower():
                return jsonify({'error': 'YouTube URLs are not supported. Please provide a news article URL.'}), 400
            elif any(domain in url.lower() for domain in ['tiktok', 'instagram', 'facebook', 'twitter', 'x.com', 'reddit', 'linkedin', 'snapchat', 'twitch', 'spotify', 'pinterest']):
                return jsonify({'error': 'Social media and video URLs are not supported. Please provide a news article URL.'}), 400
            elif 'timeout' in error_msg or 'connection' in error_msg:
                return jsonify({'error': 'Connection timeout. The website may be blocking requests or is unreachable.'}), 400
            elif '403' in error_msg or 'forbidden' in error_msg:
                return jsonify({'error': 'Access denied (403 Forbidden). The website is blocking automated requests. Try copying the article text and using "Check Text" tab instead.'}), 403
            elif '401' in error_msg:
                return jsonify({'error': 'Authentication required (401). Please provide a public URL.'}), 401
            elif '404' in error_msg or 'not found' in error_msg:
                return jsonify({'error': 'Article not found (404 error). Please check the URL is correct and still exists.'}), 404
            else:
                return jsonify({'error': f'Could not fetch article from this URL. Details: {str(fetch_error)[:100]}'}), 400
        
        if not article_text or not article_text.strip():
            return jsonify({'error': 'No article text found. The URL may not contain readable news content. Try a direct article link or use "Check Text" tab instead.'}), 400
        
        # Combine title and text for better analysis
        combined_text = (title + ' ' + article_text).strip() if title else article_text
        
        # PRIMARY: Get prediction from NLP model (without API)
        result = predict(combined_text, use_api=False)
        
        model_confidence = result['probabilities'][result['final_label']] * 100
        
        # SECONDARY: Only call API if model confidence is low (< 70%)
        api_matches = []
        api_used_for_verdict = False
        
        if model_confidence < 70:  # Model is uncertain, check API
            try:
                api_result = predict(combined_text, use_api=True)
                if api_result['decision_source'] == 'api' and api_result['api_label'] is not None:
                    result = api_result
                    api_used_for_verdict = True
                if api_result['factcheck_api']:
                    matched_claims = api_result['factcheck_api'].get('matched_claims', [])
                    if matched_claims:
                        for claim in matched_claims[:5]:
                            api_matches.append({
                                'text': claim.get('text', '')[:150],
                                'verdict': claim.get('verdict', 'No verdict'),
                                'url': claim.get('url', '')
                            })
            except:
                pass  # API error doesn't block the prediction
        
        response = {
            'url': url,
            'article_length': len(combined_text),
            'prediction': 'FAKE ❌' if result['final_label'] == 0 else 'TRUE ✅',
            'label': result['final_label'],
            'confidence': round(result['probabilities'][result['final_label']] * 100, 1),
            'probabilities': {
                'fake': round(result['probabilities'][0] * 100, 1),
                'true': round(result['probabilities'][1] * 100, 1)
            },
            'decision_source': 'NLP Model' if not api_used_for_verdict else 'API Verification (Model uncertain)',
            'api_matches': api_matches,
            'api_count': len(api_matches),
        }
        
        return jsonify(response), 200
    
    except Exception as e:
        logger.error(f"Error in /api/url: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'Fake News Detector API is running'}), 200

if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port=5000)
