import { useState, useEffect, useCallback } from 'react';
import { fetchTrends, refreshTrends, fetchTrendSummary } from '../api/trends';

const ACTION_COLORS = {
  'Design now': '#2ecc71',
  'Trending — act fast': '#3498db',
  'Worth watching': '#f39c12',
  'Fading out': '#95a5a6',
};

const DIRECTION_LABEL = {
  rising: '↑ Rising',
  stable: '→ Stable',
  falling: '↓ Falling',
};

function TrendCard({ trend }) {
  const color = ACTION_COLORS[trend.suggested_action] ?? '#ccc';
  return (
    <li
      style={{
        borderLeft: `4px solid ${color}`,
        padding: '10px 14px',
        marginBottom: '8px',
        background: '#f9f9f9',
        borderRadius: '4px',
        listStyle: 'none',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <strong style={{ fontSize: '1rem' }}>{trend.name}</strong>
        <span
          style={{
            background: color,
            color: '#fff',
            padding: '2px 8px',
            borderRadius: '12px',
            fontSize: '0.75rem',
            fontWeight: 'bold',
          }}
        >
          {trend.suggested_action}
        </span>
      </div>
      <div style={{ marginTop: '6px', fontSize: '0.85rem', color: '#555' }}>
        <span>{trend.category}</span>
        <span style={{ margin: '0 8px' }}>|</span>
        <span>{DIRECTION_LABEL[trend.trend_direction] ?? trend.trend_direction}</span>
        <span style={{ margin: '0 8px' }}>|</span>
        <span>Score: {trend.score.toFixed(1)}/100</span>
      </div>
      <div
        style={{
          marginTop: '6px',
          height: '6px',
          background: '#e0e0e0',
          borderRadius: '3px',
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            width: `${trend.score}%`,
            height: '100%',
            background: color,
            transition: 'width 0.4s ease',
          }}
        />
      </div>
    </li>
  );
}

export default function TrendDashboard() {
  const [trends, setTrends] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [trendData, summaryData] = await Promise.all([
        fetchTrends(),
        fetchTrendSummary(),
      ]);
      setTrends(trendData);
      setSummary(summaryData);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
    // Auto-refresh every 30 minutes
    const interval = setInterval(loadData, 30 * 60 * 1000);
    return () => clearInterval(interval);
  }, [loadData]);

  const handleRefresh = async () => {
    setRefreshing(true);
    setError(null);
    try {
      await refreshTrends();
      await loadData();
    } catch (e) {
      setError(e.message);
    } finally {
      setRefreshing(false);
    }
  };

  return (
    <section aria-label="Word Trend Dashboard" style={{ marginTop: '2rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
        <h2 style={{ margin: 0 }}>nene &amp; wolf — Word Trends</h2>
        <button
          onClick={handleRefresh}
          disabled={refreshing || loading}
          style={{
            padding: '6px 14px',
            cursor: refreshing || loading ? 'not-allowed' : 'pointer',
            opacity: refreshing || loading ? 0.6 : 1,
          }}
        >
          {refreshing ? 'Refreshing...' : 'Refresh Now'}
        </button>
      </div>

      {summary && summary.total > 0 && (
        <div
          style={{
            background: '#eef6ff',
            border: '1px solid #c5def7',
            borderRadius: '6px',
            padding: '10px 14px',
            marginBottom: '14px',
            fontSize: '0.88rem',
            display: 'flex',
            gap: '20px',
            flexWrap: 'wrap',
          }}
        >
          <span>
            <strong>Top trend:</strong> {summary.top_trend} ({summary.top_score?.toFixed(1)})
          </span>
          <span>
            <strong>Tracked:</strong> {summary.total} keywords
          </span>
          {summary.last_fetched && (
            <span>
              <strong>Last updated:</strong>{' '}
              {new Date(summary.last_fetched).toLocaleString()}
            </span>
          )}
          {Object.entries(summary.by_action).map(([action, count]) => (
            <span key={action}>
              <strong>{action}:</strong> {count}
            </span>
          ))}
        </div>
      )}

      {error && (
        <p role="alert" style={{ color: '#c0392b' }}>
          {error}
        </p>
      )}

      {loading ? (
        <p>Loading word trends...</p>
      ) : trends.length === 0 ? (
        <p style={{ color: '#777' }}>
          No trend data yet. Click <strong>Refresh Now</strong> to pull the latest word
          &amp; phrase trends from Google.
        </p>
      ) : (
        <ul style={{ padding: 0 }}>
          {trends.map((t) => (
            <TrendCard key={t.id} trend={t} />
          ))}
        </ul>
      )}
    </section>
  );
}
