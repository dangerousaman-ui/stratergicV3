async function fetchJson(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`Request failed: ${response.status}`);
  return response.json();
}

function renderFeed(targetId, items, emptyMessage = 'No updates available right now.') {
  const target = document.getElementById(targetId);
  if (!target) return;

  if (!items || items.length === 0) {
    target.innerHTML = `<div class="empty">${emptyMessage}</div>`;
    return;
  }

  target.innerHTML = items.map(item => `
    <article class="feed-item">
      <div class="feed-meta">${item.source || 'Source'} · ${item.published || ''}</div>
      <h3>${item.title || 'Untitled update'}</h3>
      <a href="${item.link}" target="_blank" rel="noopener">Open story</a>
    </article>
  `).join('');
}

async function loadNews(topic, targetId) {
  const target = document.getElementById(targetId);
  if (target) target.innerHTML = '<div class="loading">Loading live feed…</div>';

  try {
    const payload = await fetchJson(`/api/news?topic=${encodeURIComponent(topic)}`);
    renderFeed(targetId, payload.items);
  } catch (error) {
    if (target) target.innerHTML = `<div class="error">Unable to load feed. ${error.message}</div>`;
  }
}

async function loadWeather() {
  const target = document.getElementById('weather-content');
  target.innerHTML = '<div class="loading">Loading weather…</div>';

  try {
    const payload = await fetchJson('/api/weather');
    const current = payload.data.current || {};
    const daily = payload.data.daily || {};
    target.innerHTML = `
      <div class="metric"><span>Temperature</span><strong>${current.temperature_2m ?? '--'}°C</strong></div>
      <div class="metric"><span>Humidity</span><strong>${current.relative_humidity_2m ?? '--'}%</strong></div>
      <div class="metric"><span>Wind</span><strong>${current.wind_speed_10m ?? '--'} km/h</strong></div>
      <div class="metric"><span>3-day max</span><strong>${daily.temperature_2m_max?.join(' / ') || '--'}</strong></div>
    `;
  } catch (error) {
    target.innerHTML = `<div class="error">Unable to load weather. ${error.message}</div>`;
  }
}

async function loadFinance() {
  const target = document.getElementById('finance-content');
  target.innerHTML = '<div class="loading">Loading finance…</div>';

  try {
    const payload = await fetchJson('/api/finance');
    const rates = payload.rates || {};
    target.innerHTML = `
      <div class="metric"><span>USD / INR</span><strong>${rates.USD_INR ?? '--'}</strong></div>
      <div class="metric"><span>USD / EUR</span><strong>${rates.USD_EUR ?? '--'}</strong></div>
      <div class="metric"><span>BTC / INR</span><strong>${rates.BTC_INR ?? '--'}</strong></div>
      <div class="metric"><span>As of</span><strong>${payload.as_of ?? '--'}</strong></div>
    `;
  } catch (error) {
    target.innerHTML = `<div class="error">Unable to load finance. ${error.message}</div>`;
  }
}

async function loadSatellite() {
  const image = document.getElementById('satellite-image');
  image.alt = 'Loading satellite image';

  try {
    const payload = await fetchJson('/api/satellite');
    image.src = payload.image_url;
    image.alt = `NASA satellite image for ${payload.date}`;
  } catch {
    image.alt = 'Unable to load satellite image';
  }
}

function bindActions() {
  const topicMap = {
    uttarakhand: 'news-uttarakhand',
    laws: 'news-laws',
    cm: 'news-cm',
    pm: 'news-pm',
  };

  document.querySelectorAll('[data-topic]').forEach(button => {
    button.addEventListener('click', () => {
      const topic = button.getAttribute('data-topic');
      loadNews(topic, topicMap[topic]);
    });
  });

  document.getElementById('reload-satellite')?.addEventListener('click', loadSatellite);
}

function registerServiceWorker() {
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/service-worker.js').catch(() => {});
  }
}

window.addEventListener('DOMContentLoaded', () => {
  loadNews('uttarakhand', 'news-uttarakhand');
  loadNews('laws', 'news-laws');
  loadNews('cm', 'news-cm');
  loadNews('pm', 'news-pm');
  loadWeather();
  loadFinance();
  loadSatellite();
  bindActions();
  registerServiceWorker();
});
