"""
Database Viewer - View all data in your Resume Analyzer database
"""

import sqlite3
import os
from pathlib import Path

def view_database():
    """View all data in the database."""
    
    db_path = "output/database/resume_analyzer.db"
    
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"❌ Database not found at: {db_path}")
        print("Run 'python src/init_database.py' first to create the database.")
        return
    
    print("=" * 80)
    print("RESUME ANALYZER - DATABASE VIEWER")
    print("=" * 80)
    print(f"Database: {db_path}\n")
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print(f"📊 Found {len(tables)} tables\n")
    
    # View each table
    for table_name in tables:
        table = table_name[0]
        print("=" * 80)
        print(f"TABLE: {table}")
        print("=" * 80)
        
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"Total Rows: {count}\n")
        
        if count > 0:
            # Get all data
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            
            # Get column names
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [col[1] for col in cursor.fetchall()]
            
            # Print column headers
            print(" | ".join(columns))
            print("-" * 80)
            
            # Print rows (limit to 10 for readability)
            for i, row in enumerate(rows[:10], 1):
                row_str = " | ".join([str(val)[:30] if val else "NULL" for val in row])
                print(f"{i}. {row_str}")
            
            if len(rows) > 10:
                print(f"... and {len(rows) - 10} more rows")
        else:
            print("(No data in this table)")
        
        print()
    
    conn.close()
    
    print("=" * 80)
    print("DATABASE STATISTICS")
    print("=" * 80)
    
    # Reconnect for statistics
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get statistics
    cursor.execute("SELECT COUNT(*) FROM resumes")
    total_resumes = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM job_descriptions")
    total_jobs = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM analysis_results")
    total_analyses = cursor.fetchone()[0]
    
    cursor.execute("SELECT AVG(match_score) FROM analysis_results")
    avg_score = cursor.fetchone()[0]
    avg_score = round(avg_score, 2) if avg_score else 0
    
    print(f"📄 Total Resumes: {total_resumes}")
    print(f"💼 Total Job Descriptions: {total_jobs}")
    print(f"📊 Total Analyses: {total_analyses}")
    print(f"⭐ Average Match Score: {avg_score}%")
    
    conn.close()
    print("\n" + "=" * 80)

def view_specific_table(table_name):
    """View a specific table in detail."""
    db_path = "output/database/resume_analyzer.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Get column names
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        if not columns:
            print(f"❌ Table '{table_name}' not found")
            return
        
        print(f"\n{'=' * 80}")
        print(f"TABLE: {table_name}")
        print(f"{'=' * 80}\n")
        
        # Print column structure
        print("COLUMNS:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        # Get all data
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        print(f"\nROWS: {len(rows)}")
        print("-" * 80)
        
        if rows:
            col_names = [col[1] for col in columns]
            
            for i, row in enumerate(rows, 1):
                print(f"\nRow {i}:")
                for col_name, value in zip(col_names, row):
                    value_str = str(value)[:100] if value else "NULL"
                    print(f"  {col_name}: {value_str}")
        else:
            print("(No data)")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    finally:
        conn.close()

def interactive_viewer():
    """Interactive database viewer."""
    db_path = "output/database/resume_analyzer.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at: {db_path}")
        print("Run 'python src/init_database.py' first.")
        return
    
    while True:
        print("\n" + "=" * 80)
        print("DATABASE VIEWER - MENU")
        print("=" * 80)
        print("1. View all tables (summary)")
        print("2. View specific table")
        print("3. View statistics")
        print("4. Search resumes")
        print("5. Search analyses")
        print("6. Exit")
        print("=" * 80)
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == "1":
            view_database()
        
        elif choice == "2":
            print("\nAvailable tables:")
            print("  - resumes")
            print("  - job_descriptions")
            print("  - analysis_results")
            print("  - extracted_skills")
            print("  - contact_info")
            print("  - experience")
            print("  - education")
            
            table = input("\nEnter table name: ").strip()
            view_specific_table(table)
        
        elif choice == "3":
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            print("\n" + "=" * 80)
            print("DATABASE STATISTICS")
            print("=" * 80)
            
            cursor.execute("SELECT COUNT(*) FROM resumes")
            print(f"📄 Total Resumes: {cursor.fetchone()[0]}")
            
            cursor.execute("SELECT COUNT(*) FROM job_descriptions")
            print(f"💼 Total Job Descriptions: {cursor.fetchone()[0]}")
            
            cursor.execute("SELECT COUNT(*) FROM analysis_results")
            print(f"📊 Total Analyses: {cursor.fetchone()[0]}")
            
            cursor.execute("SELECT COUNT(*) FROM extracted_skills")
            print(f"🔧 Total Skills: {cursor.fetchone()[0]}")
            
            cursor.execute("SELECT AVG(match_score), AVG(ats_score) FROM analysis_results")
            result = cursor.fetchone()
            if result[0]:
                print(f"⭐ Average Match Score: {result[0]:.2f}%")
                print(f"⭐ Average ATS Score: {result[1]:.2f}%")
            
            conn.close()
        
        elif choice == "4":
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT id, filename, upload_date FROM resumes ORDER BY upload_date DESC")
            resumes = cursor.fetchall()
            
            if resumes:
                print("\n📄 ALL RESUMES:")
                print("-" * 80)
                for resume in resumes:
                    print(f"ID: {resume[0]} | File: {resume[1]} | Date: {resume[2]}")
            else:
                print("\n(No resumes found)")
            
            conn.close()
        
        elif choice == "5":
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT ar.id, r.filename, ar.match_score, ar.ats_score, ar.analysis_date
                FROM analysis_results ar
                JOIN resumes r ON ar.resume_id = r.id
                ORDER BY ar.analysis_date DESC
            """)
            analyses = cursor.fetchall()
            
            if analyses:
                print("\n📊 ALL ANALYSES:")
                print("-" * 80)
                for analysis in analyses:
                    print(f"ID: {analysis[0]} | Resume: {analysis[1]}")
                    print(f"  Match: {analysis[2]:.1f}% | ATS: {analysis[3]:.1f}% | Date: {analysis[4]}")
                    print()
            else:
                print("\n(No analyses found)")
            
            conn.close()
        
        elif choice == "6":
            print("\nGoodbye!")
            break
        
        else:
            print("\n❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    print("\n🔍 Resume Analyzer Database Viewer")
    print("Choose viewing mode:")
    print("1. Quick view (all data)")
    print("2. Interactive mode")
    
    mode = input("\nEnter choice (1-2): ").strip()
    
    if mode == "1":
        view_database()
    elif mode == "2":
        interactive_viewer()
    else:
        print("Invalid choice. Running quick view...")
        view_database()