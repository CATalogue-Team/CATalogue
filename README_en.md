
# CATalogue - Professional Cat Information Management System

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![Build Status](https://github.com/your-repo/CATalogue/actions/workflows/tests.yml/badge.svg)](https://github.com/your-repo/CATalogue/actions)
[![Coverage Status](https://coveralls.io/repos/github/your-repo/CATalogue/badge.svg)](https://coveralls.io/github/your-repo/CATalogue)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Table of Contents
- [Core Value](#-core-value)
- [Features](#-features) 
- [Quick Start](#-quick-start)
- [Configuration](#-configuration-guide)
- [Developer Docs](#-developer-documentation)
- [Contributing](#-how-to-contribute)
- [License](#-license)

## Requirements
- Python 3.8+
- PostgreSQL 12+ or SQLite 3
- Node.js 16+ (for frontend build)

## 📌 Core Value
Provides efficient cat information management solutions for animal rescue organizations, including:
- Complete cat information lifecycle management
- Multi-role collaboration workflow
- Data security and access control
- Responsive management interface

## 🛠️ Features

### User System
- Multi-role authentication (Admin/Regular User)
- Registration approval process
- Password encryption storage (PBKDF2+SHA256)
- Session management and activity logs

### Cat Management
- Complete profile management (basic info + multi-image upload)
- Adoption status tracking (Available/Adopted)
- Advanced search and filtering
- Batch import/export

### Admin Panel
- Role-based access control
- Data audit and version history
- System monitoring dashboard (Prometheus metrics endpoint `/metrics`)
- Request logging and performance monitoring
- Automated data backup

## 🚀 Quick Start

### Environment Setup
```bash
# Clone repository
git clone https://github.com/your-repo/CATalogue.git
cd CATalogue

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

## 🗄️ Database Initialization

### 1. Standard Migration (Recommended for development)
```bash
# Initialize migration repository
flask db init

# Generate migration script
flask db migrate -m "Initial migration"

# Apply migrations
flask db upgrade

# Create admin (CLI command)
flask create-admin <username> <password>
# Example:
flask create-admin admin securePassword123!

# Password requirements:
# - Minimum 8 characters
# - Contains uppercase, lowercase and numbers
# - Cannot be same as username
```

### 2. Using Initialization Script (First deployment/reset)
```bash
# Basic initialization (with default admin account)
python init_db.py

# Custom admin account
python init_db.py --username myadmin --password MySecurePass123

# Skip sample data
python init_db.py --skip-samples

# Parameters:
# --username: Admin username (default:admin)
# --password: Admin password (default:admin123)
# --skip-samples: Skip sample data initialization
```

## 📜 Log Management

### View Logs
```bash
# List log files
curl -H "Authorization: Bearer <token>" http://localhost:5000/admin/logs

# View log content
curl -H "Authorization: Bearer <token>" http://localhost:5000/admin/logs/app.log
```

### Adjust Log Level
```bash
# Set log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)
curl -X PUT -H "Content-Type: application/json" \
     -H "Authorization: Bearer <token>" \
     -d '{"level":"DEBUG"}' \
     http://localhost:5000/admin/logs/level
```

### Log Configuration
```ini
# .env log settings
LOG_LEVEL=INFO  # Log level
LOG_FILE=logs/app.log  # Log file path
LOG_FORMAT='%(asctime)s - %(name)s - %(levelname)s - %(message)s'  # Log format
```

### Environment Differences
| Scenario      | Development Environment       | Production Environment      |
|---------------|--------------------------------|-----------------------------|
| Recommended   | Standard migration or init_db  | Standard migration only     |
| Data Safety   | Can reset freely               | Must backup before changes  |
| Use Case      | Development & testing          | Official deployment         |

### Important Notes
1. **init_db.py will wipe existing data** - use with caution in production
2. Sample images stored in `static/uploads/`
3. Default admin account: admin/admin123
4. Before starting ensure:
```bash
pip install -r requirements.txt
```

### Start Service
```bash
# Development mode
flask run --debug

# Production mode
gunicorn -w 4 --bind 0.0.0.0:8000 "run:app"
```

## ⚙️ Configuration Guide

### Key Configurations
| Config Item | Description | Example Value |
|-------------|-------------|---------------|
| `DATABASE_URL` | Database connection | `sqlite:///instance/cats.db` |
| `UPLOAD_FOLDER` | File upload path | `./static/uploads` |
| `MAX_IMAGE_SIZE` | Image size limit | `5242880` (5MB) |

### Production Recommendations
```ini
# .env file example
FLASK_ENV=production
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@localhost/prod_db
```

## 🖼️ Screenshots

![Homepage](static/screenshots/home.png)
![Cat Details](static/screenshots/cat_detail.png)
![Admin Panel](static/screenshots/admin.png)

##  Developer Documentation

### Project Structure
```
.
├── app/              # Core modules
│   ├── routes/       # Route controllers
│   ├── services/    # Business logic
│   ├── models/      # Data models
│   └── static/      # Static resources
├── tests/           # Unit tests
└── docs/            # Project documentation
```

### API Specifications

#### Cat Management API

**1. Get Cat List**
```
GET /cats
```
Parameters:
- `page` - Page number (default 1)
- `per_page` - Items per page (default 10)
- `breed` - Filter by breed
- `is_adopted` - Filter by adoption status (true/false)

Example Request:
```bash
curl "http://localhost:5000/cats?page=2&breed=Persian"
```

Response Example:
```json
{
  "items": [
    {
      "id": 1,
      "name": "Snowball",
      "breed": "Persian",
      "age": 2,
      "is_adopted": false
    }
  ],
  "total": 15,
  "page": 2,
  "per_page": 10
}
```

**2. Create Cat Record**
```
POST /cats
```
Headers:
- `Content-Type: application/json`
- `Authorization: Bearer <token>`

Request Body:
```json
{
  "name": "New Cat",
  "breed": "British Shorthair",
  "age": 1,
  "description": "Playful and cute"
}
```

**3. Update Cat Info**
```
PUT /cats/<id>
```
Parameters:
- `id` - Cat ID (path parameter)

Request Body:
```json
{
  "age": 2,
  "is_adopted": true
}
```

#### System Monitoring API

**Get Metrics**
```
GET /metrics
```
Response Format:
```
# TYPE http_requests_total counter
http_requests_total{method="GET",endpoint="cats",status="200"} 42
```

#### Common Response Codes
| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 404 | Not Found |
| 500 | Server Error |

### Testing Guide
```bash
# Run unit tests
pytest tests/

# Generate test coverage report
pytest --cov=app tests/

# Test monitoring endpoint
curl http://localhost:5000/metrics
```

## ❓ FAQ

### Q: How to reset admin password?
```bash
flask reset-password <username> <new_password>
```

### Q: Image upload fails?
1. Check `static/uploads` directory permissions
2. Confirm image size < configured `MAX_IMAGE_SIZE`
3. Check file extension is allowed (jpg/png/gif)

### Q: How to backup database?
```bash
# SQLite
cp instance/cats.db instance/backup_$(date +%Y%m%d).db

# PostgreSQL
pg_dump -U username -d dbname > backup_$(date +%Y%m%d).sql
```

## 🤝 How to Contribute
1. Fork the repository
2. Create feature branch (`git checkout -b feature/xxx`)
3. Commit changes (`git commit -am 'Add some feature'`)
4. Push branch (`git push origin feature/xxx`)
5. Create Pull Request

## 📜 License
MIT License © 2023 CATalogue Team
