const API_BASE = 'http://127.0.0.1:8000';
let map, marker;
let predictionHistory = JSON.parse(localStorage.getItem('agriHistory') || '[]');
let compareChartInstance = null;

// ─── STATUS CHECK ─────────────────────────────────────────────
async function checkStatus() {
  const dot = document.querySelector('.status-dot');
  const txt = document.getElementById('statusText');
  try {
    const res = await fetch(`${API_BASE}/`);
    if (res.ok) { dot.classList.add('online'); txt.textContent = 'API Online'; }
    else { dot.classList.remove('online'); txt.textContent = 'API Error'; }
  } catch { dot.classList.remove('online'); txt.textContent = 'API Offline'; }
}
checkStatus();
setInterval(checkStatus, 15000);

// ─── HERO COUNTER ─────────────────────────────────────────────
function updateTotalPredsStat() {
  document.getElementById('totalPredsStat').textContent = predictionHistory.length;
}
updateTotalPredsStat();

// ─── LEAFLET MAP ──────────────────────────────────────────────
function initMap() {
  map = L.map('leafletMap', { zoomControl: true, attributionControl: false }).setView([20.5937, 78.9629], 5);

  L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    maxZoom: 18
  }).addTo(map);

  // Custom green marker
  const greenIcon = L.divIcon({
    html: `<div style="
      background:linear-gradient(135deg,#22c55e,#16a34a);
      width:20px;height:20px;border-radius:50% 50% 50% 0;
      transform:rotate(-45deg);border:2px solid #fff;
      box-shadow:0 2px 12px rgba(34,197,94,0.6)"></div>`,
    iconSize: [20, 20], iconAnchor: [10, 20], className: ''
  });

  map.on('click', (e) => {
    const { lat, lng } = e.latlng;
    setCoords(lat, lng, 'Map');
    if (marker) marker.setLatLng(e.latlng);
    else marker = L.marker(e.latlng, { icon: greenIcon }).addTo(map);
    marker.bindPopup(`<b>📍 Selected Location</b><br/>${lat.toFixed(4)}°N, ${lng.toFixed(4)}°E`).openPopup();
  });
}

function setCoords(lat, lng, source) {
  document.getElementById('latitude').value = lat.toFixed(4);
  document.getElementById('longitude').value = lng.toFixed(4);
  document.getElementById('mapCoords').textContent = `📍 ${source}: ${lat.toFixed(4)}°N, ${lng.toFixed(4)}°E`;
  document.getElementById('latAutoTag').textContent = `via ${source}`;
  document.getElementById('lngAutoTag').textContent = `via ${source}`;
}

initMap();

// ─── GPS LOCATION ─────────────────────────────────────────────
document.getElementById('locateBtn').addEventListener('click', () => {
  const btn = document.getElementById('locateBtn');
  btn.disabled = true;
  btn.querySelector('span').textContent = '📡 Locating...';
  if (!navigator.geolocation) { alert('Geolocation not supported.'); btn.disabled = false; return; }
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      const lat = pos.coords.latitude, lng = pos.coords.longitude;
      map.setView([lat, lng], 10);
      map.fire('click', { latlng: { lat, lng } });
      setCoords(lat, lng, 'GPS');
      btn.disabled = false;
      btn.querySelector('span').textContent = '📡 Use My Location';
    },
    (err) => {
      alert('Location access denied. Click the map manually.');
      btn.disabled = false;
      btn.querySelector('span').textContent = '📡 Use My Location';
    }
  );
});

