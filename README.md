# BlueAI - Leak Detection System

## Overview
Real-time leak detection system for water distribution networks using an expert system and REST API.

## Quick Start

### Prerequisites
- Python 3.8+
- MySQL 5.7+

### Installation
```bash
# Clone and setup
git clone https://github.com/your-org/blueai.git
cd blueai/backend

# Virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install
pip install -r requirements.txt

# Database
mysql -u root -p < sql/schema.sql
cp .env.example .env  # Add your MySQL credentials

# Run
python app.py