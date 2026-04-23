# Docker Airflow Setup Guide

## Prerequisites
- **Docker Desktop** installed on Windows (download from https://www.docker.com/products/docker-desktop)
- Windows 10/11 with WSL2 enabled (Docker Desktop installs this automatically)
- At least 4GB RAM allocated to Docker

## What Was Set Up

### 1. **docker-compose.yml**
   - **PostgreSQL 15**: Database for Airflow metadata
   - **Airflow Webserver**: Web UI on `http://localhost:8080`
   - **Airflow Scheduler**: Task scheduler daemon
   - All configured to work together automatically

### 2. **Directory Structure Created**
   ```
   airflow/
   ├── dags/          → Your workflow definitions go here
   ├── logs/          → Airflow execution logs
   └── plugins/       → Custom Airflow plugins (optional)
   ```

### 3. **Startup Scripts**
   - `start_airflow.bat` → Launch all services
   - `stop_airflow.bat` → Stop all services

## How to Start Airflow

### Option 1: Automated (Easiest)
```bash
# Double-click: start_airflow.bat
```
This will:
- Start PostgreSQL, Webserver, and Scheduler
- Wait 30 seconds for initialization
- Create admin user (admin/admin)
- Open http://localhost:8080

### Option 2: Manual Command Line
```powershell
cd "C:\Users\Asus TUF F15\Downloads\Project\MSC DS"
docker-compose up -d
```

## Access Airflow

- **URL**: http://localhost:8080
- **Username**: admin
- **Password**: admin

## Key Commands

```bash
# View logs
docker-compose logs -f airflow-webserver
docker-compose logs -f airflow-scheduler

# Execute command inside container
docker-compose exec airflow-webserver airflow dags list

# Stop all services
docker-compose down

# Remove all data (fresh start)
docker-compose down -v
```

## File Volumes (Connected to Your PC)

| Container Path | Windows Path | Purpose |
|---|---|---|
| `/opt/airflow/dags` | `./airflow/dags` | Your DAG files |
| `/opt/airflow/logs` | `./airflow/logs` | Execution logs |
| `/opt/airflow/data` | `./data` | CSV/data files |
| `/opt/airflow/src` | `./src` | Your Python modules |

You can edit DAG files directly on Windows, and Airflow will pick them up automatically.

## Troubleshooting

### Port 8080 Already in Use
```bash
# Find what's using port 8080
netstat -ano | findstr :8080

# Kill the process (if needed)
taskkill /PID <PID> /F
```

### Docker Service Not Running
```bash
# Make sure Docker Desktop is running
# Check: Start → Docker Desktop
```

### Can't Connect to http://localhost:8080
```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs airflow-webserver
```

## Next Steps

1. ✅ **Docker setup complete** - Services will auto-start with Airflow
2. ⏳ **Create DAG files** - Add Python files to `airflow/dags/`
3. ⏳ **Configure data ingestion** - Set up tasks to fetch NAV data
4. ⏳ **Set up ML pipeline** - Create tasks for feature engineering, clustering, ranking
5. ⏳ **Test execution** - Run DAGs from Airflow UI to verify workflow
