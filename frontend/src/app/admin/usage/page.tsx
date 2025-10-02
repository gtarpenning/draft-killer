'use client';

/**
 * Admin Usage Dashboard
 * 
 * Shows usage statistics for all users and anonymous sessions.
 * Allows admins to disable/enable user accounts.
 * 
 * Only available in development mode.
 */

import { useEffect, useState } from 'react';
import { getUsageStatistics, toggleUserAccess, UsageStats } from '@/lib/api';
import styles from './usage.module.css';

export default function AdminUsagePage() {
  const [stats, setStats] = useState<UsageStats[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [toggling, setToggling] = useState<string | null>(null);

  const loadStats = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getUsageStatistics();
      setStats(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load usage statistics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStats();
  }, []);

  const handleToggleAccess = async (userId: string) => {
    try {
      setToggling(userId);
      await toggleUserAccess(userId);
      // Reload stats after toggling
      await loadStats();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to toggle user access');
    } finally {
      setToggling(null);
    }
  };

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>Loading usage statistics...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.container}>
        <div className={styles.error}>
          <h2>Error</h2>
          <p>{error}</p>
          <button onClick={loadStats} className={styles.retryButton}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  const authenticatedUsers = stats.filter(s => s.type === 'authenticated');
  const anonymousSessions = stats.filter(s => s.type === 'anonymous');

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <div>
          <h1>Usage Dashboard</h1>
          <a href="/admin/database" style={{ color: 'white', fontSize: '0.9rem', textDecoration: 'underline' }}>
            View Database →
          </a>
        </div>
        <button onClick={loadStats} className={styles.refreshButton}>
          Refresh
        </button>
      </header>

      {/* Authenticated Users Section */}
      <section className={styles.section}>
        <h2>Authenticated Users ({authenticatedUsers.length})</h2>
        <div className={styles.tableContainer}>
          <table className={styles.table}>
            <thead>
              <tr>
                <th>Email</th>
                <th>Status</th>
                <th>Requests</th>
                <th>Last Request</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {authenticatedUsers.map((user) => (
                <tr key={user.user_id}>
                  <td>{user.email}</td>
                  <td>
                    <span className={user.is_active ? styles.statusActive : styles.statusInactive}>
                      {user.is_active ? 'Active' : 'Disabled'}
                    </span>
                  </td>
                  <td>{user.request_count}</td>
                  <td>{user.last_request ? new Date(user.last_request).toLocaleString() : 'N/A'}</td>
                  <td>
                    <button
                      onClick={() => handleToggleAccess(user.user_id!)}
                      disabled={toggling === user.user_id}
                      className={user.is_active ? styles.disableButton : styles.enableButton}
                    >
                      {toggling === user.user_id 
                        ? '...' 
                        : user.is_active 
                          ? 'Disable' 
                          : 'Enable'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {authenticatedUsers.length === 0 && (
            <div className={styles.emptyState}>No authenticated users yet</div>
          )}
        </div>
      </section>

      {/* Anonymous Sessions Section */}
      <section className={styles.section}>
        <h2>Anonymous Sessions ({anonymousSessions.length})</h2>
        <div className={styles.tableContainer}>
          <table className={styles.table}>
            <thead>
              <tr>
                <th>Session ID</th>
                <th>Requests</th>
                <th>Last Request</th>
                <th>User Agent</th>
              </tr>
            </thead>
            <tbody>
              {anonymousSessions.map((session) => (
                <tr key={session.session_id}>
                  <td>
                    <code className={styles.sessionId}>
                      {session.session_id?.substring(0, 12)}...
                    </code>
                  </td>
                  <td>
                    <span className={session.request_count >= 10 ? styles.limitReached : ''}>
                      {session.request_count}/10
                    </span>
                  </td>
                  <td>{session.last_request ? new Date(session.last_request).toLocaleString() : 'N/A'}</td>
                  <td>
                    <span className={styles.userAgent} title={session.user_agent}>
                      {session.user_agent ? session.user_agent.substring(0, 50) + '...' : 'N/A'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {anonymousSessions.length === 0 && (
            <div className={styles.emptyState}>No anonymous sessions yet</div>
          )}
        </div>
      </section>

      {/* Summary Stats */}
      <section className={styles.summary}>
        <div className={styles.stat}>
          <div className={styles.statLabel}>Total Users</div>
          <div className={styles.statValue}>{authenticatedUsers.length}</div>
        </div>
        <div className={styles.stat}>
          <div className={styles.statLabel}>Active Users</div>
          <div className={styles.statValue}>
            {authenticatedUsers.filter(u => u.is_active).length}
          </div>
        </div>
        <div className={styles.stat}>
          <div className={styles.statLabel}>Anonymous Sessions</div>
          <div className={styles.statValue}>{anonymousSessions.length}</div>
        </div>
        <div className={styles.stat}>
          <div className={styles.statLabel}>Total Requests</div>
          <div className={styles.statValue}>
            {stats.reduce((sum, s) => sum + s.request_count, 0)}
          </div>
        </div>
      </section>
    </div>
  );
}

