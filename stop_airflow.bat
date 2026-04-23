@echo off
REM Stop Docker Compose for Airflow
echo Stopping Airflow Docker containers...
docker-compose down
echo Airflow stopped!
pause
