# Database Viewer

A lightweight PostgreSQL database table viewer for the admin interface.

## Overview

The Database Viewer provides a web-based interface to inspect the state of your PostgreSQL database in development mode. It allows you to:

- View all database tables with row counts
- Browse table data with pagination
- Inspect column names and data types
- View actual values including UUIDs, timestamps, JSON, etc.

## Access

The database viewer is available at:

```
http://localhost:3000/admin/database
```

**Important:** This feature is only available in development mode for security reasons.

## Features

### Table List
- Left sidebar shows all database tables
- Displays row count for each table
- Click any table to view its data

### Table Data View
- Shows column names in a table header
- Displays up to 50 rows per page with pagination
- Supports scrolling for large data sets
- Formats values appropriately:
  - NULL values shown as "NULL"
  - Timestamps in ISO format
  - UUIDs as strings
  - JSON objects pretty-printed
  - Boolean values as "true"/"false"

### Pagination
- Navigate through large tables with Previous/Next buttons
- Shows current page and total pages
- Displays total row count

## Backend API

Two new endpoints were added to the admin API:

### GET `/api/admin/database/tables`

Returns a list of all tables in the database with row counts.

**Response:**
```json
[
  {
    "name": "users",
    "row_count": 5
  },
  {
    "name": "conversations",
    "row_count": 12
  }
]
```

### GET `/api/admin/database/tables/{table_name}`

Returns data from a specific table with pagination.

**Query Parameters:**
- `limit` (optional): Number of rows to return (default: 100)
- `offset` (optional): Number of rows to skip (default: 0)

**Response:**
```json
{
  "table_name": "users",
  "columns": ["id", "email", "created_at", "is_active"],
  "rows": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "email": "user@example.com",
      "created_at": "2025-10-01T12:00:00",
      "is_active": true
    }
  ],
  "total_rows": 1
}
```

## Security

- **Development Mode Only:** The endpoints are only accessible when `IS_DEVELOPMENT=true`
- **No Authentication Required:** Since this is development-only, no auth is needed
- **SQL Injection Prevention:** Uses SQLAlchemy parameterized queries
- **Table Validation:** Validates table names against information_schema

## Technical Details

### Backend
- Location: `/backend/app/api/routes/admin.py`
- Uses SQLAlchemy's `text()` for raw SQL queries
- Queries `information_schema` for table metadata
- Converts Python types (datetime, UUID) to JSON-serializable formats

### Frontend
- Location: `/frontend/src/app/admin/database/`
- React component with TypeScript
- Responsive design with sidebar + main content layout
- CSS modules for scoped styling
- Handles loading, error, and empty states

### API Client
- Location: `/frontend/src/lib/api.ts`
- Added `getDatabaseTables()` and `getTableData()` functions
- TypeScript interfaces for `TableInfo` and `TableData`

## Usage Example

1. Start the backend server:
   ```bash
   cd backend
   source venv/bin/activate
   uvicorn app.main:app --reload
   ```

2. Start the frontend:
   ```bash
   cd frontend
   npm run dev
   ```

3. Navigate to `http://localhost:3000/admin/database`

4. Click on any table in the sidebar to view its contents

5. Use pagination controls to browse through data

## Navigation

- From Usage Dashboard → Database Viewer via "View Database →" link
- From Database Viewer → Usage Dashboard via "← Back to Usage Dashboard" link

## Future Enhancements

Possible improvements for the future:
- Search/filter within tables
- Sort by column
- Export table data to CSV/JSON
- View table schema (data types, constraints)
- Execute custom SQL queries
- View foreign key relationships
- Real-time updates

