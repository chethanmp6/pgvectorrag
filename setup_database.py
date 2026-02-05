#!/usr/bin/env python3
"""
RAG Database Setup Script

This script initializes the RAG database using direct PostgreSQL connections.
It reads database configuration from .env file and works in both development
and production environments without requiring Docker access.
"""

import sys
import os
from pathlib import Path
from urllib.parse import urlparse
from dotenv import load_dotenv

try:
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
except ImportError:
    print("❌ Error: psycopg2 is not installed")
    print("   Install it with: pip install psycopg2-binary")
    sys.exit(1)


def parse_database_url(url: str) -> dict:
    """Parse DATABASE_URL into connection parameters"""
    # Remove asyncpg driver prefix if present
    url = url.replace("postgresql+asyncpg://", "postgresql://")
    parsed = urlparse(url)
    
    return {
        'user': parsed.username,
        'password': parsed.password,
        'host': parsed.hostname,
        'port': parsed.port or 5432,
        'database': parsed.path.lstrip('/')
    }


def database_exists(conn_params: dict, db_name: str) -> bool:
    """Check if a database exists"""
    # Connect to default 'postgres' database to check
    check_params = conn_params.copy()
    check_params['database'] = 'postgres'
    
    try:
        conn = psycopg2.connect(**check_params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (db_name,)
        )
        exists = cursor.fetchone() is not None
        
        cursor.close()
        conn.close()
        return exists
    except psycopg2.Error as e:
        print(f"❌ Error checking database: {e}")
        return False


def create_database(conn_params: dict, db_name: str):
    """Create a new database"""
    # Connect to default 'postgres' database
    create_params = conn_params.copy()
    create_params['database'] = 'postgres'
    
    conn = psycopg2.connect(**create_params)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    cursor.execute(f'CREATE DATABASE "{db_name}"')
    
    cursor.close()
    conn.close()


def drop_database(conn_params: dict, db_name: str):
    """Drop a database"""
    drop_params = conn_params.copy()
    drop_params['database'] = 'postgres'
    
    conn = psycopg2.connect(**drop_params)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    # Terminate existing connections
    cursor.execute(f"""
        SELECT pg_terminate_backend(pg_stat_activity.pid)
        FROM pg_stat_activity
        WHERE pg_stat_activity.datname = '{db_name}'
        AND pid <> pg_backend_pid()
    """)
    
    cursor.execute(f'DROP DATABASE IF EXISTS "{db_name}"')
    
    cursor.close()
    conn.close()


def enable_extension(conn_params: dict, extension_name: str):
    """Enable a PostgreSQL extension"""
    conn = psycopg2.connect(**conn_params)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    cursor.execute(f'CREATE EXTENSION IF NOT EXISTS "{extension_name}"')
    
    cursor.close()
    conn.close()


def execute_sql_file(conn_params: dict, sql_file_path: Path):
    """Execute SQL from a file"""
    with open(sql_file_path, 'r') as f:
        sql_content = f.read()
    
    conn = psycopg2.connect(**conn_params)
    cursor = conn.cursor()
    
    try:
        cursor.execute(sql_content)
        conn.commit()
    except psycopg2.Error as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


def list_tables(conn_params: dict):
    """List all tables in the database"""
    conn = psycopg2.connect(**conn_params)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public'
        ORDER BY tablename
    """)
    
    tables = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return [table[0] for table in tables]


def main():
    print("🔧 RAG Database Setup")
    print("=" * 70)
    print()
    
    # Load environment variables
    env_path = Path(__file__).parent / ".env"
    if not env_path.exists():
        print("❌ Error: .env file not found")
        print(f"   Expected at: {env_path}")
        sys.exit(1)
    
    load_dotenv(env_path)
    
    # Parse database URL from .env
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ Error: DATABASE_URL not found in .env")
        sys.exit(1)
    
    # Parse connection details
    conn_params = parse_database_url(database_url)
    db_name = conn_params['database']
    
    print(f"📋 Configuration from .env:")
    print(f"   Database: {db_name}")
    print(f"   User: {conn_params['user']}")
    print(f"   Host: {conn_params['host']}:{conn_params['port']}")
    print()
    
    # Test connection to PostgreSQL server
    print("🔍 Testing connection to PostgreSQL server...")
    test_params = conn_params.copy()
    test_params['database'] = 'postgres'
    
    try:
        test_conn = psycopg2.connect(**test_params)
        test_conn.close()
        print("✅ Successfully connected to PostgreSQL server")
    except psycopg2.Error as e:
        print(f"❌ Error connecting to PostgreSQL: {e}")
        print(f"   Please check your DATABASE_URL in .env")
        sys.exit(1)
    
    print()
    
    # Check if database already exists
    print(f"🔍 Checking if database '{db_name}' exists...")
    if database_exists(conn_params, db_name):
        print(f"⚠️  Database '{db_name}' already exists")
        response = input("   Do you want to recreate it? (y/N): ").strip().lower()
        
        if response == 'y':
            print(f"🗑️  Dropping existing database '{db_name}'...")
            try:
                drop_database(conn_params, db_name)
                print(f"✅ Database '{db_name}' dropped")
            except psycopg2.Error as e:
                print(f"❌ Error dropping database: {e}")
                sys.exit(1)
        else:
            print("ℹ️  Skipping database creation")
            sys.exit(0)
    
    # Create database
    print(f"📦 Creating database '{db_name}'...")
    try:
        create_database(conn_params, db_name)
        print(f"✅ Database '{db_name}' created")
    except psycopg2.Error as e:
        print(f"❌ Error creating database: {e}")
        sys.exit(1)
    
    # Enable vector extension
    print("🔌 Enabling 'vector' extension...")
    try:
        enable_extension(conn_params, 'vector')
        print("✅ Vector extension enabled")
    except psycopg2.Error as e:
        print(f"❌ Error enabling vector extension: {e}")
        print("   Make sure pgvector is installed on your PostgreSQL server")
        sys.exit(1)
    
    # Enable uuid-ossp extension
    print("🔌 Enabling 'uuid-ossp' extension...")
    try:
        enable_extension(conn_params, 'uuid-ossp')
        print("✅ UUID extension enabled")
    except psycopg2.Error as e:
        print(f"❌ Error enabling uuid-ossp extension: {e}")
        sys.exit(1)
    
    # Initialize schema
    init_sql_path = Path(__file__).parent / "database" / "init.sql"
    if not init_sql_path.exists():
        print(f"❌ Error: init.sql not found at {init_sql_path}")
        sys.exit(1)
    
    print("📋 Initializing schema from database/init.sql...")
    try:
        execute_sql_file(conn_params, init_sql_path)
        print("✅ Schema initialized")
    except psycopg2.Error as e:
        print(f"❌ Error initializing schema: {e}")
        sys.exit(1)
    
    # Show tables
    print()
    print("📊 Database tables created:")
    try:
        tables = list_tables(conn_params)
        for table in tables:
            print(f"   ✓ {table}")
    except psycopg2.Error as e:
        print(f"   Error listing tables: {e}")
    
    print()
    print("=" * 70)
    print("✅ Database setup complete!")
    print("=" * 70)
    print()
    print("🚀 You can now start the RAG API:")
    print("   python -m app.main")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
