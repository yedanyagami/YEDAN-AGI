/**
 * YEDAN AGI - Synapse Worker
 * Bridges Tampermonkey (Slow Brain) with Cloudflare KV (Neural Bus)
 * 
 * Deployed to: https://synapse.yagami8095.workers.dev
 */

export default {
  async fetch(request, env, ctx) {
    // CORS headers for Tampermonkey access
    const corsHeaders = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Authorization",
    };

    // Handle preflight
    if (request.method === "OPTIONS") {
      return new Response(null, { headers: corsHeaders });
    }

    const url = new URL(request.url);
    const path = url.pathname;

    try {
      // === HEARTBEAT ===
      if (path === "/heartbeat" && request.method === "POST") {
        await env.YEDAN_KV.put("synapse:heartbeat", new Date().toISOString(), {
          expirationTtl: 120
        });
        return json({ success: true, message: "Heartbeat received" }, corsHeaders);
      }

      // === GET VALUE ===
      if (path.startsWith("/get/") && request.method === "GET") {
        const key = path.replace("/get/", "");
        const value = await env.YEDAN_KV.get(key);
        return json({ success: true, key, value }, corsHeaders);
      }

      // === SET VALUE ===
      if (path.startsWith("/set/") && request.method === "POST") {
        const key = path.replace("/set/", "");
        const body = await request.json();
        const ttl = body.ttl || 3600; // Default 1 hour
        
        await env.YEDAN_KV.put(key, JSON.stringify(body.value), {
          expirationTtl: ttl
        });
        return json({ success: true, key, ttl }, corsHeaders);
      }

      // === SUBMIT TASK ===
      if (path === "/task/submit" && request.method === "POST") {
        const body = await request.json();
        const taskId = `task_${Date.now()}`;
        
        const task = {
          task_id: taskId,
          type: body.type,
          data: body.data,
          status: "pending",
          created_at: new Date().toISOString()
        };
        
        await env.YEDAN_KV.put(`synapse:task:${taskId}`, JSON.stringify(task), {
          expirationTtl: 300
        });
        
        // Add to task queue
        const queue = JSON.parse(await env.YEDAN_KV.get("synapse:task_queue") || "[]");
        queue.push(taskId);
        await env.YEDAN_KV.put("synapse:task_queue", JSON.stringify(queue));
        
        return json({ success: true, task_id: taskId }, corsHeaders);
      }

      // === GET PENDING TASKS (for Tampermonkey to poll) ===
      if (path === "/task/pending" && request.method === "GET") {
        const queue = JSON.parse(await env.YEDAN_KV.get("synapse:task_queue") || "[]");
        const tasks = [];
        
        for (const taskId of queue) {
          const task = await env.YEDAN_KV.get(`synapse:task:${taskId}`);
          if (task) {
            const parsed = JSON.parse(task);
            if (parsed.status === "pending") {
              tasks.push(parsed);
            }
          }
        }
        
        return json({ success: true, tasks }, corsHeaders);
      }

      // === COMPLETE TASK (Tampermonkey submits result) ===
      if (path === "/task/complete" && request.method === "POST") {
        const body = await request.json();
        const taskId = body.task_id;
        
        const taskData = await env.YEDAN_KV.get(`synapse:task:${taskId}`);
        if (!taskData) {
          return json({ success: false, error: "Task not found" }, corsHeaders, 404);
        }
        
        const task = JSON.parse(taskData);
        task.status = "completed";
        task.result = body.result;
        task.completed_at = new Date().toISOString();
        
        await env.YEDAN_KV.put(`synapse:task:${taskId}`, JSON.stringify(task), {
          expirationTtl: 3600
        });
        
        // Store result separately for fast retrieval
        await env.YEDAN_KV.put(`synapse:result:${taskId}`, JSON.stringify(body.result), {
          expirationTtl: 3600
        });
        
        // Remove from queue
        const queue = JSON.parse(await env.YEDAN_KV.get("synapse:task_queue") || "[]");
        const newQueue = queue.filter(id => id !== taskId);
        await env.YEDAN_KV.put("synapse:task_queue", JSON.stringify(newQueue));
        
        return json({ success: true, task_id: taskId }, corsHeaders);
      }

      // === GET TASK RESULT ===
      if (path.startsWith("/task/result/") && request.method === "GET") {
        const taskId = path.replace("/task/result/", "");
        const result = await env.YEDAN_KV.get(`synapse:result:${taskId}`);
        
        if (result) {
          return json({ success: true, task_id: taskId, result: JSON.parse(result) }, corsHeaders);
        }
        return json({ success: false, error: "Result not found" }, corsHeaders, 404);
      }

      // === STATUS CHECK ===
      if (path === "/status" && request.method === "GET") {
        const heartbeat = await env.YEDAN_KV.get("synapse:heartbeat");
        const isAlive = heartbeat && (Date.now() - new Date(heartbeat).getTime()) < 120000;
        
        return json({
          success: true,
          slow_brain_alive: isAlive,
          last_heartbeat: heartbeat,
          timestamp: new Date().toISOString()
        }, corsHeaders);
      }

      // === SET STRATEGY ===
      if (path === "/strategy" && request.method === "POST") {
        const body = await request.json();
        await env.YEDAN_KV.put("synapse:strategy", JSON.stringify({
          strategy: body.strategy,
          reasoning: body.reasoning || "",
          updated_at: new Date().toISOString()
        }));
        return json({ success: true, strategy: body.strategy }, corsHeaders);
      }

      // === GET STRATEGY ===
      if (path === "/strategy" && request.method === "GET") {
        const strategy = await env.YEDAN_KV.get("synapse:strategy");
        return json({ 
          success: true, 
          ...JSON.parse(strategy || '{"strategy":"NEUTRAL"}') 
        }, corsHeaders);
      }

      // === SEND ALERT (to Telegram) ===
      if (path === "/alert" && request.method === "POST") {
        const body = await request.json();
        
        const message = `🔔 *YEDAN SYNAPSE ALERT*\n\n📌 Type: ${body.type}\n💬 ${body.message}`;
        
        await fetch(`https://api.telegram.org/bot${env.TELEGRAM_BOT_TOKEN}/sendMessage`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            chat_id: env.TELEGRAM_CHAT_ID,
            text: message,
            parse_mode: "Markdown"
          })
        });
        
        return json({ success: true, sent: true }, corsHeaders);
      }

      // === OPAL WEBHOOK (receives content from Google Opal) ===
      if (path === "/opal/webhook" && request.method === "POST") {
        const body = await request.json();
        const contentId = `opal_${Date.now()}`;
        
        // Store generated content
        await env.YEDAN_KV.put(`opal:content:${contentId}`, JSON.stringify({
          id: contentId,
          type: body.type || "unknown",
          content: body.content,
          metadata: body.metadata || {},
          created_at: new Date().toISOString()
        }), {
          expirationTtl: 86400 // 24 hours
        });
        
        // Notify via Telegram
        const notifyMsg = `🤖 *OPAL Content Received*\n\nType: ${body.type}\nID: ${contentId}`;
        await fetch(`https://api.telegram.org/bot${env.TELEGRAM_BOT_TOKEN}/sendMessage`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            chat_id: env.TELEGRAM_CHAT_ID,
            text: notifyMsg,
            parse_mode: "Markdown"
          })
        });
        
        return json({ success: true, content_id: contentId, received: body.type }, corsHeaders);
      }

      // === OPAL CONTENT LIST ===
      if (path === "/opal/content" && request.method === "GET") {
        const list = await env.YEDAN_KV.list({ prefix: "opal:content:" });
        const contents = [];
        for (const key of list.keys.slice(0, 10)) {
          const data = await env.YEDAN_KV.get(key.name);
          if (data) contents.push(JSON.parse(data));
        }
        return json({ success: true, contents }, corsHeaders);
      }

      // === SHOPIFY ACTION (cloud-triggered product/price updates) ===
      if (path === "/shopify/action" && request.method === "POST") {
        const body = await request.json();
        const actionId = `action_${Date.now()}`;
        
        // Queue action for processing
        await env.YEDAN_KV.put(`shopify:action:${actionId}`, JSON.stringify({
          id: actionId,
          action: body.action, // "create_product", "update_price", etc.
          payload: body.payload,
          status: "pending",
          created_at: new Date().toISOString()
        }), {
          expirationTtl: 3600
        });
        
        return json({ success: true, action_id: actionId }, corsHeaders);
      }

      // === SHOPIFY ORDER WEBHOOK (receives order notifications) ===
      if (path === "/shopify/order" && request.method === "POST") {
        const body = await request.json();
        const orderId = body.id || `order_${Date.now()}`;
        
        // Extract order details
        const orderData = {
          order_id: orderId,
          order_number: body.order_number,
          total_price: body.total_price,
          currency: body.currency || "USD",
          customer_email: body.email || body.customer?.email,
          products: (body.line_items || []).map(item => ({
            title: item.title,
            quantity: item.quantity,
            price: item.price
          })),
          created_at: body.created_at || new Date().toISOString(),
          received_at: new Date().toISOString()
        };
        
        // Store order in KV
        await env.YEDAN_KV.put(`shopify:order:${orderId}`, JSON.stringify(orderData), {
          expirationTtl: 86400 * 30 // 30 days
        });
        
        // Update daily sales counter
        const today = new Date().toISOString().split('T')[0];
        const dailyKey = `roi:sales:${today}`;
        const dailySales = JSON.parse(await env.YEDAN_KV.get(dailyKey) || '{"count":0,"revenue":0}');
        dailySales.count += 1;
        dailySales.revenue += parseFloat(body.total_price || 0);
        await env.YEDAN_KV.put(dailyKey, JSON.stringify(dailySales), { expirationTtl: 86400 * 90 });
        
        // Send Telegram notification
        const saleMsg = `💰 *NEW SALE!*\n\nOrder: #${body.order_number || orderId}\nAmount: $${body.total_price}\nCustomer: ${orderData.customer_email || 'N/A'}\n\nToday: ${dailySales.count} sales ($${dailySales.revenue.toFixed(2)})`;
        
        await fetch(`https://api.telegram.org/bot${env.TELEGRAM_BOT_TOKEN}/sendMessage`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            chat_id: env.TELEGRAM_CHAT_ID,
            text: saleMsg,
            parse_mode: "Markdown"
          })
        });
        
        return json({ success: true, order_id: orderId, daily_sales: dailySales }, corsHeaders);
      }

      // === SALES HISTORY (get recent orders) ===
      if (path === "/shopify/sales" && request.method === "GET") {
        const list = await env.YEDAN_KV.list({ prefix: "shopify:order:" });
        const orders = [];
        for (const key of list.keys.slice(0, 20)) {
          const data = await env.YEDAN_KV.get(key.name);
          if (data) orders.push(JSON.parse(data));
        }
        return json({ success: true, orders, count: orders.length }, corsHeaders);
      }

      // === DAILY REVENUE (for ROI tracking) ===
      if (path === "/roi/daily" && request.method === "GET") {
        const days = parseInt(url.searchParams.get('days') || '7');
        const revenue = [];
        for (let i = 0; i < days; i++) {
          const date = new Date();
          date.setDate(date.getDate() - i);
          const dateStr = date.toISOString().split('T')[0];
          const data = await env.YEDAN_KV.get(`roi:sales:${dateStr}`);
          revenue.push({
            date: dateStr,
            ...(data ? JSON.parse(data) : { count: 0, revenue: 0 })
          });
        }
        return json({ success: true, revenue }, corsHeaders);
      }

      // === ROI METRICS ===
      if (path === "/roi/metrics" && request.method === "GET") {
        const metrics = await env.YEDAN_KV.get("roi:metrics");
        return json({ success: true, metrics: JSON.parse(metrics || "{}") }, corsHeaders);
      }

      if (path === "/roi/metrics" && request.method === "POST") {
        const body = await request.json();
        await env.YEDAN_KV.put("roi:metrics", JSON.stringify({
          ...body,
          updated_at: new Date().toISOString()
        }));
        return json({ success: true }, corsHeaders);
      }

      // === NEWSLETTER SUBSCRIBE ===
      if (path === "/newsletter/subscribe" && request.method === "POST") {
        const contentType = request.headers.get("content-type") || "";
        let email = "";
        
        if (contentType.includes("application/x-www-form-urlencoded")) {
          const formData = await request.formData();
          email = formData.get("email");
        } else {
          const body = await request.json();
          email = body.email;
        }
        
        if (!email || !email.includes("@")) {
          return json({ success: false, error: "Invalid email" }, corsHeaders);
        }
        
        const subscriberId = `sub_${Date.now()}`;
        await env.YEDAN_KV.put(`newsletter:subscriber:${subscriberId}`, JSON.stringify({
          id: subscriberId,
          email: email,
          source: "landing_page",
          subscribed_at: new Date().toISOString(),
          status: "active"
        }));
        
        // Update subscriber count
        const countData = await env.YEDAN_KV.get("newsletter:count");
        const count = (countData ? parseInt(countData) : 0) + 1;
        await env.YEDAN_KV.put("newsletter:count", count.toString());
        
        // Send Telegram notification
        await fetch(`https://api.telegram.org/bot${env.TELEGRAM_BOT_TOKEN}/sendMessage`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            chat_id: env.TELEGRAM_CHAT_ID,
            text: `📬 *NEW SUBSCRIBER*\n\nEmail: ${email}\nTotal: ${count} subscribers\n\n_AI Insider for Real Estate_`,
            parse_mode: "Markdown"
          })
        });
        
        // Redirect to thank you or return success
        if (contentType.includes("form")) {
          return new Response(null, {
            status: 302,
            headers: { ...corsHeaders, "Location": "https://yedanyagami-io-2.myshopify.com?subscribed=true" }
          });
        }
        
        return json({ success: true, subscriber_id: subscriberId, total: count }, corsHeaders);
      }

      // === NEWSLETTER STATS ===
      if (path === "/newsletter/stats" && request.method === "GET") {
        const count = await env.YEDAN_KV.get("newsletter:count") || "0";
        const list = await env.YEDAN_KV.list({ prefix: "newsletter:subscriber:" });
        return json({ 
          success: true, 
          subscribers: parseInt(count),
          recent: list.keys.length
        }, corsHeaders);
      }

      // Default response
      return json({
        success: true,
        service: "YEDAN Synapse API",
        version: "2.1.0",
        endpoints: [
          "POST /heartbeat",
          "GET /get/{key}",
          "POST /set/{key}",
          "POST /task/submit",
          "GET /task/pending",
          "POST /task/complete",
          "GET /task/result/{id}",
          "GET /status",
          "GET|POST /strategy",
          "POST /alert",
          "POST /opal/webhook",
          "GET /opal/content",
          "POST /shopify/action",
          "POST /shopify/order",
          "GET /shopify/sales",
          "GET /roi/daily",
          "GET|POST /roi/metrics"
        ]
      }, corsHeaders);

    } catch (err) {
      return json({ success: false, error: err.message }, corsHeaders, 500);
    }
  }
};

function json(data, corsHeaders, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "Content-Type": "application/json",
      ...corsHeaders
    }
  });
}
