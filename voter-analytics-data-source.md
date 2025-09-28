# Voter Analytics Data Source for Apache Superset

## Primary Data Source: Electoral Commission Voter Roll

### Option 1: Official Election Commission Database (Recommended)
The Bangladesh Election Commission maintains the National Identity Registration Wing (NIDW) database. This would be your most authoritative source.

**Data Available:**
- NID (National ID) - anonymized/hashed for privacy
- Age group
- Gender  
- Constituency
- District/Upazila/Union
- Voting center
- Urban/Rural classification

**Access Method:**
- Official API (if available)
- Bulk data export (CSV/Excel)
- Database replica access

### Option 2: Build Your Own Voter Database
If official access is limited, create a campaign voter database:

```sql
-- Core voter analytics table structure
CREATE TABLE voter_registry (
    id SERIAL PRIMARY KEY,
    -- Location Information
    constituency_id INTEGER NOT NULL,
    constituency_name VARCHAR(255),
    district VARCHAR(100),
    upazila VARCHAR(100),
    union_ward VARCHAR(100),
    voting_center_id VARCHAR(50),
    voting_center_name VARCHAR(255),
    
    -- Demographics (Aggregated for Privacy)
    age_group VARCHAR(20), -- '18-25', '26-35', '36-50', '51-65', '65+'
    gender VARCHAR(10), -- 'M', 'F', 'Other'
    occupation_category VARCHAR(50), -- 'Student', 'Farmer', 'Business', etc.
    education_level VARCHAR(50), -- 'Primary', 'Secondary', 'Higher', etc.
    
    -- Voter Metrics
    total_voters INTEGER,
    new_voters INTEGER, -- First time voters
    
    -- Historical Data
    turnout_2018 DECIMAL(5,2), -- Percentage
    turnout_2014 DECIMAL(5,2),
    turnout_2008 DECIMAL(5,2),
    
    -- Derived Fields
    urban_rural VARCHAR(10),
    economic_category VARCHAR(20), -- 'Low', 'Middle', 'High'
    
    -- Metadata
    data_source VARCHAR(50),
    last_updated TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for performance
CREATE INDEX idx_constituency ON voter_registry(constituency_id);
CREATE INDEX idx_district ON voter_registry(district);
CREATE INDEX idx_demographics ON voter_registry(age_group, gender);
```

## Data Collection Methods

### 1. Government Sources
```python
# Example: Parsing election commission data
import pandas as pd

def import_election_commission_data(file_path):
    """
    Import voter data from Election Commission CSV/Excel
    """
    df = pd.read_csv(file_path, encoding='utf-8')
    
    # Standardize constituency names
    df['constituency_name'] = df['constituency_name'].str.strip()
    
    # Create age groups
    df['age_group'] = pd.cut(df['age'], 
                             bins=[18, 25, 35, 50, 65, 100],
                             labels=['18-25', '26-35', '36-50', '51-65', '65+'])
    
    # Aggregate for privacy
    aggregated = df.groupby(['constituency_id', 'age_group', 'gender']).agg({
        'voter_id': 'count'
    }).rename(columns={'voter_id': 'total_voters'})
    
    return aggregated
```

### 2. Field Survey Data
```sql
-- Supplementary table for field-collected data
CREATE TABLE voter_survey_data (
    id SERIAL PRIMARY KEY,
    constituency_id INTEGER,
    survey_date DATE,
    
    -- Sample demographics
    respondent_age_group VARCHAR(20),
    respondent_gender VARCHAR(10),
    respondent_occupation VARCHAR(50),
    
    -- Voting intention (anonymized)
    likely_to_vote BOOLEAN,
    issues_priority JSONB, -- {"economy": 5, "education": 4, ...}
    
    -- Metadata
    surveyor_id VARCHAR(50),
    survey_method VARCHAR(20), -- 'door-to-door', 'phone', 'online'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Data Pipeline Architecture

```yaml
# Apache Airflow DAG for voter data pipeline
from airflow import DAG
from datetime import datetime, timedelta

default_args = {
    'owner': 'campaign-analytics',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
}

dag = DAG(
    'voter_data_pipeline',
    default_args=default_args,
    description='Voter analytics data pipeline',
    schedule_interval='@daily',
)

# Task 1: Import official data
import_official_data = PythonOperator(
    task_id='import_election_commission_data',
    python_callable=import_from_election_commission,
    dag=dag,
)

# Task 2: Process and aggregate
process_data = PythonOperator(
    task_id='process_voter_data',
    python_callable=process_and_aggregate,
    dag=dag,
)

