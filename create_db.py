#!/usr/bin/env python3
"""
Create database tables for Pic2Kitchen
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.app import app, db

with app.app_context():
    # Create all tables
    db.create_all()
    print("Database tables created successfully!")
    
    # List created tables
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"Created tables: {', '.join(tables)}")