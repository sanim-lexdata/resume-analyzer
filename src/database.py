import sqlite3
import json
from datetime import datetime
import os
from pathlib import Path

class ResumeDatabase:
    """Database manager for Resume Analyzer application."""
    
    def __init__(self, db_path="output/database/resume_analyzer.db"):
        self.db_path = db_path
        self._setup_database()
    
    def _setup_database(self):
        """Create database directory and initialize tables."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._create_tables()
    
    def _create_tables(self):
        """Create all necessary tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table 1: Resumes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                file_size INTEGER,
                file_type TEXT,
                full_text TEXT,
                UNIQUE(filename, upload_date)
            )
        ''')
        
        # Table 2: Job Descriptions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS job_descriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                company TEXT,
                description TEXT NOT NULL,
                requirements TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table 3: Analysis Results
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resume_id INTEGER NOT NULL,
                job_id INTEGER,
                analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                match_score REAL,
                ats_score REAL,
                keyword_match_count INTEGER,
                missing_keywords TEXT,
                strengths TEXT,
                weaknesses TEXT,
                recommendations TEXT,
                detailed_analysis TEXT,
                FOREIGN KEY (resume_id) REFERENCES resumes (id),
                FOREIGN KEY (job_id) REFERENCES job_descriptions (id)
            )
        ''')
        
        # Table 4: Extracted Skills
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS extracted_skills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resume_id INTEGER NOT NULL,
                skill_name TEXT NOT NULL,
                skill_category TEXT,
                confidence_score REAL,
                FOREIGN KEY (resume_id) REFERENCES resumes (id)
            )
        ''')
        
        # Table 5: Contact Information
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contact_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resume_id INTEGER NOT NULL,
                email TEXT,
                phone TEXT,
                linkedin TEXT,
                github TEXT,
                website TEXT,
                location TEXT,
                FOREIGN KEY (resume_id) REFERENCES resumes (id)
            )
        ''')
        
        # Table 6: Experience
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS experience (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resume_id INTEGER NOT NULL,
                company TEXT,
                position TEXT,
                start_date TEXT,
                end_date TEXT,
                description TEXT,
                FOREIGN KEY (resume_id) REFERENCES resumes (id)
            )
        ''')
        
        # Table 7: Education
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS education (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resume_id INTEGER NOT NULL,
                institution TEXT,
                degree TEXT,
                field_of_study TEXT,
                graduation_date TEXT,
                gpa TEXT,
                FOREIGN KEY (resume_id) REFERENCES resumes (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def insert_resume(self, filename, file_size, file_type, full_text):
        """Insert a new resume into the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO resumes (filename, file_size, file_type, full_text)
                VALUES (?, ?, ?, ?)
            ''', (filename, file_size, file_type, full_text))
            
            resume_id = cursor.lastrowid
            conn.commit()
            return resume_id
        except sqlite3.IntegrityError:
            # Resume already exists, get its ID
            cursor.execute('''
                SELECT id FROM resumes WHERE filename = ?
                ORDER BY upload_date DESC LIMIT 1
            ''', (filename,))
            result = cursor.fetchone()
            return result[0] if result else None
        finally:
            conn.close()
    
    def insert_job_description(self, title, company, description, requirements):
        """Insert a new job description."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO job_descriptions (title, company, description, requirements)
            VALUES (?, ?, ?, ?)
        ''', (title, company, description, requirements))
        
        job_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return job_id
    
    def insert_analysis_result(self, resume_id, job_id, match_score, ats_score, 
                              keyword_match_count, missing_keywords, strengths, 
                              weaknesses, recommendations, detailed_analysis):
        """Insert analysis results."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO analysis_results 
            (resume_id, job_id, match_score, ats_score, keyword_match_count,
             missing_keywords, strengths, weaknesses, recommendations, detailed_analysis)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (resume_id, job_id, match_score, ats_score, keyword_match_count,
              json.dumps(missing_keywords), json.dumps(strengths), 
              json.dumps(weaknesses), json.dumps(recommendations), 
              json.dumps(detailed_analysis)))
        
        analysis_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return analysis_id
    
    def insert_skills(self, resume_id, skills):
        """Insert extracted skills for a resume."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for skill in skills:
            cursor.execute('''
                INSERT INTO extracted_skills (resume_id, skill_name, skill_category, confidence_score)
                VALUES (?, ?, ?, ?)
            ''', (resume_id, skill.get('name'), skill.get('category'), skill.get('confidence', 1.0)))
        
        conn.commit()
        conn.close()
    
    def insert_contact_info(self, resume_id, email=None, phone=None, linkedin=None, 
                           github=None, website=None, location=None):
        """Insert contact information."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO contact_info (resume_id, email, phone, linkedin, github, website, location)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (resume_id, email, phone, linkedin, github, website, location))
        
        conn.commit()
        conn.close()
    
    def insert_experience(self, resume_id, experiences):
        """Insert work experience entries."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for exp in experiences:
            cursor.execute('''
                INSERT INTO experience (resume_id, company, position, start_date, end_date, description)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (resume_id, exp.get('company'), exp.get('position'), 
                  exp.get('start_date'), exp.get('end_date'), exp.get('description')))
        
        conn.commit()
        conn.close()
    
    def insert_education(self, resume_id, education_list):
        """Insert education entries."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for edu in education_list:
            cursor.execute('''
                INSERT INTO education (resume_id, institution, degree, field_of_study, graduation_date, gpa)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (resume_id, edu.get('institution'), edu.get('degree'), 
                  edu.get('field'), edu.get('graduation_date'), edu.get('gpa')))
        
        conn.commit()
        conn.close()
    
    def get_resume_by_id(self, resume_id):
        """Retrieve resume information by ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM resumes WHERE id = ?', (resume_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'id': result[0],
                'filename': result[1],
                'upload_date': result[2],
                'file_size': result[3],
                'file_type': result[4],
                'full_text': result[5]
            }
        return None
    
    def get_all_resumes(self):
        """Get all resumes from database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, filename, upload_date, file_size FROM resumes ORDER BY upload_date DESC')
        results = cursor.fetchall()
        conn.close()
        
        return [{'id': r[0], 'filename': r[1], 'upload_date': r[2], 'file_size': r[3]} for r in results]
    
    def get_analysis_results(self, resume_id):
        """Get all analysis results for a resume."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT ar.*, jd.title, jd.company 
            FROM analysis_results ar
            LEFT JOIN job_descriptions jd ON ar.job_id = jd.id
            WHERE ar.resume_id = ?
            ORDER BY ar.analysis_date DESC
        ''', (resume_id,))
        
        results = cursor.fetchall()
        conn.close()
        
        analysis_list = []
        for r in results:
            analysis_list.append({
                'id': r[0],
                'resume_id': r[1],
                'job_id': r[2],
                'analysis_date': r[3],
                'match_score': r[4],
                'ats_score': r[5],
                'keyword_match_count': r[6],
                'missing_keywords': json.loads(r[7]) if r[7] else [],
                'strengths': json.loads(r[8]) if r[8] else [],
                'weaknesses': json.loads(r[9]) if r[9] else [],
                'recommendations': json.loads(r[10]) if r[10] else [],
                'detailed_analysis': json.loads(r[11]) if r[11] else {},
                'job_title': r[12],
                'company': r[13]
            })
        
        return analysis_list
    
    def get_skills_by_resume(self, resume_id):
        """Get all skills for a resume."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT skill_name, skill_category, confidence_score FROM extracted_skills WHERE resume_id = ?', 
                      (resume_id,))
        results = cursor.fetchall()
        conn.close()
        
        return [{'name': r[0], 'category': r[1], 'confidence': r[2]} for r in results]
    
    def delete_resume(self, resume_id):
        """Delete a resume and all associated data."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Delete in order due to foreign key constraints
        cursor.execute('DELETE FROM analysis_results WHERE resume_id = ?', (resume_id,))
        cursor.execute('DELETE FROM extracted_skills WHERE resume_id = ?', (resume_id,))
        cursor.execute('DELETE FROM contact_info WHERE resume_id = ?', (resume_id,))
        cursor.execute('DELETE FROM experience WHERE resume_id = ?', (resume_id,))
        cursor.execute('DELETE FROM education WHERE resume_id = ?', (resume_id,))
        cursor.execute('DELETE FROM resumes WHERE id = ?', (resume_id,))
        
        conn.commit()
        conn.close()
    
    def get_statistics(self):
        """Get database statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        cursor.execute('SELECT COUNT(*) FROM resumes')
        stats['total_resumes'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM job_descriptions')
        stats['total_jobs'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM analysis_results')
        stats['total_analyses'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT AVG(match_score) FROM analysis_results')
        avg_score = cursor.fetchone()[0]
        stats['average_match_score'] = round(avg_score, 2) if avg_score else 0
        
        conn.close()
        return stats