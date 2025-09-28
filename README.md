# Campaign Analytics Dashboard

A powerful, open-source analytics platform built on Apache Superset, customized for Bangladesh election campaigns.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- At least 8GB RAM
- 20GB free disk space

### Installation

1. Clone this repository:
```bash
git clone <your-repo-url>
cd campaign-analytics
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configurations
```

3. Start the services:
```bash
docker-compose up -d
```

4. Initialize Superset:
```bash
docker exec -it campaign_superset superset fab create-admin \
    --username admin \
    --firstname Campaign \
    --lastname Admin \
    --email admin@campaign.bd \
    --password admin

docker exec -it campaign_superset superset db upgrade
docker exec -it campaign_superset superset init
```

5. Access the dashboard:
- Superset: http://localhost:8088
- Metabase (optional): http://localhost:3000

## 📊 Features

### Core Dashboards
1. **Campaign Overview** - Real-time campaign metrics
2. **Voter Analytics** - Demographic analysis and predictions
3. **Social Media Command Center** - Multi-platform monitoring
4. **Field Operations** - Volunteer and ground activity tracking

### Bangladesh-Specific Features
- 🇧🇩 Bengali language support
- 📍 300 constituency mapping
- 💰 Local payment gateway integration (bKash, Rocket, Nagad)
- 📱 Mobile-first responsive design
- 🔌 Offline capability for field operations

### Advanced Analytics
- Predictive voter turnout modeling
- Sentiment analysis for Bengali content
- Real-time alert system
- Resource optimization algorithms

## 🛠️ Customization Guide

### Adding Custom Visualizations
```python
# Place in custom_visualizations/constituency_map.py
from superset.viz import BaseViz

class ConstituencyMapViz(BaseViz):
    viz_type = "constituency_map"
    verbose_name = "Bangladesh Constituency Map"
    # Implementation details...
```

### Creating Campaign-Specific Metrics
```sql
-- Add to init_scripts/campaign_metrics.sql
CREATE OR REPLACE VIEW voter_engagement_score AS
SELECT 
    constituency_id,
    (rally_attendance + door_visits + social_engagement) / 3 as score
FROM campaign_activities;
```

## 📱 Mobile App Integration

The platform provides REST APIs for mobile app integration:
```bash
GET /api/v1/campaign/constituency/{id}/metrics
GET /api/v1/campaign/realtime/social-sentiment
POST /api/v1/campaign/field-report
```

## 🔒 Security

- Row-level security by constituency
- Two-factor authentication
- Encrypted data at rest and in transit
- Audit logging for all data access

## 📈 Performance Optimization

- Redis caching for frequently accessed data
- Materialized views for complex queries
- CDN integration for static assets
- Horizontal scaling support via Kubernetes

## 🌐 Multi-language Support

Currently supports:
- English
- বাংলা (Bengali)

To add more languages, edit `superset_config.py`:
```python
LANGUAGES = {
    'en': {'flag': 'us', 'name': 'English'},
    'bn': {'flag': 'bd', 'name': 'বাংলা'},
    # Add more languages here
}
```

## 📚 Documentation

- [User Guide](docs/user-guide.md)
- [Admin Guide](docs/admin-guide.md)
- [API Documentation](docs/api-docs.md)
- [Troubleshooting](docs/troubleshooting.md)

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the Apache License 2.0 - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Built on top of these amazing open-source projects:
- [Apache Superset](https://superset.apache.org/)
- [PostgreSQL](https://www.postgresql.org/)
- [Redis](https://redis.io/)
- [Docker](https://www.docker.com/)

## 📞 Support

For support and questions:
- Create an issue in this repository
- Email: support@campaign-analytics.bd
- Slack: #campaign-analytics

---

**Note**: Remember to change default passwords and secure your installation before using in production!