@echo off
REM Start Docker Compose for Airflow
echo Starting Airflow with Docker...
docker-compose up -d

REM Wait for services to be ready
echo Waiting for services to initialize (30 seconds)...
timeout /t 30 /nobreak

REM Create admin user
echo Creating Airflow admin user...
docker-compose exec -T airflow-webserver airflow users create ^
  --username admin ^
  --firstname Admin ^
  --lastname User ^
  --role Admin ^
  --email admin@example.com ^
  --password admin

echo.
echo Airflow is starting! Access it at: http://localhost:8080
echo Default credentials - Username: admin, Password: admin
echo.
pause
