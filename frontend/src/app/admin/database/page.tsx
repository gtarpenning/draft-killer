'use client';

/**
 * Admin Database Viewer
 * 
 * Provides a lightweight table viewer for inspecting the PostgreSQL database.
 * Shows all tables with row counts and allows viewing table data with pagination.
 * 
 * Only available in development mode.
 */

import { useEffect, useState } from 'react';
import { getDatabaseTables, getTableData, TableInfo, TableData } from '@/lib/api';
import styles from './database.module.css';

export default function AdminDatabasePage() {
  const [tables, setTables] = useState<TableInfo[]>([]);
  const [selectedTable, setSelectedTable] = useState<string | null>(null);
  const [tableData, setTableData] = useState<TableData | null>(null);
  const [loading, setLoading] = useState(true);
  const [dataLoading, setDataLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(0);
  const [pageSize] = useState(50);

  const loadTables = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getDatabaseTables();
      setTables(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load database tables');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTables();
  }, []);

  const loadTableData = async (tableName: string, pageNum: number = 0) => {
    try {
      setDataLoading(true);
      setError(null);
      const data = await getTableData(tableName, pageSize, pageNum * pageSize);
      setTableData(data);
      setSelectedTable(tableName);
      setPage(pageNum);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load table data');
    } finally {
      setDataLoading(false);
    }
  };

  const handleTableClick = (tableName: string) => {
    loadTableData(tableName, 0);
  };

  const handleNextPage = () => {
    if (selectedTable && tableData && (page + 1) * pageSize < tableData.total_rows) {
      loadTableData(selectedTable, page + 1);
    }
  };

  const handlePrevPage = () => {
    if (selectedTable && page > 0) {
      loadTableData(selectedTable, page - 1);
    }
  };

  const formatValue = (value: any): string => {
    if (value === null || value === undefined) {
      return 'NULL';
    }
    if (typeof value === 'object') {
      return JSON.stringify(value, null, 2);
    }
    if (typeof value === 'boolean') {
      return value ? 'true' : 'false';
    }
    return String(value);
  };

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>Loading database tables...</div>
      </div>
    );
  }

  if (error && !selectedTable) {
    return (
      <div className={styles.container}>
        <div className={styles.error}>
          <h2>Error</h2>
          <p>{error}</p>
          <button onClick={loadTables} className={styles.retryButton}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  const totalPages = tableData ? Math.ceil(tableData.total_rows / pageSize) : 0;

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <div>
          <h1>Database Viewer</h1>
          <a href="/admin/usage" style={{ color: 'white', fontSize: '0.9rem', textDecoration: 'underline' }}>
            ← Back to Usage Dashboard
          </a>
        </div>
        <button onClick={loadTables} className={styles.refreshButton}>
          Refresh Tables
        </button>
      </header>

      <div className={styles.content}>
        {/* Left sidebar - Table list */}
        <aside className={styles.sidebar}>
          <h2>Tables ({tables.length})</h2>
          <div className={styles.tableList}>
            {tables.map((table) => (
              <button
                key={table.name}
                onClick={() => handleTableClick(table.name)}
                className={`${styles.tableButton} ${
                  selectedTable === table.name ? styles.active : ''
                }`}
              >
                <span className={styles.tableName}>{table.name}</span>
                <span className={styles.rowCount}>{table.row_count} rows</span>
              </button>
            ))}
          </div>
        </aside>

        {/* Main content - Table data */}
        <main className={styles.main}>
          {!selectedTable ? (
            <div className={styles.emptyState}>
              <p>Select a table from the sidebar to view its data</p>
            </div>
          ) : dataLoading ? (
            <div className={styles.loading}>Loading table data...</div>
          ) : error ? (
            <div className={styles.error}>
              <p>{error}</p>
            </div>
          ) : tableData ? (
            <>
              <div className={styles.tableHeader}>
                <h2>{tableData.table_name}</h2>
                <div className={styles.pagination}>
                  <button
                    onClick={handlePrevPage}
                    disabled={page === 0}
                    className={styles.pageButton}
                  >
                    ← Previous
                  </button>
                  <span className={styles.pageInfo}>
                    Page {page + 1} of {totalPages} ({tableData.total_rows} total rows)
                  </span>
                  <button
                    onClick={handleNextPage}
                    disabled={(page + 1) * pageSize >= tableData.total_rows}
                    className={styles.pageButton}
                  >
                    Next →
                  </button>
                </div>
              </div>

              <div className={styles.tableContainer}>
                {tableData.rows.length === 0 ? (
                  <div className={styles.emptyState}>
                    <p>No data in this table</p>
                  </div>
                ) : (
                  <table className={styles.dataTable}>
                    <thead>
                      <tr>
                        <th className={styles.rowNumber}>#</th>
                        {tableData.columns.map((col) => (
                          <th key={col}>{col}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {tableData.rows.map((row, idx) => (
                        <tr key={idx}>
                          <td className={styles.rowNumber}>
                            {page * pageSize + idx + 1}
                          </td>
                          {tableData.columns.map((col) => (
                            <td key={col} className={styles.dataCell}>
                              <div className={styles.cellContent}>
                                {formatValue(row[col])}
                              </div>
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            </>
          ) : null}
        </main>
      </div>
    </div>
  );
}

