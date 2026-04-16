const BASE = '/trends';

export async function fetchTrends(source = null, limit = 50) {
  const params = new URLSearchParams({ limit });
  if (source) params.set('source', source);
  const res = await fetch(`${BASE}/?${params}`);
  if (!res.ok) throw new Error('Failed to fetch trends');
  return res.json();
}

export async function refreshTrends() {
  const res = await fetch(`${BASE}/refresh`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to refresh trends');
  return res.json();
}

export async function fetchTrendSummary() {
  const res = await fetch(`${BASE}/summary`);
  if (!res.ok) throw new Error('Failed to fetch trend summary');
  return res.json();
}
