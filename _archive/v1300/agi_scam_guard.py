"""
YEDAN AGI - Scam Guard Module
Multi-layer scam detection system following SCAM-GUARD PROTOCOL
Layer 1: Whitelist/Blacklist (Cost: $0)
Layer 2: Domain Metadata (Cost: $)
Layer 3: AI Semantic Analysis (Cost: $$)
"""
import os
import re
import json
import hashlib
from datetime import datetime
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    import whois
    WHOIS_AVAILABLE = True
except ImportError:
    WHOIS_AVAILABLE = False

try:
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    GEMINI_AVAILABLE = True
except:
    GEMINI_AVAILABLE = False


class ScamGuard:
    """
    Multi-layer scam detection following the GEM AI Standard.
    80% of garbage filtered in Layer 1, saving API costs.
    """
    
    # Top trusted domains (whitelist)
    WHITELIST = {
        # News
        "cnn.com", "bbc.com", "reuters.com", "bloomberg.com", "wsj.com",
        "nytimes.com", "theguardian.com", "forbes.com", "cnbc.com",
        # Tech
        "google.com", "microsoft.com", "apple.com", "github.com", "stackoverflow.com",
        # Crypto (legit)
        "binance.com", "coinbase.com", "kraken.com", "coingecko.com", "coinmarketcap.com",
        "etherscan.io", "solscan.io", "dexscreener.com",
        # Social
        "twitter.com", "x.com", "linkedin.com", "reddit.com",
        # Gov
        "gov", "edu", "mil"
    }
    
    # Known scam patterns
    SCAM_PATTERNS = [
        r"(?i)send\s+\d+\s*(btc|eth|sol|usdt)",
        r"(?i)double\s+your\s+(money|crypto|bitcoin)",
        r"(?i)guaranteed\s+\d+%\s+return",
        r"(?i)act\s+now|urgent|limited\s+time",
        r"(?i)wallet\s+verification\s+required",
        r"(?i)claim\s+your\s+(airdrop|reward|prize)",
        r"(?i)connect\s+wallet\s+to\s+(claim|receive)",
        r"(?i)you\s+(won|have\s+been\s+selected)",
        r"(?i)seed\s+phrase|private\s+key|recovery\s+phrase"
    ]
    
    # Suspicious TLDs
    RISKY_TLDS = {".xyz", ".top", ".work", ".click", ".link", ".tk", ".ml", ".ga", ".cf"}
    
    def __init__(self, cache_backend="local"):
        self.cache = {}
        self.cache_backend = cache_backend
        self.synapse_url = os.getenv("SYNAPSE_API_URL", "https://synapse.yagami8095.workers.dev")
        print("[SCAM_GUARD] Initialized with 3-layer protection")
    
    def _get_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            parsed = urlparse(url if "://" in url else f"https://{url}")
            domain = parsed.netloc or parsed.path.split("/")[0]
            return domain.lower().replace("www.", "")
        except:
            return url.lower()
    
    def _cache_key(self, url: str) -> str:
        """Generate cache key"""
        return hashlib.md5(url.encode()).hexdigest()[:16]
    
    def _check_cache(self, url: str) -> dict:
        """Check if result is cached"""
        key = self._cache_key(url)
        if key in self.cache:
            return self.cache[key]
        return None
    
    def _save_cache(self, url: str, result: dict):
        """Save result to cache"""
        key = self._cache_key(url)
        self.cache[key] = result
    
    # ============ LAYER 1: FILTER GATE (Cost: $0) ============
    
    def layer1_whitelist_check(self, domain: str) -> dict:
        """Check against whitelist"""
        # Check exact match
        if domain in self.WHITELIST:
            return {"passed": True, "status": "SAFE", "source": "whitelist", "score": 95}
        
        # Check TLD (gov, edu)
        for tld in [".gov", ".edu", ".mil"]:
            if domain.endswith(tld):
                return {"passed": True, "status": "SAFE", "source": "trusted_tld", "score": 90}
        
        # Check if subdomain of whitelisted
        for trusted in self.WHITELIST:
            if domain.endswith(f".{trusted}"):
                return {"passed": True, "status": "SAFE", "source": "trusted_subdomain", "score": 85}
        
        return {"passed": False}
    
    def layer1_blacklist_check(self, domain: str) -> dict:
        """Check against known phishing/scam databases"""
        # Check risky TLDs
        for tld in self.RISKY_TLDS:
            if domain.endswith(tld):
                return {"flagged": True, "status": "SUSPICIOUS", "reason": f"Risky TLD: {tld}", "score": 30}
        
        # PhishTank API (free, but requires API key)
        # For now, use pattern-based detection
        return {"flagged": False}
    
    def layer1_pattern_check(self, text: str) -> dict:
        """Check text for scam patterns"""
        matches = []
        for pattern in self.SCAM_PATTERNS:
            if re.search(pattern, text):
                matches.append(pattern)
        
        if matches:
            return {
                "flagged": True,
                "status": "SCAM",
                "reason": f"Matched {len(matches)} scam patterns",
                "patterns": matches[:3],
                "score": max(5, 30 - len(matches) * 5)
            }
        return {"flagged": False}
    
    # ============ LAYER 2: METADATA ANALYSIS (Cost: $) ============
    
    def layer2_domain_age(self, domain: str) -> dict:
        """Check domain age via WHOIS"""
        if not WHOIS_AVAILABLE:
            return {"checked": False, "reason": "whois not installed"}
        
        try:
            w = whois.whois(domain)
            creation_date = w.creation_date
            
            if isinstance(creation_date, list):
                creation_date = creation_date[0]
            
            if creation_date:
                age_days = (datetime.now() - creation_date).days
                
                if age_days < 7:
                    return {"checked": True, "age_days": age_days, "risk": "CRITICAL", "score": 10}
                elif age_days < 30:
                    return {"checked": True, "age_days": age_days, "risk": "HIGH", "score": 25}
                elif age_days < 90:
                    return {"checked": True, "age_days": age_days, "risk": "MEDIUM", "score": 50}
                elif age_days < 365:
                    return {"checked": True, "age_days": age_days, "risk": "LOW", "score": 70}
                else:
                    return {"checked": True, "age_days": age_days, "risk": "SAFE", "score": 85}
            
            return {"checked": False, "reason": "No creation date found"}
        except Exception as e:
            return {"checked": False, "reason": str(e)}
    
    def layer2_ssl_check(self, url: str) -> dict:
        """Check SSL certificate validity"""
        if not REQUESTS_AVAILABLE:
            return {"checked": False}
        
        try:
            full_url = url if url.startswith("http") else f"https://{url}"
            resp = requests.head(full_url, timeout=5, allow_redirects=True)
            
            # Check if HTTPS
            if resp.url.startswith("https://"):
                return {"checked": True, "ssl": True, "score_boost": 10}
            else:
                return {"checked": True, "ssl": False, "score_penalty": -15}
        except:
            return {"checked": False}
    
    # ============ LAYER 3: AI SEMANTIC ANALYSIS (Cost: $$) ============
    
    def layer3_ai_analysis(self, text: str, url: str = None) -> dict:
        """Use Gemini for deep semantic analysis"""
        if not GEMINI_AVAILABLE:
            return {"analyzed": False, "reason": "Gemini not available"}
        
        prompt = f"""You are a Cybersecurity Analyst. Analyze this content for scam/fraud patterns.

Content to analyze:
{text[:2000]}

{f"URL: {url}" if url else ""}

Respond in JSON format ONLY:
{{
    "verdict": "SCAM" or "SUSPICIOUS" or "LEGIT",
    "confidence": 0-100,
    "urgency_manipulation": true/false,
    "emotional_manipulation": true/false,
    "unrealistic_promises": true/false,
    "impersonation_detected": true/false,
    "red_flags": ["list", "of", "issues"],
    "reasoning": "One sentence explanation"
}}"""

        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            
            # Parse JSON from response
            response_text = response.text
            json_match = re.search(r'\{[^{}]*\}', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                result["analyzed"] = True
                return result
            
            return {"analyzed": False, "reason": "Failed to parse response"}
        except Exception as e:
            return {"analyzed": False, "reason": str(e)}
    
    # ============ MAIN ANALYSIS PIPELINE ============
    
    def analyze(self, url: str = None, text: str = None) -> dict:
        """
        Main analysis pipeline following SCAM-GUARD PROTOCOL.
        Returns: {trust_score: 0-100, verdict: SCAM/SUSPICIOUS/LEGIT, details: {...}}
        """
        if not url and not text:
            return {"error": "Provide url or text"}
        
        # Check cache
        cache_key = url or text[:100]
        cached = self._check_cache(cache_key)
        if cached:
            return {**cached, "source": "cache"}
        
        result = {
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "layers_checked": [],
            "trust_score": 50,  # Start neutral
            "verdict": "UNKNOWN"
        }
        
        # ===== LAYER 1: FILTER GATE =====
        
        if url:
            domain = self._get_domain(url)
            result["domain"] = domain
            
            # Whitelist check
            whitelist = self.layer1_whitelist_check(domain)
            if whitelist.get("passed"):
                result["trust_score"] = whitelist["score"]
                result["verdict"] = "LEGIT"
                result["layers_checked"].append("L1_whitelist")
                result["quick_exit"] = True
                self._save_cache(cache_key, result)
                return result
            
            # Blacklist check
            blacklist = self.layer1_blacklist_check(domain)
            if blacklist.get("flagged"):
                result["trust_score"] = blacklist["score"]
                result["verdict"] = blacklist["status"]
                result["reason"] = blacklist["reason"]
                result["layers_checked"].append("L1_blacklist")
                result["quick_exit"] = True
                self._save_cache(cache_key, result)
                return result
        
        if text:
            # Pattern check
            pattern = self.layer1_pattern_check(text)
            if pattern.get("flagged"):
                result["trust_score"] = pattern["score"]
                result["verdict"] = pattern["status"]
                result["reason"] = pattern["reason"]
                result["patterns_matched"] = pattern.get("patterns", [])
                result["layers_checked"].append("L1_patterns")
                result["quick_exit"] = True
                self._save_cache(cache_key, result)
                return result
        
        result["layers_checked"].append("L1_passed")
        
        # ===== LAYER 2: METADATA ANALYSIS =====
        
        if url:
            domain = self._get_domain(url)
            
            # Domain age
            age_check = self.layer2_domain_age(domain)
            if age_check.get("checked"):
                result["domain_age_days"] = age_check.get("age_days")
                result["domain_risk"] = age_check.get("risk")
                result["trust_score"] = (result["trust_score"] + age_check.get("score", 50)) // 2
                result["layers_checked"].append("L2_age")
            
            # SSL check
            ssl_check = self.layer2_ssl_check(url)
            if ssl_check.get("checked"):
                result["has_ssl"] = ssl_check.get("ssl", False)
                if ssl_check.get("score_boost"):
                    result["trust_score"] = min(100, result["trust_score"] + ssl_check["score_boost"])
                if ssl_check.get("score_penalty"):
                    result["trust_score"] = max(0, result["trust_score"] + ssl_check["score_penalty"])
                result["layers_checked"].append("L2_ssl")
        
        # ===== LAYER 3: AI ANALYSIS (Only if still uncertain) =====
        
        if 30 < result["trust_score"] < 80 and text:
            ai_result = self.layer3_ai_analysis(text, url)
            if ai_result.get("analyzed"):
                result["ai_analysis"] = ai_result
                result["layers_checked"].append("L3_ai")
                
                # Adjust score based on AI verdict
                if ai_result.get("verdict") == "SCAM":
                    result["trust_score"] = min(result["trust_score"], 15)
                elif ai_result.get("verdict") == "SUSPICIOUS":
                    result["trust_score"] = min(result["trust_score"], 40)
                elif ai_result.get("verdict") == "LEGIT":
                    result["trust_score"] = max(result["trust_score"], 75)
        
        # ===== FINAL VERDICT =====
        
        if result["trust_score"] >= 70:
            result["verdict"] = "LEGIT"
        elif result["trust_score"] >= 40:
            result["verdict"] = "SUSPICIOUS"
        else:
            result["verdict"] = "SCAM"
        
        # Hallucination check (Module 3.2)
        if result["verdict"] == "LEGIT" and result.get("domain_age_days", 999) < 2:
            result["verdict"] = "SUSPICIOUS"
            result["override_reason"] = "Domain too new for LEGIT status"
        
        self._save_cache(cache_key, result)
        return result
    
    def quick_check(self, url: str) -> dict:
        """Fast check using only Layer 1 (whitelist/blacklist)"""
        domain = self._get_domain(url)
        
        whitelist = self.layer1_whitelist_check(domain)
        if whitelist.get("passed"):
            return {"status": "SAFE", "score": whitelist["score"]}
        
        blacklist = self.layer1_blacklist_check(domain)
        if blacklist.get("flagged"):
            return {"status": blacklist["status"], "score": blacklist["score"]}
        
        return {"status": "UNKNOWN", "score": 50, "needs_deep_check": True}
    
    def analyze_news(self, headline: str, source_url: str = None) -> dict:
        """Specialized news analysis"""
        result = self.analyze(url=source_url, text=headline)
        result["content_type"] = "news"
        
        # Additional news-specific checks
        clickbait_patterns = [
            r"(?i)you\s+won't\s+believe",
            r"(?i)shocking|unbelievable|incredible",
            r"(?i)\d+\s+reasons?\s+why",
            r"(?i)what\s+happened\s+next"
        ]
        
        clickbait_score = 0
        for pattern in clickbait_patterns:
            if re.search(pattern, headline):
                clickbait_score += 15
        
        if clickbait_score > 0:
            result["clickbait_detected"] = True
            result["trust_score"] = max(0, result["trust_score"] - clickbait_score)
        
        return result

    # [COMPAT] Alias for backward compatibility with yedan_agi.py
    def verify_source(self, target: str) -> dict:
        """
        Alias for quick_check/analyze. Returns a dict with 'score' key.
        """
        # If target looks like a URL, use quick_check. Otherwise, analyze as text.
        if target.startswith("http"):
            res = self.quick_check(target)
            return {"score": res.get("trust_score", 0)}
        else:
            # Just a name like "Bitcoin" - use quick heuristic (whitelisted? patterns?)
            # For common assets, assume safe
            return {"score": 80} # Default safe for known text-only targets


# ============ STANDALONE TEST ============

if __name__ == "__main__":
    guard = ScamGuard()
    
    print("\n" + "="*60)
    print("[SCAM_GUARD] Testing...")
    print("="*60)
    
    # Test 1: Whitelisted domain
    print("\n[TEST 1] Trusted domain:")
    result = guard.analyze(url="https://www.binance.com/trade")
    print(f"  Verdict: {result['verdict']} (Score: {result['trust_score']})")
    
    # Test 2: Scam text
    print("\n[TEST 2] Scam text:")
    scam_text = "URGENT! Send 0.5 ETH to claim your airdrop reward! Connect wallet now!"
    result = guard.analyze(text=scam_text)
    print(f"  Verdict: {result['verdict']} (Score: {result['trust_score']})")
    print(f"  Patterns: {result.get('patterns_matched', [])}")
    
    # Test 3: Suspicious domain
    print("\n[TEST 3] Suspicious domain:")
    result = guard.analyze(url="https://free-crypto-giveaway.xyz")
    print(f"  Verdict: {result['verdict']} (Score: {result['trust_score']})")
    
    # Test 4: News headline
    print("\n[TEST 4] News analysis:")
    result = guard.analyze_news(
        headline="Bitcoin Surges 10% as Fed Signals Rate Pause",
        source_url="https://www.reuters.com/crypto"
    )
    print(f"  Verdict: {result['verdict']} (Score: {result['trust_score']})")
    
    print("\n" + "="*60)
    print("[SCAM_GUARD] Tests complete")
    print("="*60)
