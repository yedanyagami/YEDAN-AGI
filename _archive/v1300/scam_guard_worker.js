/**
 * YEDAN AGI - Scam Guard Worker
 * REST API for scam detection with KV caching
 */

export default {
  async fetch(request, env, ctx) {
    const corsHeaders = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
    };

    if (request.method === "OPTIONS") {
      return new Response(null, { headers: corsHeaders });
    }

    const url = new URL(request.url);
    const path = url.pathname;

    try {
      // === ANALYZE URL ===
      if (path === "/analyze" && request.method === "POST") {
        const body = await request.json();
        const targetUrl = body.url;
        const text = body.text || "";

        if (!targetUrl && !text) {
          return json({ error: "Provide url or text" }, corsHeaders, 400);
        }

        // Check cache first
        const cacheKey = `scam:${hashCode(targetUrl || text)}`;
        const cached = await env.YEDAN_KV.get(cacheKey);
        if (cached) {
          return json({ ...JSON.parse(cached), cached: true }, corsHeaders);
        }

        // Layer 1: Quick checks
        let result = { trust_score: 50, verdict: "UNKNOWN", layers: [] };

        if (targetUrl) {
          const domain = extractDomain(targetUrl);
          
          // Whitelist check
          if (WHITELIST.has(domain) || domain.endsWith(".gov") || domain.endsWith(".edu")) {
            result = { trust_score: 95, verdict: "LEGIT", reason: "Trusted domain", layers: ["L1"] };
          }
          // Risky TLD check
          else if (RISKY_TLDS.some(tld => domain.endsWith(tld))) {
            result = { trust_score: 25, verdict: "SUSPICIOUS", reason: "Risky TLD", layers: ["L1"] };
          }
        }

        if (text && result.verdict === "UNKNOWN") {
          // Pattern matching
          for (const pattern of SCAM_PATTERNS) {
            if (pattern.test(text)) {
              result = { trust_score: 10, verdict: "SCAM", reason: "Scam pattern detected", layers: ["L1"] };
              break;
            }
          }
        }

        // If still uncertain, use AI (Layer 3)
        if (result.verdict === "UNKNOWN" && text && env.GEMINI_API_KEY) {
          result.layers.push("L3");
          
          const aiResponse = await fetch(
            `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${env.GEMINI_API_KEY}`,
            {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                contents: [{
                  parts: [{
                    text: `Analyze for scam patterns. Reply JSON only: {"verdict":"SCAM/SUSPICIOUS/LEGIT","score":0-100,"reason":"..."}

Content: ${text.slice(0, 1000)}`
                  }]
                }]
              })
            }
          );

          if (aiResponse.ok) {
            const aiData = await aiResponse.json();
            const aiText = aiData.candidates?.[0]?.content?.parts?.[0]?.text || "";
            const jsonMatch = aiText.match(/\{[^{}]*\}/);
            if (jsonMatch) {
              const parsed = JSON.parse(jsonMatch[0]);
              result.trust_score = parsed.score || 50;
              result.verdict = parsed.verdict || "UNKNOWN";
              result.ai_reason = parsed.reason;
            }
          }
        }

        // Final verdict logic
        if (result.trust_score >= 70) result.verdict = "LEGIT";
        else if (result.trust_score >= 40) result.verdict = "SUSPICIOUS";
        else if (result.trust_score < 40 && result.verdict === "UNKNOWN") result.verdict = "SCAM";

        result.timestamp = new Date().toISOString();
        result.url = targetUrl;

        // Cache result
        await env.YEDAN_KV.put(cacheKey, JSON.stringify(result), { expirationTtl: 3600 });

        return json(result, corsHeaders);
      }

      // === QUICK CHECK (URL only, no AI) ===
      if (path === "/quick" && request.method === "GET") {
        const targetUrl = url.searchParams.get("url");
        if (!targetUrl) return json({ error: "url param required" }, corsHeaders, 400);

        const domain = extractDomain(targetUrl);
        
        if (WHITELIST.has(domain)) {
          return json({ status: "SAFE", score: 95 }, corsHeaders);
        }
        if (RISKY_TLDS.some(tld => domain.endsWith(tld))) {
          return json({ status: "RISKY", score: 30 }, corsHeaders);
        }
        return json({ status: "UNKNOWN", score: 50 }, corsHeaders);
      }

      // === STATS ===
      if (path === "/stats" && request.method === "GET") {
        const keys = await env.YEDAN_KV.list({ prefix: "scam:" });
        return json({ 
          cached_analyses: keys.keys.length,
          service: "YEDAN Scam Guard",
          version: "1.0.0"
        }, corsHeaders);
      }

      // Default
      return json({
        service: "YEDAN Scam Guard API",
        endpoints: [
          "POST /analyze - Full analysis {url, text}",
          "GET /quick?url= - Quick whitelist check",
          "GET /stats - Cache statistics"
        ]
      }, corsHeaders);

    } catch (err) {
      return json({ error: err.message }, corsHeaders, 500);
    }
  }
};

// === CONSTANTS ===

const WHITELIST = new Set([
  "google.com", "twitter.com", "x.com", "github.com", "microsoft.com",
  "binance.com", "coinbase.com", "kraken.com", "coingecko.com",
  "bloomberg.com", "reuters.com", "cnn.com", "bbc.com", "wsj.com",
  "etherscan.io", "solscan.io", "dexscreener.com"
]);

const RISKY_TLDS = [".xyz", ".top", ".work", ".click", ".tk", ".ml", ".ga"];

const SCAM_PATTERNS = [
  /send\s+\d+\s*(btc|eth|sol)/i,
  /double\s+your\s+(money|crypto)/i,
  /guaranteed\s+\d+%\s+return/i,
  /connect\s+wallet\s+to\s+(claim|receive)/i,
  /seed\s+phrase|private\s+key/i,
  /urgent|act\s+now|limited\s+time/i
];

// === HELPERS ===

function json(data, corsHeaders, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json", ...corsHeaders }
  });
}

function extractDomain(url) {
  try {
    const parsed = new URL(url.includes("://") ? url : `https://${url}`);
    return parsed.hostname.replace("www.", "");
  } catch {
    return url.toLowerCase();
  }
}

function hashCode(str) {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = ((hash << 5) - hash) + str.charCodeAt(i);
    hash |= 0;
  }
  return Math.abs(hash).toString(16);
}