// ─── FEATURE IMPORTANCE CHART ─────────────────────────────────
function buildFeatureChart() {
  const ctx = document.getElementById('featureChart').getContext('2d');
  const features = ['Precipitation', 'Soil pH', 'Temperature', 'Latitude', 'Longitude', 'Humidity', 'Soil Nutrients', 'Crop Type'];
  const values   = [31.2, 20.5, 17.3, 10.8, 8.4, 5.9, 4.5, 1.4];
  const colors   = values.map(v => v > 25 ? '#22c55e' : v > 15 ? '#4ade80' : v > 10 ? '#86efac' : '#bbf7d0');

  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: features,
      datasets: [{
        label: 'Importance (%)',
        data: values,
        backgroundColor: colors,
        borderRadius: 8,
        borderSkipped: false
      }]
    },
    options: {
      responsive: true,
      indexAxis: 'y',
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: (c) => ` ${c.raw}% importance` } }
      },
      scales: {
        x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#8b9e92', font: { size: 12 } } },
        y: { grid: { display: false }, ticks: { color: '#f1f5f2', font: { size: 13, weight: '600' } } }
      }
    }
  });
}
buildFeatureChart();

// ─── YIELD RATING ─────────────────────────────────────────────
function getYieldRating(yield_val) {
  if (yield_val >= 8)   return { label: '🏆 Excellent Yield', color: '#22c55e' };
  if (yield_val >= 5)   return { label: '✅ Good Yield',      color: '#4ade80' };
  if (yield_val >= 3)   return { label: '🟡 Average Yield',   color: '#fbbf24' };
  return                       { label: '⚠️ Poor Yield',      color: '#f87171' };
}

// ─── MAIN PREDICTION ──────────────────────────────────────────
document.getElementById('predictForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const btn = document.getElementById('predictBtn');
  const btnText = document.querySelector('.btn-text');
  const btnLoader = document.getElementById('btnLoader');
  const resultCard = document.getElementById('resultCard');
  const errorCard = document.getElementById('errorCard');

  btn.disabled = true; btnText.style.display = 'none'; btnLoader.style.display = 'inline-flex';
  resultCard.style.display = 'none'; errorCard.style.display = 'none';

  const payload = {
    temperature:    parseFloat(document.getElementById('temperature').value),
    humidity:       parseFloat(document.getElementById('humidity').value),
    precipitation:  parseFloat(document.getElementById('precipitation').value),
    soil_ph:        parseFloat(document.getElementById('soil_ph').value),
    soil_nutrients: parseFloat(document.getElementById('soil_nutrients').value),
    latitude:       parseFloat(document.getElementById('latitude').value),
    longitude:      parseFloat(document.getElementById('longitude').value),
    crop_type:      document.getElementById('crop_type').value
  };

  try {
    const res = await fetch(`${API_BASE}/api/predict`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload)
    });
    if (!res.ok) { const err = await res.json(); throw new Error(err.detail || `HTTP ${res.status}`); }
    const data = await res.json();

    // Show result
    document.getElementById('yieldValue').textContent = data.predicted_yield.toFixed(2);
    document.getElementById('confidenceVal').textContent = (data.confidence * 100).toFixed(1) + '%';
    document.getElementById('statusVal').textContent = data.status.toUpperCase();
    document.getElementById('cropVal').textContent = payload.crop_type.charAt(0).toUpperCase() + payload.crop_type.slice(1);

    const pct = Math.min(100, Math.max(0, (data.predicted_yield / 15) * 100));
    document.getElementById('yieldBar').style.width = pct + '%';

    const rating = getYieldRating(data.predicted_yield);
    const ratingEl = document.getElementById('yieldRating');
    ratingEl.textContent = rating.label;
    ratingEl.style.color = rating.color;

    resultCard.style.display = 'block';
    resultCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

    // Save to history
    const entry = {
      id: predictionHistory.length + 1,
      crop: payload.crop_type,
      yield: data.predicted_yield.toFixed(2),
      temp: payload.temperature,
      rain: payload.precipitation,
      lat: payload.latitude,
      lng: payload.longitude,
      rating: rating.label,
      time: new Date().toLocaleTimeString()
    };
    predictionHistory.unshift(entry);
    localStorage.setItem('agriHistory', JSON.stringify(predictionHistory));
    updateTotalPredsStat();
    renderHistory();

  } catch (err) {
    document.getElementById('errorMsg').textContent = 'Prediction failed: ' + err.message;
    errorCard.style.display = 'flex';
  } finally {
    btn.disabled = false; btnText.style.display = 'inline'; btnLoader.style.display = 'none';
  }
});

