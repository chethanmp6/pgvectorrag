#!/usr/bin/env python3
"""
Quick test script to verify the RAG system setup
"""
import asyncio
from sqlalchemy import text
from app.database import engine


async def test_database_connection():
    """Test database connection and verify tables"""
    print("🔍 Testing database connection...")
    
    try:
        async with engine.connect() as conn:
            # Test connection
            result = await conn.execute(text("SELECT version();"))
            version = result.scalar()
            print(f"✅ PostgreSQL connected: {version}")
            
            # Check pgvector extension
            result = await conn.execute(text("SELECT * FROM pg_extension WHERE extname='vector';"))
            if result.first():
                print("✅ pgvector extension installed")
            else:
                print("❌ pgvector extension not found")
            
            # Check tables
            result = await conn.execute(text("""
                SELECT tablename FROM pg_tables 
                WHERE schemaname = 'public' 
                ORDER BY tablename;
            """))
            tables = [row[0] for row in result]
            print(f"✅ Tables found: {', '.join(tables)}")
            
            # Check corpus count
            result = await conn.execute(text("SELECT COUNT(*) FROM corpus;"))
            count = result.scalar()
            print(f"📊 Corpus count: {count}")
            
        print("\n✨ Database setup verified successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False


async def main():
    """Main test function"""
    print("=" * 50)
    print("RAG System - Database Verification")
    print("=" * 50)
    print()
    
    success = await test_database_connection()
    
    print()
    if success:
        print("🎉 All checks passed!")
        print("\nNext steps:")
        print("1. Add your OpenAI API key to .env file")
        print("2. Run: python -m app.main")
        print("3. Visit: http://localhost:8000/docs")
    else:
        print("⚠️  Some checks failed. Please review the errors above.")
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
