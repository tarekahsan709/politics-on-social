# Campaign Analytics Superset Configuration
import os
from celery.schedules import crontab

# Security
SECRET_KEY = os.environ.get('SUPERSET_SECRET_KEY', 'YOUR_SECRET_KEY_HERE')
CSRF_ENABLED = True

# Database configuration
SQLALCHEMY_DATABASE_URI = (
    f"postgresql://{os.environ.get('DATABASE_USER')}:"
    f"{os.environ.get('DATABASE_PASSWORD')}@"
    f"{os.environ.get('DATABASE_HOST')}:"
    f"{os.environ.get('DATABASE_PORT', 5432)}/"
    f"{os.environ.get('DATABASE_DB')}"
)

# Redis configuration
REDIS_HOST = os.environ.get('REDIS_HOST', 'redis')
REDIS_PORT = os.environ.get('REDIS_PORT', 6379)

# Celery configuration for async queries
class CeleryConfig:
    BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'
    CELERY_IMPORTS = ('superset.sql_lab',)
    CELERY_RESULT_BACKEND = f'redis://{REDIS_HOST}:{REDIS_PORT}/1'
    CELERY_ANNOTATIONS = {'tasks.add': {'rate_limit': '10/s'}}
    CELERYBEAT_SCHEDULE = {
        'refresh-campaign-data': {
            'task': 'refresh_campaign_data',
            'schedule': crontab(minute='*/30'),
        },
    }

CELERY_CONFIG = CeleryConfig

# Language configuration - Add Bengali support
LANGUAGES = {
    'en': {'flag': 'us', 'name': 'English'},
    'bn': {'flag': 'bd', 'name': 'বাংলা'}
}

# Feature flags
FEATURE_FLAGS = {
    'ENABLE_TEMPLATE_PROCESSING': True,
    'ENABLE_EXPLORE_DRAG_AND_DROP': True,
    'DASHBOARD_NATIVE_FILTERS': True,
    'DASHBOARD_CROSS_FILTERS': True,
    'EMBEDDABLE_CHARTS': True,
    'SCHEDULED_REPORTS': True,
    'ESTIMATE_QUERY_COST': True,
    'ENABLE_REACT_CRUD_VIEWS': True,
    'ALLOW_ADHOC_SUBQUERY': True,
}

# Custom visualization plugins
CUSTOM_VIZ_TYPE_DENYLIST = []

# Campaign-specific settings
CAMPAIGN_SETTINGS = {
    'DEFAULT_CONSTITUENCY_COUNT': 300,
    'ENABLE_REAL_TIME_UPDATES': True,
    'VOTER_DATA_REFRESH_INTERVAL': 1800,  # 30 minutes
    'SOCIAL_MEDIA_PLATFORMS': ['facebook', 'twitter', 'youtube', 'whatsapp'],
    'ENABLE_BENGALI_SENTIMENT_ANALYSIS': True,
}

# Security settings
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes

# Row level security
ENABLE_ROW_LEVEL_SECURITY = True

# Map configuration for Bangladesh
MAPBOX_API_KEY = os.environ.get('MAPBOX_API_KEY', '')

# Custom CSS for campaign branding
CUSTOM_CSS = """
/* Campaign color scheme */
.navbar {
    background-color: #006a4e !important;  /* Bangladesh green */
}
.btn-primary {
    background-color: #f42a41 !important;  /* Bangladesh red */
    border-color: #f42a41 !important;
}
"""

# Email configuration for alerts
SMTP_HOST = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
SMTP_STARTTLS = True
SMTP_SSL = False
SMTP_USER = os.environ.get('SMTP_USER', '')
SMTP_PORT = 587
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')
SMTP_MAIL_FROM = os.environ.get('SMTP_MAIL_FROM', 'campaign-analytics@example.com')

# Alert configuration
ALERT_REPORTS_NOTIFICATION_DRY_RUN = False
ALERT_MINIMUM_INTERVAL = 300  # 5 minutes

# Performance settings
SUPERSET_WEBSERVER_WORKERS = 4
SUPERSET_WEBSERVER_TIMEOUT = 300
SQL_MAX_ROW = 100000
DISPLAY_MAX_ROW = 10000

# Cache configuration
CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_KEY_PREFIX': 'campaign_',
    'CACHE_REDIS_HOST': REDIS_HOST,
    'CACHE_REDIS_PORT': REDIS_PORT,
    'CACHE_REDIS_DB': 2,
    'CACHE_DEFAULT_TIMEOUT': 300,
}

# Data upload settings
UPLOAD_FOLDER = '/app/upload'
ALLOWED_EXTENSIONS = {'csv', 'xls', 'xlsx', 'json'}
CSV_UPLOAD_MAX_SIZE = 50 * 1024 * 1024  # 50MB

# Custom middleware for campaign analytics
ADDITIONAL_MIDDLEWARE = [
    'campaign_analytics.middleware.ConstituencyAccessMiddleware',
    'campaign_analytics.middleware.AuditLogMiddleware',
]