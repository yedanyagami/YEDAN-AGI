var __defProp = Object.defineProperty;
var __name = (target, value) => __defProp(target, "name", { value, configurable: true });

// synapse_worker.js
var synapse_worker_default = {
  async fetch(request, env, ctx) {
    const corsHeaders = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Authorization"
    };
    if (request.method === "OPTIONS") {
      return new Response(null, { headers: corsHeaders });
    }
    const url = new URL(request.url);
    const path = url.pathname;
    try {
      if (path === "/heartbeat" && request.method === "POST") {
        await env.YEDAN_KV.put("synapse:heartbeat", (/* @__PURE__ */ new Date()).toISOString(), {
          expirationTtl: 120
        });
        return json({ success: true, message: "Heartbeat received" }, corsHeaders);
      }
      if (path.startsWith("/get/") && request.method === "GET") {
        const key = path.replace("/get/", "");
        const value = await env.YEDAN_KV.get(key);
        return json({ success: true, key, value }, corsHeaders);
      }
      if (path.startsWith("/set/") && request.method === "POST") {
        const key = path.replace("/set/", "");
        const body = await request.json();
        const ttl = body.ttl || 3600;
        await env.YEDAN_KV.put(key, JSON.stringify(body.value), {
          expirationTtl: ttl
        });
        return json({ success: true, key, ttl }, corsHeaders);
      }
      if (path === "/task/submit" && request.method === "POST") {
        const body = await request.json();
        const taskId = `task_${Date.now()}`;
        const task = {
          task_id: taskId,
          type: body.type,
          data: body.data,
          status: "pending",
          created_at: (/* @__PURE__ */ new Date()).toISOString()
        };
        await env.YEDAN_KV.put(`synapse:task:${taskId}`, JSON.stringify(task), {
          expirationTtl: 300
        });
        const queue = JSON.parse(await env.YEDAN_KV.get("synapse:task_queue") || "[]");
        queue.push(taskId);
        await env.YEDAN_KV.put("synapse:task_queue", JSON.stringify(queue));
        return json({ success: true, task_id: taskId }, corsHeaders);
      }
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
        task.completed_at = (/* @__PURE__ */ new Date()).toISOString();
        await env.YEDAN_KV.put(`synapse:task:${taskId}`, JSON.stringify(task), {
          expirationTtl: 3600
        });
        await env.YEDAN_KV.put(`synapse:result:${taskId}`, JSON.stringify(body.result), {
          expirationTtl: 3600
        });
        const queue = JSON.parse(await env.YEDAN_KV.get("synapse:task_queue") || "[]");
        const newQueue = queue.filter((id) => id !== taskId);
        await env.YEDAN_KV.put("synapse:task_queue", JSON.stringify(newQueue));
        return json({ success: true, task_id: taskId }, corsHeaders);
      }
      if (path.startsWith("/task/result/") && request.method === "GET") {
        const taskId = path.replace("/task/result/", "");
        const result = await env.YEDAN_KV.get(`synapse:result:${taskId}`);
        if (result) {
          return json({ success: true, task_id: taskId, result: JSON.parse(result) }, corsHeaders);
        }
        return json({ success: false, error: "Result not found" }, corsHeaders, 404);
      }
      if (path === "/status" && request.method === "GET") {
        const heartbeat = await env.YEDAN_KV.get("synapse:heartbeat");
        const isAlive = heartbeat && Date.now() - new Date(heartbeat).getTime() < 12e4;
        return json({
          success: true,
          slow_brain_alive: isAlive,
          last_heartbeat: heartbeat,
          timestamp: (/* @__PURE__ */ new Date()).toISOString()
        }, corsHeaders);
      }
      if (path === "/strategy" && request.method === "POST") {
        const body = await request.json();
        await env.YEDAN_KV.put("synapse:strategy", JSON.stringify({
          strategy: body.strategy,
          reasoning: body.reasoning || "",
          updated_at: (/* @__PURE__ */ new Date()).toISOString()
        }));
        return json({ success: true, strategy: body.strategy }, corsHeaders);
      }
      if (path === "/strategy" && request.method === "GET") {
        const strategy = await env.YEDAN_KV.get("synapse:strategy");
        return json({
          success: true,
          ...JSON.parse(strategy || '{"strategy":"NEUTRAL"}')
        }, corsHeaders);
      }
      if (path === "/alert" && request.method === "POST") {
        const body = await request.json();
        const message = `\u{1F514} *YEDAN SYNAPSE ALERT*

\u{1F4CC} Type: ${body.type}
\u{1F4AC} ${body.message}`;
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
      if (path === "/opal/webhook" && request.method === "POST") {
        const body = await request.json();
        const contentId = `opal_${Date.now()}`;
        await env.YEDAN_KV.put(`opal:content:${contentId}`, JSON.stringify({
          id: contentId,
          type: body.type || "unknown",
          content: body.content,
          metadata: body.metadata || {},
          created_at: (/* @__PURE__ */ new Date()).toISOString()
        }), {
          expirationTtl: 86400
          // 24 hours
        });
        const notifyMsg = `\u{1F916} *OPAL Content Received*

Type: ${body.type}
ID: ${contentId}`;
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
      if (path === "/opal/content" && request.method === "GET") {
        const list = await env.YEDAN_KV.list({ prefix: "opal:content:" });
        const contents = [];
        for (const key of list.keys.slice(0, 10)) {
          const data = await env.YEDAN_KV.get(key.name);
          if (data) contents.push(JSON.parse(data));
        }
        return json({ success: true, contents }, corsHeaders);
      }
      if (path === "/shopify/action" && request.method === "POST") {
        const body = await request.json();
        const actionId = `action_${Date.now()}`;
        await env.YEDAN_KV.put(`shopify:action:${actionId}`, JSON.stringify({
          id: actionId,
          action: body.action,
          // "create_product", "update_price", etc.
          payload: body.payload,
          status: "pending",
          created_at: (/* @__PURE__ */ new Date()).toISOString()
        }), {
          expirationTtl: 3600
        });
        return json({ success: true, action_id: actionId }, corsHeaders);
      }
      if (path === "/shopify/order" && request.method === "POST") {
        const body = await request.json();
        const orderId = body.id || `order_${Date.now()}`;
        const orderData = {
          order_id: orderId,
          order_number: body.order_number,
          total_price: body.total_price,
          currency: body.currency || "USD",
          customer_email: body.email || body.customer?.email,
          products: (body.line_items || []).map((item) => ({
            title: item.title,
            quantity: item.quantity,
            price: item.price
          })),
          created_at: body.created_at || (/* @__PURE__ */ new Date()).toISOString(),
          received_at: (/* @__PURE__ */ new Date()).toISOString()
        };
        await env.YEDAN_KV.put(`shopify:order:${orderId}`, JSON.stringify(orderData), {
          expirationTtl: 86400 * 30
          // 30 days
        });
        const today = (/* @__PURE__ */ new Date()).toISOString().split("T")[0];
        const dailyKey = `roi:sales:${today}`;
        const dailySales = JSON.parse(await env.YEDAN_KV.get(dailyKey) || '{"count":0,"revenue":0}');
        dailySales.count += 1;
        dailySales.revenue += parseFloat(body.total_price || 0);
        await env.YEDAN_KV.put(dailyKey, JSON.stringify(dailySales), { expirationTtl: 86400 * 90 });
        const saleMsg = `\u{1F4B0} *NEW SALE!*

Order: #${body.order_number || orderId}
Amount: $${body.total_price}
Customer: ${orderData.customer_email || "N/A"}

Today: ${dailySales.count} sales ($${dailySales.revenue.toFixed(2)})`;
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
      if (path === "/shopify/sales" && request.method === "GET") {
        const list = await env.YEDAN_KV.list({ prefix: "shopify:order:" });
        const orders = [];
        for (const key of list.keys.slice(0, 20)) {
          const data = await env.YEDAN_KV.get(key.name);
          if (data) orders.push(JSON.parse(data));
        }
        return json({ success: true, orders, count: orders.length }, corsHeaders);
      }
      if (path === "/roi/daily" && request.method === "GET") {
        const days = parseInt(url.searchParams.get("days") || "7");
        const revenue = [];
        for (let i = 0; i < days; i++) {
          const date = /* @__PURE__ */ new Date();
          date.setDate(date.getDate() - i);
          const dateStr = date.toISOString().split("T")[0];
          const data = await env.YEDAN_KV.get(`roi:sales:${dateStr}`);
          revenue.push({
            date: dateStr,
            ...data ? JSON.parse(data) : { count: 0, revenue: 0 }
          });
        }
        return json({ success: true, revenue }, corsHeaders);
      }
      if (path === "/roi/metrics" && request.method === "GET") {
        const metrics = await env.YEDAN_KV.get("roi:metrics");
        return json({ success: true, metrics: JSON.parse(metrics || "{}") }, corsHeaders);
      }
      if (path === "/roi/metrics" && request.method === "POST") {
        const body = await request.json();
        await env.YEDAN_KV.put("roi:metrics", JSON.stringify({
          ...body,
          updated_at: (/* @__PURE__ */ new Date()).toISOString()
        }));
        return json({ success: true }, corsHeaders);
      }
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
__name(json, "json");
export {
  synapse_worker_default as default
};
//# sourceMappingURL=synapse_worker.js.map
