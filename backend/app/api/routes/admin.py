"""
Admin endpoints for usage tracking and user management.

These endpoints are only available in development mode.
"""

from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from pydantic import BaseModel

from app.core.database import get_db
from app.core.config import settings
from app.services.usage_service import get_all_usage_stats, toggle_user_access


router = APIRouter()


# ============================================================================
# Schemas
# ============================================================================

class UsageStatsResponse(BaseModel):
    """Response model for usage statistics."""
    type: str  # "authenticated" or "anonymous"
    user_id: str | None = None
    email: str | None = None
    is_active: bool | None = None
    session_id: str | None = None
    request_count: int
    last_request: str | None = None
    user_agent: str | None = None


class ToggleAccessRequest(BaseModel):
    """Request model for toggling user access."""
    user_id: str


class ToggleAccessResponse(BaseModel):
    """Response model for toggle user access."""
    user_id: str
    email: str
    is_active: bool
    message: str


class TableInfo(BaseModel):
    """Information about a database table."""
    name: str
    row_count: int


class TableData(BaseModel):
    """Data from a database table."""
    table_name: str
    columns: list[str]
    rows: list[dict[str, Any]]
    total_rows: int


# ============================================================================
# Middleware
# ============================================================================

async def require_development_mode():
    """
    Dependency to ensure admin routes are only accessible in development.
    
    Raises:
        HTTPException: If not in development mode
    """
    if not settings.is_development:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found"
        )


# ============================================================================
# Endpoints
# ============================================================================

@router.get("/usage", response_model=list[UsageStatsResponse])
async def get_usage_statistics(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: None = Depends(require_development_mode),
) -> list[UsageStatsResponse]:
    """
    Get usage statistics for all users and anonymous sessions.
    
    Only available in development mode.
    
    Args:
        db: Database session
        
    Returns:
        List of usage statistics
    """
    stats = await get_all_usage_stats(db, limit=1000)
    
    return [UsageStatsResponse(**stat) for stat in stats]


@router.post("/toggle-access", response_model=ToggleAccessResponse)
async def toggle_user_access_endpoint(
    request: ToggleAccessRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: None = Depends(require_development_mode),
) -> ToggleAccessResponse:
    """
    Toggle a user's access (enable/disable).
    
    Only available in development mode.
    
    Args:
        request: Request with user_id to toggle
        db: Database session
        
    Returns:
        Updated user status
        
    Raises:
        404: If user not found
    """
    try:
        user_id = UUID(request.user_id)
        user = await toggle_user_access(db, user_id)
        
        return ToggleAccessResponse(
            user_id=str(user.id),
            email=user.email,
            is_active=user.is_active,
            message=f"User access {'enabled' if user.is_active else 'disabled'} successfully"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/database/tables", response_model=list[TableInfo])
async def get_database_tables(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: None = Depends(require_development_mode),
) -> list[TableInfo]:
    """
    Get list of all tables in the database with row counts.
    
    Only available in development mode.
    
    Args:
        db: Database session
        
    Returns:
        List of tables with their row counts
    """
    # Get all tables from information_schema
    query = text("""
        SELECT 
            table_name,
            (SELECT COUNT(*) FROM "' || table_name || '") as row_count
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        ORDER BY table_name
    """)
    
    # For better performance, we'll query each table separately
    tables_query = text("""
        SELECT table_name
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        ORDER BY table_name
    """)
    
    result = await db.execute(tables_query)
    tables = result.fetchall()
    
    table_info_list = []
    for (table_name,) in tables:
        count_query = text(f'SELECT COUNT(*) FROM "{table_name}"')
        count_result = await db.execute(count_query)
        row_count = count_result.scalar() or 0
        
        table_info_list.append(TableInfo(name=table_name, row_count=row_count))
    
    return table_info_list


@router.get("/database/tables/{table_name}", response_model=TableData)
async def get_table_data(
    table_name: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: None = Depends(require_development_mode),
    limit: int = 100,
    offset: int = 0,
) -> TableData:
    """
    Get data from a specific table.
    
    Only available in development mode.
    
    Args:
        table_name: Name of the table to query
        db: Database session
        limit: Maximum number of rows to return (default: 100)
        offset: Number of rows to skip (default: 0)
        
    Returns:
        Table data with columns and rows
        
    Raises:
        404: If table not found
    """
    # Validate table exists
    table_check = text("""
        SELECT table_name
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        AND table_name = :table_name
    """)
    
    result = await db.execute(table_check, {"table_name": table_name})
    if not result.fetchone():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Table '{table_name}' not found"
        )
    
    # Get column names
    columns_query = text("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = :table_name
        ORDER BY ordinal_position
    """)
    
    columns_result = await db.execute(columns_query, {"table_name": table_name})
    columns = [row[0] for row in columns_result.fetchall()]
    
    # Get total row count
    count_query = text(f'SELECT COUNT(*) FROM "{table_name}"')
    count_result = await db.execute(count_query)
    total_rows = count_result.scalar() or 0
    
    # Get table data with pagination
    data_query = text(f'SELECT * FROM "{table_name}" LIMIT :limit OFFSET :offset')
    data_result = await db.execute(data_query, {"limit": limit, "offset": offset})
    
    rows = []
    for row in data_result.fetchall():
        row_dict = {}
        for i, col in enumerate(columns):
            value = row[i]
            # Convert to JSON-serializable types
            if hasattr(value, 'isoformat'):  # datetime objects
                value = value.isoformat()
            elif isinstance(value, UUID):
                value = str(value)
            row_dict[col] = value
        rows.append(row_dict)
    
    return TableData(
        table_name=table_name,
        columns=columns,
        rows=rows,
        total_rows=total_rows
    )

