#!/usr/bin/env python3
"""
Simple Flask Task Manager App
Demonstrates integration with PostgreSQL and Nginx reverse proxy
"""

from flask import Flask, render_template, request, jsonify
import psycopg
import os
from datetime import datetime

app = Flask(__name__)

# Database connection details (from environment variables)
DB_HOST = os.getenv('PGHOST', 'localhost')
DB_USER = os.getenv('PGUSER', 'kmistry')
DB_PASSWORD = os.getenv('PGPASSWORD', '')
DB_NAME = os.getenv('PGDATABASE', 'app_db')

def get_db_connection():
    """Create database connection"""
    try:
        conn = psycopg.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            dbname=DB_NAME
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def init_db():
    """Create tasks table if it doesn't exist"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        with conn.cursor() as cur:
            cur.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(200) NOT NULL,
                    description TEXT,
                    completed BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Database init error: {e}")
        return False

@app.route('/')
def index():
    """Home page - list all tasks"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT id, title, description, completed, created_at FROM tasks ORDER BY created_at DESC')
            tasks = cur.fetchall()
        conn.close()
        
        return render_template('index.html', tasks=tasks)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Create new task"""
    data = request.get_json()
    title = data.get('title')
    description = data.get('description', '')
    
    if not title:
        return jsonify({'error': 'Title required'}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        with conn.cursor() as cur:
            cur.execute(
                'INSERT INTO tasks (title, description) VALUES (%s, %s) RETURNING id',
                (title, description)
            )
            task_id = cur.fetchone()[0]
        conn.commit()
        conn.close()
        
        return jsonify({'id': task_id, 'message': 'Task created'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks/<int:task_id>/complete', methods=['PUT'])
def complete_task(task_id):
    """Mark task as complete"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        with conn.cursor() as cur:
            cur.execute('UPDATE tasks SET completed = TRUE WHERE id = %s', (task_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Task completed'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint (for monitoring)"""
    conn = get_db_connection()
    if conn:
        conn.close()
        return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()}), 200
    else:
        return jsonify({'status': 'unhealthy'}), 500

if __name__ == '__main__':
    # Initialize database on startup
    init_db()
    
    # Run on 0.0.0.0 so it listens on all interfaces in Docker
    app.run(host='0.0.0.0', port=5000, debug=False)
