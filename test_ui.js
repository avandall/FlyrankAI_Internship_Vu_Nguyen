const { JSDOM } = require('jsdom');
const fs = require('fs');
const html = fs.readFileSync('capstone/AI_Image/static/index.html', 'utf-8');
const dom = new JSDOM(html, { runScripts: "dangerously", url: "http://localhost:8002/" });
const window = dom.window;

window.onerror = function(msg, url, line, col, error) {
    console.error("JSDOM Error:", msg, line, col, error);
};

// Mock fetch
window.fetch = async (url, options) => {
    console.log('Fetching:', url);
    if (url.includes('/api/images')) return { json: async () => ({images: [{filename: 'test.jpg'}]}), ok: true };
    if (url.includes('/images/reviews')) return { json: async () => ({reviews: []}), ok: true };
    if (url.includes('/metrics/precision')) return { json: async () => ({precision_percent: '10%', total_reviews: 1}), ok: true };
    if (url.includes('/api/costs')) return { json: async () => ({total_cost_usd: '$0'}), ok: true };
    return { json: async () => ({}), ok: true };
};

setTimeout(() => {
    console.log("Calling showTab('library')");
    try {
        window.showTab('library');
    } catch(e) {
        console.error("showTab library error:", e);
    }
    setTimeout(() => {
        console.log("Library HTML:", window.document.getElementById('image-library-grid').innerHTML.substring(0, 100));
        console.log("Calling showTab('metrics')");
        try {
            window.showTab('metrics');
        } catch(e) {
            console.error("showTab metrics error:", e);
        }
        setTimeout(() => {
            console.log("Metrics HTML:", window.document.getElementById('precision-stats').innerHTML.substring(0, 100));
        }, 1000);
    }, 1000);
}, 1000);
