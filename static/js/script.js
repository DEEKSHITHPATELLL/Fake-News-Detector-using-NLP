// ============================================
// FAKE NEWS DETECTOR - FRONTEND JAVASCRIPT
// ============================================

const API_BASE_URL = 'http://127.0.0.1:5000/api';

// ============ DOM ELEMENTS ============
const textInput = document.getElementById('textInput');
const urlInput = document.getElementById('urlInput');
const checkBtn = document.getElementById('checkBtn');
const checkUrlBtn = document.getElementById('checkUrlBtn');
const loadingSpinner = document.getElementById('loadingSpinner');
const resultsSection = document.getElementById('resultsSection');
const tabBtns = document.querySelectorAll('.tab-btn');
const tabContents = document.querySelectorAll('.tab');

// ============ TAB SWITCHING ============
tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const tabName = btn.getAttribute('data-tab');
        
        // Remove active from all
        tabBtns.forEach(b => b.classList.remove('active'));
        tabContents.forEach(t => t.classList.remove('active'));
        
        // Add active to clicked
        btn.classList.add('active');
        document.getElementById(tabName).classList.add('active');
        
        // Reset results
        resultsSection.style.display = 'none';
    });
});

// ============ CHECK CLAIM ============
checkBtn.addEventListener('click', async () => {
    const text = textInput.value.trim();
    
    if (!text) {
        alert('Please enter a claim to check');
        return;
    }
    
    if (text.length > 5000) {
        alert('Text is too long (max 5000 characters)');
        return;
    }
    
    await analyzeClaim(text);
});

// ============ CHECK URL ============
checkUrlBtn.addEventListener('click', async () => {
    const url = urlInput.value.trim();
    
    if (!url) {
        alert('Please enter a URL');
        return;
    }
    
    await analyzeUrl(url);
});

