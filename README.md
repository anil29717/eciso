# ETCISO Quiz Game

A comprehensive industry-specific quiz game application built with Flask.

## Features

- **Industry-Specific Questions**: 22 different industries with tailored questions
- **HTTPS Support**: Secure connection for camera access on mobile devices
- **Admin Panel**: Complete management system for questions, users, and analytics
- **Mobile Responsive**: Optimized for all device types
- **Real-time Analytics**: Track user performance and engagement
- **Bulk Data Import**: Excel/CSV support for questions and users

## Quick Start

### Prerequisites
- Python 3.7+
- pip (Python package manager)

### Installation

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run HTTP Version** (Development)
   ```bash
   python app.py
   ```
   Access at: http://localhost:5000

3. **Run HTTPS Version** (Production/Mobile)
   ```bash
   python app_https.py
   ```
   Access at: https://localhost:5000

### Admin Access

- **URL**: `/admin/login`
- **Default Credentials**: 
  - Username: `admin`
  - Password: `admin123`

## File Structure

```
ETCISOfull/
├── app.py                 # Main Flask application (HTTP)
├── app_https.py          # HTTPS version with SSL
├── routes.py             # All application routes
├── requirements.txt      # Python dependencies
├── game.db              # SQLite database
├── HTTPS_SETUP_GUIDE.md # HTTPS configuration guide
├── templates/           # HTML templates
│   ├── game/           # Game interface templates
│   └── admin/          # Admin panel templates
├── static/             # CSS, JS, images
├── bulk_uploads/       # File upload directory
├── instance/           # Flask instance folder
└── question_files/     # Question import files
```

## Database

- **Type**: SQLite
- **File**: `game.db`
- **Auto-created**: On first run
- **Contains**: 160+ questions across 22 industries

## Industries Supported

1. BFSI (Banking, Financial Services, Insurance)
2. Manufacturing
3. Healthcare/Pharma
4. IT/ITES
5. Automotive
6. New-Age (Startups/Tech)
7. Aviation
8. Conglomerate
9. Media & Entertainment
10. Retail
11. FMCG
12. Telecom
13. Insurance
14. Financial Services
15. Infrastructure
16. Construction
17. Logistics
18. Business Consulting
19. Government Administration
20. PSU (Public Sector)
21. Diversified
22. Energy

## Key Features

### Game Flow
1. **Welcome Screen**: Introduction and branding
2. **User Information**: Name, company, email collection
3. **Industry Selection**: Choose from 22+ industries
4. **Selfie Capture**: Camera integration for engagement
5. **Quiz Questions**: Industry-specific multiple choice
6. **Results & Analytics**: Performance tracking
7. **Company Information**: Customized industry insights
8. **Thank You**: Completion and next steps

### Admin Features
- **Dashboard**: Overview of all activities
- **Question Management**: Add, edit, delete questions
- **User Management**: View and manage participants
- **Analytics**: Detailed performance reports
- **Bulk Import**: Excel/CSV file uploads
- **Category Management**: Organize questions by industry

## HTTPS Configuration

For mobile camera access, HTTPS is required. See `HTTPS_SETUP_GUIDE.md` for detailed instructions.

### Quick HTTPS Setup
1. Run `python app_https.py`
2. Accept browser security warning
3. Grant camera permissions when prompted

## Production Deployment

### Environment Variables
```bash
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
DATABASE_URL=your-database-url
```

### Security Recommendations
1. Change default admin credentials
2. Use proper SSL certificates (not self-signed)
3. Set strong SECRET_KEY
4. Configure firewall rules
5. Regular database backups

## Troubleshooting

### Common Issues

1. **Camera not working**
   - Ensure HTTPS is enabled
   - Check browser permissions
   - Try different browser

2. **Database errors**
   - Check file permissions
   - Ensure SQLite is installed
   - Verify disk space

3. **Import failures**
   - Check file format (CSV/Excel)
   - Verify column headers
   - Check file encoding (UTF-8)

## Support

For technical support or questions:
- Check the admin panel for system status
- Review application logs
- Ensure all dependencies are installed

## License

Proprietary software. All rights reserved.