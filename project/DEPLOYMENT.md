# CBT System Deployment Guide

This guide covers deploying the CBT System to production environments.

## Production Checklist

### Security Settings
1. **Environment Variables**
   ```bash
   SECRET_KEY=your-production-secret-key-here
   DEBUG=False
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   ```

2. **Database Configuration**
   ```bash
   DB_ENGINE=django.db.backends.postgresql
   DB_NAME=cbt_production
   DB_USER=cbt_user
   DB_PASSWORD=secure_password
   DB_HOST=localhost
   DB_PORT=5432
   ```

### Static Files
1. **Configure Static Files**
   ```python
   STATIC_ROOT = '/var/www/cbt/static/'
   MEDIA_ROOT = '/var/www/cbt/media/'
   ```

2. **Collect Static Files**
   ```bash
   python manage.py collectstatic --noinput
   ```

### Database Setup
1. **Install PostgreSQL** (recommended for production)
   ```bash
   sudo apt-get install postgresql postgresql-contrib
   ```

2. **Create Database**
   ```sql
   CREATE DATABASE cbt_production;
   CREATE USER cbt_user WITH PASSWORD 'secure_password';
   GRANT ALL PRIVILEGES ON DATABASE cbt_production TO cbt_user;
   ```

3. **Run Migrations**
   ```bash
   python manage.py migrate
   ```

## Deployment Options

### Option 1: Traditional Server (Ubuntu/CentOS)

1. **Install Dependencies**
   ```bash
   sudo apt-get update
   sudo apt-get install python3 python3-pip python3-venv nginx postgresql
   ```

2. **Setup Application**
   ```bash
   cd /var/www/
   git clone your-repo cbt
   cd cbt
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure Nginx**
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;
       
       location /static/ {
           alias /var/www/cbt/static/;
       }
       
       location /media/ {
           alias /var/www/cbt/media/;
       }
       
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

4. **Setup Gunicorn**
   ```bash
   pip install gunicorn
   gunicorn --bind 127.0.0.1:8000 project.wsgi:application
   ```

### Option 2: Docker Deployment

1. **Create Dockerfile**
   ```dockerfile
   FROM python:3.11-slim
   
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   
   COPY . .
   
   EXPOSE 8000
   CMD ["gunicorn", "--bind", "0.0.0.0:8000", "project.wsgi:application"]
   ```

2. **Create docker-compose.yml**
   ```yaml
   version: '3.8'
   services:
     web:
       build: .
       ports:
         - "8000:8000"
       environment:
         - DEBUG=False
         - SECRET_KEY=your-secret-key
       depends_on:
         - db
     
     db:
       image: postgres:13
       environment:
         POSTGRES_DB: cbt_production
         POSTGRES_USER: cbt_user
         POSTGRES_PASSWORD: secure_password
   ```

### Option 3: Cloud Deployment (Heroku)

1. **Install Heroku CLI**
2. **Create Procfile**
   ```
   web: gunicorn project.wsgi:application
   release: python manage.py migrate
   ```

3. **Deploy**
   ```bash
   heroku create your-cbt-app
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set DEBUG=False
   git push heroku main
   ```

## Performance Optimization

### Database Optimization
1. **Add Database Indexes**
   ```python
   # In models.py
   class Question(models.Model):
       subject = models.ForeignKey(Subject, on_delete=models.CASCADE, db_index=True)
       class_group = models.ForeignKey(StudentClass, on_delete=models.CASCADE, db_index=True)
   ```

2. **Use Database Connection Pooling**
   ```python
   # Install django-db-pool
   pip install django-db-pool
   ```

### Caching
1. **Install Redis**
   ```bash
   sudo apt-get install redis-server
   pip install django-redis
   ```

2. **Configure Caching**
   ```python
   CACHES = {
       'default': {
           'BACKEND': 'django_redis.cache.RedisCache',
           'LOCATION': 'redis://127.0.0.1:6379/1',
       }
   }
   ```

## Monitoring and Logging

### Logging Configuration
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/cbt/django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### Health Checks
Create a simple health check endpoint:
```python
# In urls.py
path('health/', lambda request: HttpResponse('OK'), name='health'),
```

## Backup Strategy

### Database Backup
```bash
# Create backup script
#!/bin/bash
pg_dump cbt_production > /backups/cbt_$(date +%Y%m%d_%H%M%S).sql
```

### Media Files Backup
```bash
# Backup media files
rsync -av /var/www/cbt/media/ /backups/media/
```

## SSL/HTTPS Setup

### Using Let's Encrypt
```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

### Django HTTPS Settings
```python
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

## Maintenance

### Regular Tasks
1. **Update Dependencies**
   ```bash
   pip install -r requirements.txt --upgrade
   ```

2. **Database Maintenance**
   ```bash
   python manage.py clearsessions  # Clear expired sessions
   ```

3. **Log Rotation**
   ```bash
   # Setup logrotate for Django logs
   sudo nano /etc/logrotate.d/django
   ```

### Monitoring Commands
```bash
# Check system resources
htop
df -h
free -m

# Check application logs
tail -f /var/log/cbt/django.log

# Check database connections
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"
```

## Troubleshooting

### Common Issues
1. **Static files not serving**: Check STATIC_ROOT and run collectstatic
2. **Database connection errors**: Verify database credentials and connectivity
3. **Permission errors**: Check file permissions for media and static directories
4. **Memory issues**: Monitor memory usage and consider adding swap space

### Debug Mode in Production
Never run with DEBUG=True in production. For debugging:
1. Check logs in /var/log/cbt/
2. Use Django's logging framework
3. Set up error reporting (e.g., Sentry)

## Security Considerations

1. **Regular Updates**: Keep Django and dependencies updated
2. **Firewall**: Configure firewall to only allow necessary ports
3. **Database Security**: Use strong passwords and limit database access
4. **File Permissions**: Set appropriate permissions on application files
5. **Backup Security**: Encrypt backups and store securely

This deployment guide provides a foundation for deploying the CBT System in various environments. Adjust configurations based on your specific requirements and infrastructure.