# Task 3: Load to Superset
load_to_database = PythonOperator(
    task_id='load_to_superset_db',
    python_callable=load_to_postgresql,
    dag=dag,
)

import_official_data >> process_data >> load_to_database
```

## Superset Configuration

### 1. Database Connection
```python
# In Superset UI or via API
database_config = {
    "database_name": "Voter Analytics DB",
    "sqlalchemy_uri": "postgresql://user:pass@localhost:5432/voter_analytics",
    "cache_timeout": 300,
    "expose_in_sqllab": True,
    "allow_ctas": True,
    "allow_cvas": True,
}
```

### 2. Create Dataset
```sql
-- Create a view for Superset
CREATE OR REPLACE VIEW voter_analytics_view AS
SELECT 
    vr.*,
    -- Calculate derived metrics
    CASE 
        WHEN age_group IN ('18-25', '26-35') THEN 'Youth'
        WHEN age_group IN ('36-50') THEN 'Middle Age'
        ELSE 'Senior'
    END as age_category,
    
    -- Historical turnout average
    (COALESCE(turnout_2018, 0) + COALESCE(turnout_2014, 0) + COALESCE(turnout_2008, 0)) / 
    NULLIF(
        (CASE WHEN turnout_2018 IS NOT NULL THEN 1 ELSE 0 END +
         CASE WHEN turnout_2014 IS NOT NULL THEN 1 ELSE 0 END +
         CASE WHEN turnout_2008 IS NOT NULL THEN 1 ELSE 0 END), 0
    ) as avg_historical_turnout
FROM voter_registry vr;
```

### 3. Key Metrics for Superset
```sql
-- Metrics to configure in Superset
-- 1. Total Registered Voters
SELECT SUM(total_voters) as total_registered_voters
FROM voter_analytics_view;

-- 2. Youth Voter Percentage
SELECT 
    (SUM(CASE WHEN age_group IN ('18-25', '26-35') THEN total_voters ELSE 0 END)::FLOAT / 
     SUM(total_voters) * 100) as youth_voter_percentage
FROM voter_analytics_view;

-- 3. Gender Balance Index
SELECT 
    ABS(
        SUM(CASE WHEN gender = 'M' THEN total_voters ELSE 0 END) - 
        SUM(CASE WHEN gender = 'F' THEN total_voters ELSE 0 END)
    )::FLOAT / SUM(total_voters) as gender_balance_index
FROM voter_analytics_view;

-- 4. New Voter Impact
SELECT 
    (SUM(new_voters)::FLOAT / SUM(total_voters) * 100) as new_voter_percentage
FROM voter_analytics_view;
```

## Privacy & Compliance

### Data Privacy Rules
1. **No Personal Identifiers**: Never store names, NID numbers, or addresses
2. **Aggregation**: Always aggregate data to groups of 50+ people
3. **Hashing**: If IDs needed, use one-way hashing
4. **Access Control**: Implement row-level security by constituency

### Compliance Checklist
- [ ] Follow Bangladesh Data Protection Act
- [ ] Get necessary permissions from Election Commission
- [ ] Implement audit logging
- [ ] Regular data purging policy
- [ ] Encrypted storage and transmission

## Quick Start Implementation

```bash
# 1. Create database
createdb voter_analytics

# 2. Run schema creation
psql voter_analytics < voter_schema.sql

# 3. Import sample data
python import_voter_data.py --source ec_data_2023.csv

# 4. Connect to Superset
# Go to Superset UI > Data > Databases > + Database
# Add PostgreSQL connection string

# 5. Create charts
# Go to Charts > + Chart > Select voter_analytics_view
```

## Sample Queries for Insights

```sql
-- 1. Constituency Competitiveness Index
WITH turnout_variance AS (
    SELECT 
        constituency_id,
        STDDEV(ARRAY[turnout_2018, turnout_2014, turnout_2008]) as turnout_volatility
    FROM voter_registry
    GROUP BY constituency_id
)
SELECT * FROM turnout_variance ORDER BY turnout_volatility DESC LIMIT 20;

-- 2. Youth vs Senior Voter Distribution
SELECT 
    constituency_name,
    SUM(CASE WHEN age_group IN ('18-25', '26-35') THEN total_voters ELSE 0 END) as youth_voters,
    SUM(CASE WHEN age_group IN ('51-65', '65+') THEN total_voters ELSE 0 END) as senior_voters,
    SUM(total_voters) as total
FROM voter_registry
GROUP BY constituency_name;
```

This single data source approach gives you a solid foundation to build your voter analytics dashboard in Superset!