// ============ ANALYZE CLAIM ============
async function analyzeClaim(text) {
    try {
        showLoading();
        
        const payload = {
            text: text
        };
        
        const response = await fetch(`${API_BASE_URL}/predict`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        
        if (!response.ok) {
            throw new Error('Server error: ' + response.statusText);
        }
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        displayResults(data);
        
    } catch (error) {
        console.error('Error:', error);
        hideLoading();
        alert('Error: ' + error.message);
    }
}

// ============ ANALYZE URL ============
async function analyzeUrl(url) {
    try {
        showLoading();
        
        // Validate URL format on frontend
        if (!url) {
            hideLoading();
            alert('Please enter a URL');
            return;
        }
        
        if (!url.startsWith('http://') && !url.startsWith('https://')) {
            hideLoading();
            alert('URL must start with http:// or https://\n\nExample: https://www.bbc.com/news/article-title');
            return;
        }
        
        const payload = { url: url };
        
        const response = await fetch(`${API_BASE_URL}/url`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        
        // Try to get the error message from response
        let data;
        try {
            data = await response.json();
        } catch (e) {
            hideLoading();
            alert('Server error: Invalid response format');
            return;
        }
        
        if (!response.ok) {
            hideLoading();
            // Show server error message if available
            if (data.error) {
                alert('Error: ' + data.error);
            } else {
                alert('Server error: ' + response.statusText);
            }
            return;
        }
        
        if (data.error) {
            hideLoading();
            alert('Error: ' + data.error);
            return;
        }
        
        displayResults(data);
        
    } catch (error) {
        console.error('Error:', error);
        hideLoading();
        alert('Error: ' + error.message);
    }
}

// ============ DISPLAY RESULTS ============
function displayResults(data) {
    hideLoading();
    
    // Check if this is a known site (satire, conspiracy, etc.)
    const isKnownSite = data.is_known_site === true;
    const verdictType = data.verdict_type;  // 'satire' or 'fake'
    const isFake = data.label === 0;
    const label = data.prediction;
    const confidence = data.confidence;
    const fakeProb = data.probabilities.fake;
    const trueProb = data.probabilities.true;
    const source = data.decision_source || 'model';
    
    // Update verdict box
    const verdictBox = document.getElementById('verdictBox');
    
    if (isKnownSite) {
        // Special styling for satire sites
        if (verdictType === 'satire') {
            verdictBox.className = 'verdict-box satire';
            const verdictIcon = verdictBox.querySelector('.verdict-icon');
            verdictIcon.innerHTML = '<i class="fas fa-theater-masks"></i>';
            verdictIcon.classList.add('done');
        } else {
            // Fake/conspiracy sites - use fake styling
            verdictBox.className = 'verdict-box fake';
            const verdictIcon = verdictBox.querySelector('.verdict-icon');
            verdictIcon.innerHTML = '<i class="fas fa-times-circle"></i>';
            verdictIcon.classList.add('done');
        }
    } else {
        verdictBox.className = `verdict-box ${isFake ? 'fake' : 'true'}`;
        const verdictIcon = verdictBox.querySelector('.verdict-icon');
        verdictIcon.innerHTML = isFake ? '<i class="fas fa-times-circle"></i>' : '<i class="fas fa-check-circle"></i>';
        verdictIcon.classList.add('done');
    }
    
    document.getElementById('verdictLabel').textContent = label;
    document.getElementById('verdictConfidence').textContent = `${confidence}% Confidence`;
    
    // Update confidence bars (hide for known sites)
    const confidenceSection = document.querySelector('.confidence-section');
    if (isKnownSite) {
        confidenceSection.style.display = 'none';
    } else {
        confidenceSection.style.display = 'block';
        document.getElementById('fakePercent').textContent = fakeProb + '%';
        document.getElementById('truePercent').textContent = trueProb + '%';
        
        const fakeBar = document.getElementById('fakeBar');
        const trueBar = document.getElementById('trueBar');
        
        fakeBar.style.width = '0%';
        trueBar.style.width = '0%';
        
        setTimeout(() => {
            fakeBar.style.width = fakeProb + '%';
            trueBar.style.width = trueProb + '%';
        }, 100);
    }
    
    // Update decision source
    document.getElementById('decisionSource').textContent = source;
    
    // Update WordNet match (hide for known sites)
    const wordnetSection = document.querySelector('.info-grid');
    if (isKnownSite) {
        wordnetSection.style.display = 'none';
    } else {
        wordnetSection.style.display = 'grid';
        if (data.wordnet_hits !== undefined && data.wordnet_total !== undefined) {
            document.getElementById('wordnetMatch').textContent = 
                `${data.wordnet_hits}/${data.wordnet_total} keywords`;
        }
    }
    
    // Update original text
    if (data.text) {
        document.getElementById('originalText').textContent = data.text;
    } else if (data.url) {
        document.getElementById('originalText').textContent = `URL: ${data.url}`;
    }
    
    // Handle API matches
    if (data.api_matches && data.api_matches.length > 0) {
        const apiMatchesSection = document.getElementById('apiMatchesSection');
        const apiMatches = document.getElementById('apiMatches');
        
        apiMatchesSection.style.display = 'block';
        apiMatches.innerHTML = '';
        
        data.api_matches.forEach((match, index) => {
            const matchHtml = `
                <div class="match-item">
                    <div class="match-verdict">
                        <strong>Source ${index + 1}:</strong> ${match.verdict}
                    </div>
                    <div class="match-text">"${match.text}"</div>
                    <a href="${match.url}" target="_blank" class="match-url">
                        <i class="fas fa-external-link-alt"></i> View Full Article
                    </a>
                </div>
            `;
            apiMatches.innerHTML += matchHtml;
        });
    } else {
        document.getElementById('apiMatchesSection').style.display = 'none';
    }
    
    // Show results
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// ============ LOADING SPINNER ============
function showLoading() {
    loadingSpinner.style.display = 'flex';
}

function hideLoading() {
    loadingSpinner.style.display = 'none';
}

// ============ RESET FORM ============
function resetForm() {
    textInput.value = '';
    urlInput.value = '';
    resultsSection.style.display = 'none';
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ============ COPY RESULTS ============
function copyResults() {
    const verdictLabel = document.getElementById('verdictLabel').textContent;
    const verdictConfidence = document.getElementById('verdictConfidence').textContent;
    const decisionSource = document.getElementById('decisionSource').textContent;
    const originalText = document.getElementById('originalText').textContent;
    
    const text = `Fake News Detector Results
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Verdict: ${verdictLabel}
Confidence: ${verdictConfidence}
Decision Source: ${decisionSource}

Claim: "${originalText}"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`;
    
    navigator.clipboard.writeText(text).then(() => {
        alert('Results copied to clipboard!');
    }).catch(err => {
        console.error('Failed to copy:', err);
    });
}

// ============ KEYBOARD SHORTCUTS ============
document.addEventListener('keydown', (e) => {
    // Ctrl+Enter or Cmd+Enter to submit
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        const activeTab = document.querySelector('.tab.active');
        if (activeTab.id === 'text-tab') {
            checkBtn.click();
        } else if (activeTab.id === 'url-tab') {
            checkUrlBtn.click();
        }
    }
});

// ============ SMOOTH SCROLL ============
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth' });
        }
    });
});

// ============ CHECK API HEALTH ============
async function checkApiHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            console.log('✅ API is healthy');
            return true;
        }
    } catch (error) {
        console.error('❌ API connection failed:', error);
        return false;
    }
}

// Check health on page load
window.addEventListener('load', () => {
    checkApiHealth();
});

// ============ EXAMPLE CLAIMS ============
const exampleClaims = [
    'The Earth is flat and scientists are hiding the truth',
    'Vaccines contain microchips that track people',
    'Bill Gates created COVID-19 to control the population',
    'The moon landing was faked by NASA',
    '5G towers spread coronavirus disease',
    'Humans only use 10% of their brain',
    'Climate change is not real',
    'COVID vaccines reduce the risk of severe illness',
];

// Load example on page load (optional)
function loadRandomExample() {
    const example = exampleClaims[Math.floor(Math.random() * exampleClaims.length)];
    textInput.placeholder = `Example: "${example}"`;
}

console.log('🚀 Fake News Detector Frontend Loaded Successfully!');