// ─── PREDICTION HISTORY ───────────────────────────────────────
function renderHistory() {
  const body = document.getElementById('historyBody');
  const empty = document.getElementById('historyEmpty');
  const wrap = document.getElementById('historyTableWrap');

  if (predictionHistory.length === 0) {
    empty.style.display = 'block'; wrap.style.display = 'none'; return;
  }
  empty.style.display = 'none'; wrap.style.display = 'block';

  body.innerHTML = predictionHistory.map(e => `
    <tr>
      <td>${e.id}</td>
      <td>🌱 ${e.crop.charAt(0).toUpperCase() + e.crop.slice(1)}</td>
      <td><span class="yield-badge">${e.yield}</span></td>
      <td>${e.temp}°</td>
      <td>${e.rain}mm</td>
      <td>${e.lat}°, ${e.lng}°</td>
      <td>${e.rating}</td>
      <td>${e.time}</td>
    </tr>`).join('');
}
renderHistory();

document.getElementById('clearHistoryBtn').addEventListener('click', () => {
  predictionHistory = [];
  localStorage.removeItem('agriHistory');
  updateTotalPredsStat();
  renderHistory();
});

// ─── CROP COMPARISON ──────────────────────────────────────────
const CROPS = ['rice', 'wheat', 'maize', 'cotton', 'sugarcane', 'potato', 'onion', 'tomato', 'pulses', 'groundnut'];

document.getElementById('compareBtn').addEventListener('click', async () => {
  const btn = document.getElementById('compareBtn');
  const temp = parseFloat(document.getElementById('temperature').value);
  const humidity = parseFloat(document.getElementById('humidity').value);
  const precip = parseFloat(document.getElementById('precipitation').value);
  const ph = parseFloat(document.getElementById('soil_ph').value);
  const nutrients = parseFloat(document.getElementById('soil_nutrients').value);
  const lat = parseFloat(document.getElementById('latitude').value);
  const lng = parseFloat(document.getElementById('longitude').value);

  if ([temp, humidity, precip, ph, nutrients, lat, lng].some(isNaN)) {
    alert('Please fill in all form fields first, then click Compare.');
    return;
  }

  btn.disabled = true;
  btn.textContent = '⏳ Running comparisons...';

  const results = [];
  for (const crop of CROPS) {
    try {
      const res = await fetch(`${API_BASE}/api/predict`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ temperature: temp, humidity, precipitation: precip, soil_ph: ph, soil_nutrients: nutrients, latitude: lat, longitude: lng, crop_type: crop })
      });
      if (res.ok) {
        const d = await res.json();
        results.push({ crop, yield: d.predicted_yield });
      }
    } catch {}
  }

  btn.disabled = false;
  btn.textContent = '🔄 Run Crop Comparison';

  if (results.length === 0) { alert('Could not fetch comparisons. Is the API running?'); return; }

  results.sort((a, b) => b.yield - a.yield);
  const wrap = document.getElementById('compareWrap');
  wrap.style.display = 'block';

  const colors = results.map((_, i) => i === 0 ? '#22c55e' : i === 1 ? '#4ade80' : '#86efac');

  const ctx = document.getElementById('compareChart').getContext('2d');
  if (compareChartInstance) compareChartInstance.destroy();
  compareChartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: results.map(r => r.crop.charAt(0).toUpperCase() + r.crop.slice(1)),
      datasets: [{
        label: 'Predicted Yield (tons/ha)',
        data: results.map(r => r.yield.toFixed(2)),
        backgroundColor: colors,
        borderRadius: 8,
        borderSkipped: false
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: c => ` ${c.raw} tons/ha` } }
      },
      scales: {
        x: { grid: { display: false }, ticks: { color: '#f1f5f2', font: { size: 13, weight: '600' } } },
        y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#8b9e92' }, title: { display: true, text: 'Yield (tons/ha)', color: '#8b9e92' } }
      }
    }
  });

  wrap.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
});
