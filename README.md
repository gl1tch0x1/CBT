# CBT System - Computer-Based Testing Application

A comprehensive Django-based Computer-Based Testing (CBT) system that allows educational institutions to create, manage, and conduct online examinations.

## Features

### Core Features
- **User Management**: Support for Admin, Staff (Teachers), and Students
- **Question Bank**: Centralized repository for questions with rich text support
- **Exam Management**: Create and manage exams with customizable settings
- **Real-time Exam Taking**: Timer-based exam interface with auto-submission
- **Result Management**: Comprehensive scoring and result analysis
- **Academic Management**: Support for sessions, terms, subjects, and classes

### Key Capabilities
- ✅ Role-based access control (Admin, Staff, Student)
- ✅ Rich question editor with multiple choice support
- ✅ Configurable exam duration and question count
- ✅ Real-time countdown timer during exams
- ✅ Auto-submission when time expires
- ✅ Detailed result analysis with feedback
- ✅ Question bank with filtering and search
- ✅ Responsive Bootstrap 5 UI
- ✅ Print-friendly result reports

## Installation

### Prerequisites
- Python 3.8+
- Django 5.1+
- Virtual environment (recommended)

### Setup Instructions

1. **Clone or extract the project**
   ```bash
   cd project
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   - Copy `.env.example` to `.env` (if available)
   - Update the `.env` file with your settings
   - Or use the existing `.env` file

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Load sample data (optional)**
   ```bash
   python manage.py populate_sample_data
   ```

8. **Run the development server**
   ```bash
   set DJANGO_SETTINGS_MODULE=project.settings && python manage.py runserver
   ```

9. **Access the application**
   - Open your browser and go to `http://127.0.0.1:8000`

## Default Login Credentials

After running the sample data command:

- **Admin**: admin / admin123
- **Teacher**: teacher / teacher123  
- **Student**: student1 / student123

## Usage Guide

### For Administrators
1. **User Management**: Create and manage staff and student accounts
2. **Academic Setup**: Configure sessions, terms, subjects, and classes
3. **System Oversight**: Monitor all exams and results across the system

### For Teachers/Staff
1. **Question Bank**: Create and manage questions for your subjects
2. **Exam Creation**: Set up exams with custom duration and settings
3. **Question Assignment**: Add questions to exams from the question bank
4. **Result Analysis**: View and analyze student performance

### For Students
1. **Take Exams**: Access available exams for your class
2. **View Results**: Check your exam scores and detailed feedback
3. **Exam History**: Review past exam attempts and performance

## Project Structure

```
project/
├── apps/
│   ├── core/           # User management, academic setup
│   └── exam/           # Exam and question management
├── templates/          # HTML templates
├── static/            # Static files (CSS, JS, images)
├── media/             # User uploaded files
├── manage.py          # Django management script
└── project/           # Main project settings
```

## Key Models

### Core App
- **User**: Extended user model with role support
- **Subject**: Academic subjects
- **StudentClass**: Class/grade levels
- **AcademicTerm**: Academic terms (e.g., First Term)
- **AcademicSession**: Academic years (e.g., 2024/2025)

### Exam App
- **Question**: Questions with subject and class association
- **Choice**: Multiple choice options for questions
- **Exam**: Exam configuration and settings
- **Answer**: Student exam submissions and scores

## API Endpoints

The system uses Django's built-in views. Key URL patterns:

- `/` - Dashboard (role-based)
- `/accounts/login/` - User login
- `/exam/` - Exam management
- `/questionbank/` - Question bank management
- `/admin/` - Django admin interface

## Configuration

### Environment Variables
- `SECRET_KEY`: Django secret key
- `DEBUG`: Debug mode (True/False)
- `ALLOWED_HOSTS`: Allowed host names
- `DB_ENGINE`: Database engine
- `DB_NAME`: Database name

### Customization
- Modify templates in the `templates/` directory
- Add custom CSS/JS in the `static/` directory
- Extend models in the respective apps

## Security Features

- CSRF protection on all forms
- User authentication and authorization
- Role-based access control
- Session management
- SQL injection protection (Django ORM)

## Browser Support

- Chrome (recommended)
- Firefox
- Safari
- Edge
- Mobile browsers (responsive design)

## Troubleshooting

### Common Issues

1. **Server won't start**
   - Ensure virtual environment is activated
   - Check if all dependencies are installed
   - Verify database migrations are applied

2. **Login issues**
   - Use the default credentials provided
   - Check if user accounts exist in the database

3. **Static files not loading**
   - Run `python manage.py collectstatic` in production
   - Check STATIC_URL and STATIC_ROOT settings

### Getting Help

1. Check the Django logs for error messages
2. Verify all migrations are applied: `python manage.py showmigrations`
3. Test with sample data: `python manage.py populate_sample_data`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For support and questions, please refer to the Django documentation or create an issue in the project repository.
