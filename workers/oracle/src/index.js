/**
 * ORACLE WORKER 🔮
 * Trend Score Predictor (JavaScript Edition)
 * Returns simulated but deterministic trend scores for keywords.
 */

export default {
  async fetch(request) {
    const url = new URL(request.url);
    const path = url.pathname;
    
    // CORS Headers
    const corsHeaders = {
      "Access-Control-Allow-Origin": "*",
      "Content-Type": "application/json"
    };

    if (!path.includes("trend")) {
      return new Response("Oracle Online 🔮", { headers: corsHeaders });
    }

    // Parse keyword from query
    const keyword = url.searchParams.get("keyword") || "AI";
    
    // Generate deterministic but varied score based on keyword hash
    let hash = 0;
    for (let i = 0; i < keyword.length; i++) {
      hash = ((hash << 5) - hash) + keyword.charCodeAt(i);
      hash = hash & hash;
    }
    
    // Base score from hash (20-90)
    const baseScore = 20 + Math.abs(hash % 70);
    
    // Add daily variation (using day of year)
    const dayOfYear = Math.floor((Date.now() - new Date(new Date().getFullYear(), 0, 0)) / 86400000);
    const variation = (dayOfYear % 20) - 10;
    
    const score = Math.max(0, Math.min(100, baseScore + variation));
    
    const data = {
      keyword: keyword,
      score: score,
      status: score > 50 ? "rising" : "stable",
      source: "oracle-worker"
    };
    
    return new Response(JSON.stringify(data), { headers: corsHeaders });
  }
};
