/**
 * YEDAN AGI - Payhip 收款通知傳令兵
 * 部署於 Cloudflare Workers
 */
export default {
  async fetch(request, env, ctx) {
    // 1. 只接受 POST 請求 (Payhip 會傳 POST 過來)
    if (request.method !== "POST") {
      return new Response("Method Not Allowed", { status: 405 });
    }

    try {
      // 2. 讀取 Payhip 傳來的銷售數據
      const data = await request.json();

      // 3. 提取關鍵資訊
      const email = data.email || "未知買家";
      const price = data.price || "0";
      const currency = data.currency || "USD";
      const productName = data.product_name || "數位商品";
      const txId = data.transaction_id || "N/A";

      // 4. 撰寫戰報 (Telegram 訊息)
      const message = `
💰 *資金入帳確認！*
-------------------------
👤 *買家:* \`${email}\`
💵 *金額:* *${price} ${currency}*
📦 *商品:* ${productName}
🧾 *單號:* \`${txId}\`
-------------------------
🤖 _YEDAN AGI 自動監控系統_
      `;

      // 5. 發送到您的 Telegram (使用環境變數)
      const telegramUrl = `https://api.telegram.org/bot${env.TELEGRAM_BOT_TOKEN}/sendMessage`;

      const tgResponse = await fetch(telegramUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          chat_id: env.TELEGRAM_CHAT_ID,
          text: message,
          parse_mode: "Markdown",
        }),
      });

      if (tgResponse.ok) {
        return new Response("Webhook Received & Telegram Sent", {
          status: 200,
        });
      } else {
        return new Response("Telegram Error", { status: 500 });
      }
    } catch (err) {
      return new Response(`Error: ${err.message}`, { status: 400 });
    }
  },
};
