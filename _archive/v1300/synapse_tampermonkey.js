// ==UserScript==
// @name         YEDAN AGI Synapse - Cloudflare Neural Link
// @namespace    https://yedan.agi
// @version      2.0.0
// @description  Connects Antigravity browser to YEDAN Cloud Brain via Cloudflare Workers
// @author       YEDAN AGI System
// @match        https://gemini.google.com/*
// @match        https://www.coingecko.com/*
// @match        https://twitter.com/*
// @match        https://x.com/*
// @grant        GM_xmlhttpRequest
// @grant        GM_getValue
// @grant        GM_setValue
// @grant        GM_notification
// @connect      *.workers.dev
// @connect      *
// ==/UserScript==

(function() {
    'use strict';

    // === CLOUDFLARE CONFIGURATION ===
    const CONFIG = {
        SYNAPSE_API: 'https://synapse.yagami8095.workers.dev',
        
        HEARTBEAT_INTERVAL: 30000,  // 30 seconds
        TASK_CHECK_INTERVAL: 5000,  // 5 seconds
        
        DEBUG: true
    };

    // === STATE ===
    let isInitialized = false;
    let currentTaskId = null;
    let processedTasks = new Set();

    // === LOGGING ===
    function log(msg, type = 'info') {
        if (!CONFIG.DEBUG && type === 'debug') return;
        const prefix = {
            info: '🔵',
            success: '✅',
            error: '❌',
            debug: '🔍',
            task: '📋'
        }[type] || '▪️';
        console.log(`[SYNAPSE] ${prefix} ${msg}`);
    }

    // === API INTERFACE ===
    function apiRequest(endpoint, method = 'GET', body = null) {
        return new Promise((resolve, reject) => {
            GM_xmlhttpRequest({
                method: method,
                url: `${CONFIG.SYNAPSE_API}${endpoint}`,
                headers: {
                    'Content-Type': 'application/json'
                },
                data: body ? JSON.stringify(body) : null,
                onload: (response) => {
                    try {
                        const data = JSON.parse(response.responseText);
                        resolve(data);
                    } catch (e) {
                        resolve({ success: false, error: 'Parse error' });
                    }
                },
                onerror: (err) => reject(err)
            });
        });
    }

    // === GEMINI INTERFACE ===
    function getGeminiInput() {
        return document.querySelector('.ql-editor') || 
               document.querySelector('[contenteditable="true"]');
    }

    function getGeminiResponse() {
        const responses = document.querySelectorAll('[data-message-author-role="model"]');
        if (responses.length > 0) {
            return responses[responses.length - 1].innerText;
        }
        return null;
    }

    function sendToGemini(text) {
        const editor = getGeminiInput();
        if (!editor) {
            log('Gemini input not found', 'error');
            return false;
        }

        editor.innerHTML = `<p>${text}</p>`;
        editor.dispatchEvent(new Event('input', { bubbles: true }));

        setTimeout(() => {
            const sendButton = document.querySelector('[data-test-id="send-button"]') ||
                              document.querySelector('button[aria-label*="Send"]') ||
                              document.querySelector('.send-button');
            if (sendButton) {
                sendButton.click();
                log('Message sent to Gemini', 'success');
            }
        }, 500);

        return true;
    }

    function waitForGeminiResponse(timeout = 60000) {
        return new Promise((resolve) => {
            const startTime = Date.now();
            const initialCount = document.querySelectorAll('[data-message-author-role="model"]').length;

            const checkInterval = setInterval(() => {
                const currentCount = document.querySelectorAll('[data-message-author-role="model"]').length;
                
                if (currentCount > initialCount) {
                    setTimeout(() => {
                        clearInterval(checkInterval);
                        resolve(getGeminiResponse());
                    }, 2000);
                }

                if (Date.now() - startTime > timeout) {
                    clearInterval(checkInterval);
                    resolve(null);
                }
            }, 1000);
        });
    }

    // === COINGECKO DATA EXTRACTION ===
    function extractCoinGeckoData() {
        if (!window.location.hostname.includes('coingecko')) return null;

        try {
            // Trending page
            if (window.location.pathname.includes('trending')) {
                const coins = Array.from(document.querySelectorAll('span.font-bold')).slice(0, 10);
                return {
                    type: 'trending',
                    coins: coins.map(el => el.innerText)
                };
            }

            // Coin page
            const priceEl = document.querySelector('[data-target="price.price"]');
            const changeEl = document.querySelector('[data-target="price.change"]');
            
            if (priceEl) {
                return {
                    type: 'price',
                    price: priceEl.innerText,
                    change: changeEl ? changeEl.innerText : 'N/A'
                };
            }
        } catch (e) {
            log(`CoinGecko extraction error: ${e.message}`, 'error');
        }
        return null;
    }

    // === TASK HANDLERS ===
    async function handleTask(task) {
        const taskId = task.task_id;
        const taskType = task.type;
        const data = task.data || {};

        log(`Handling task: ${taskType} (${taskId})`, 'task');

        // Skip if on wrong page for Gemini tasks
        if (taskType.includes('gemini') && !window.location.hostname.includes('gemini')) {
            log('Wrong page for Gemini task', 'debug');
            return null;
        }

        let prompt = '';
        let result = null;
        
        switch (taskType) {
            case 'news_check':
                prompt = `[YEDAN AGI] Search latest news about: ${data.query}. 
                         Summarize in 2-3 sentences. End with: SENTIMENT: BULLISH/BEARISH/NEUTRAL`;
                break;
            
            case 'chart_analysis':
                prompt = `[YEDAN AGI] Based on ${data.symbol}:
                         - Price: $${data.price}
                         - 24h: ${data.change_24h}%
                         Should we BUY, SELL, or HOLD?
                         Respond: ACTION: BUY/SELL/HOLD with 1 sentence reasoning.`;
                break;
            
            case 'sentiment':
                prompt = `[YEDAN AGI] Current crypto market sentiment? Check Twitter/X.
                         Respond: SENTIMENT: EXTREME_GREED/GREED/NEUTRAL/FEAR/EXTREME_FEAR`;
                break;
            
            case 'strategy_decision':
                const strategies = ['ACCUMULATE_DIP', 'SELL_RALLY', 'NEUTRAL', 'FULL_RISK_ON', 'FULL_RISK_OFF'];
                prompt = `[YEDAN AGI STRATEGIC DECISION]
                         Data: ${JSON.stringify(data)}
                         
                         Choose ONE: ${strategies.join(', ')}
                         
                         STRATEGY: [choice]
                         REASONING: [one sentence]`;
                break;

            case 'extract_coingecko':
                result = extractCoinGeckoData();
                break;
            
            default:
                prompt = `[YEDAN AGI] ${JSON.stringify(data)}`;
        }

        // For Gemini tasks
        if (prompt && window.location.hostname.includes('gemini')) {
            if (sendToGemini(prompt)) {
                const response = await waitForGeminiResponse();
                
                if (response) {
                    result = {
                        raw: response,
                        parsed: parseGeminiResponse(response)
                    };
                }
            }
        }

        // Submit result
        if (result) {
            await apiRequest('/task/complete', 'POST', {
                task_id: taskId,
                result: result
            });
            log(`Task ${taskId} completed`, 'success');

            // Notification
            GM_notification({
                title: 'YEDAN Synapse',
                text: `Task completed: ${taskType}`,
                timeout: 3000
            });
        }

        return result;
    }

    function parseGeminiResponse(response) {
        const parsed = {};
        
        const actionMatch = response.match(/ACTION:\s*(BUY|SELL|HOLD)/i);
        if (actionMatch) parsed.action = actionMatch[1].toUpperCase();
        
        const sentimentMatch = response.match(/SENTIMENT:\s*(EXTREME_GREED|GREED|NEUTRAL|FEAR|EXTREME_FEAR|BULLISH|BEARISH)/i);
        if (sentimentMatch) parsed.sentiment = sentimentMatch[1].toUpperCase();
        
        const strategyMatch = response.match(/STRATEGY:\s*(ACCUMULATE_DIP|SELL_RALLY|NEUTRAL|FULL_RISK_ON|FULL_RISK_OFF)/i);
        if (strategyMatch) parsed.strategy = strategyMatch[1].toUpperCase();
        
        const reasoningMatch = response.match(/REASONING:\s*(.+)/i);
        if (reasoningMatch) parsed.reasoning = reasoningMatch[1].trim();
        
        return parsed;
    }

    // === MAIN LOOPS ===
    async function sendHeartbeat() {
        try {
            await apiRequest('/heartbeat', 'POST');
            log('Heartbeat sent', 'debug');
        } catch (e) {
            log(`Heartbeat failed: ${e}`, 'error');
        }
    }

    async function checkForTasks() {
        try {
            const response = await apiRequest('/task/pending', 'GET');
            
            if (response.success && response.tasks) {
                for (const task of response.tasks) {
                    if (!processedTasks.has(task.task_id)) {
                        processedTasks.add(task.task_id);
                        await handleTask(task);
                    }
                }
            }
        } catch (e) {
            log(`Task check failed: ${e}`, 'error');
        }
    }

    // === UI ===
    function createStatusUI() {
        const container = document.createElement('div');
        container.id = 'synapse-status';
        container.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            background: linear-gradient(135deg, rgba(0,0,0,0.9), rgba(30,30,50,0.9));
            color: #0ff;
            padding: 12px 18px;
            border-radius: 10px;
            font-family: 'Courier New', monospace;
            font-size: 11px;
            z-index: 99999;
            border: 1px solid #0ff;
            box-shadow: 0 0 20px rgba(0,255,255,0.3);
            min-width: 180px;
        `;
        container.innerHTML = `
            <div style="font-weight:bold;margin-bottom:8px;font-size:13px;color:#fff;">
                🧠 YEDAN SYNAPSE
            </div>
            <div id="synapse-status-text" style="color:#0f0;">Initializing...</div>
            <div id="synapse-page" style="color:#888;margin-top:5px;font-size:10px;"></div>
        `;
        document.body.appendChild(container);
        return container;
    }

    function updateStatus(text, isError = false) {
        const statusEl = document.getElementById('synapse-status-text');
        const pageEl = document.getElementById('synapse-page');
        if (statusEl) {
            statusEl.textContent = text;
            statusEl.style.color = isError ? '#f00' : '#0f0';
        }
        if (pageEl) {
            pageEl.textContent = `📍 ${window.location.hostname}`;
        }
    }

    // === INITIALIZATION ===
    async function init() {
        log('Initializing YEDAN Synapse v2.0...');
        
        createStatusUI();
        
        // Start heartbeat loop
        setInterval(sendHeartbeat, CONFIG.HEARTBEAT_INTERVAL);
        await sendHeartbeat();
        
        // Start task checking loop
        setInterval(checkForTasks, CONFIG.TASK_CHECK_INTERVAL);
        
        isInitialized = true;
        updateStatus('🟢 Connected');
        log('YEDAN Synapse initialized', 'success');

        // Auto-extract CoinGecko data if on that site
        if (window.location.hostname.includes('coingecko')) {
            const data = extractCoinGeckoData();
            if (data) {
                await apiRequest('/set/synapse:coingecko', 'POST', { 
                    value: data, 
                    ttl: 300 
                });
                log('CoinGecko data synced', 'success');
            }
        }
    }

    // Wait for page load
    if (document.readyState === 'complete') {
        setTimeout(init, 2000);
    } else {
        window.addEventListener('load', () => setTimeout(init, 2000));
    }

})();
