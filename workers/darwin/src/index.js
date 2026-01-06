/**
 * DARWIN WORKER 🧬
 * The Evolutionary Engine of YEDAN (Cloudflare Edition).
 * Replaces local modules/darwin.py
 */

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname;

    // CORS Headers
    const corsHeaders = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
    };

    if (request.method === "OPTIONS") {
      return new Response("OK", { headers: corsHeaders });
    }

    try {
      // 1. GET /strategy?task=reddit_reply
      if (request.method === "GET" && path === "/strategy") {
        const taskType = url.searchParams.get("task") || "default";
        
        // Get Genome from KV (or use default if empty)
        let genome = await env.GENOME.get("prompts", { type: "json" });
        if (!genome) genome = DEFAULT_GENOME;

        const strategy = selectStrategy(genome, taskType);
        
        return new Response(JSON.stringify(strategy), {
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
      }

      // 2. POST /feedback { task: "reddit_reply", name: "sassy", success: true }
      if (request.method === "POST" && path === "/feedback") {
        const body = await request.json();
        const { task, name, success } = body;

        let genome = await env.GENOME.get("prompts", { type: "json" });
        if (!genome) genome = DEFAULT_GENOME;

        // Update Stats
        if (genome[task] && genome[task][name]) {
          const gene = genome[task][name];
          gene.trials = (gene.trials || 0) + 1;
          if (success) gene.wins = (gene.wins || 0) + 1;
          
          // Save back to KV
          await env.GENOME.put("prompts", JSON.stringify(genome));
          
          return new Response(JSON.stringify({ status: "updated", gene }), {
            headers: { ...corsHeaders, "Content-Type": "application/json" },
          });
        }
        
        return new Response(JSON.stringify({ error: "Gene not found" }), { status: 404, headers: corsHeaders });
      }

      return new Response("Darwin Online 🧬", { headers: corsHeaders });

    } catch (e) {
      return new Response(JSON.stringify({ error: e.message }), { status: 500, headers: corsHeaders });
    }
  },
};

// --- Logic ---

function selectStrategy(genome, taskType) {
  // Defensive 
  if (!genome[taskType]) {
    return { name: "default", text: "You are a helpful assistant." };
  }

  const strategies = genome[taskType];
  const candidates = Object.keys(strategies).filter(k => strategies[k].active !== false);

  if (candidates.length === 0) {
    return { name: "default", text: "You are a helpful assistant." };
  }

  // Epsilon-Greedy: 10% Exploration
  const EPSILON = 0.1;
  let choice;

  if (Math.random() < EPSILON) {
    // Explore
    choice = candidates[Math.floor(Math.random() * candidates.length)];
  } else {
    // Exploit (Best Win Rate)
    choice = candidates.reduce((best, current) => {
      const bestRate = getWinRate(strategies[best]);
      const currRate = getWinRate(strategies[current]);
      return currRate > bestRate ? current : best;
    }, candidates[0]);
  }

  return {
    name: choice,
    text: strategies[choice].text,
    win_rate: getWinRate(strategies[choice])
  };
}

function getWinRate(gene) {
  return (gene.wins || 0) / ((gene.trials || 0) + 1);
}

const DEFAULT_GENOME = {
  "reddit_reply": {
    "sassy_friend": {
      "text": "You are a sassy, knowledgeable friend. Keep it short, use slang, but give real value.",
      "wins": 5, "trials": 10, "active": true
    },
    "professional_helper": {
      "text": "You are a professional customer support agent. Be polite, concise, and helpful.",
      "wins": 2, "trials": 8, "active": true
    }
  },
  "shopify_product_desc": {
    "value_first": {
      "text": "Focus on the problem this product solves. Use bullet points.",
      "wins": 0, "trials": 0, "active": true
    },
    "scarcity_driven": {
      "text": "Emphasize limited time and high demand. Create urgency.",
      "wins": 0, "trials": 0, "active": true
    }
  }
};
