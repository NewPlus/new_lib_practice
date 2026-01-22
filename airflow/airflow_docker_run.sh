
# 기존 컨테이너 정리
echo "Checking for existing airflow container..."
if docker ps -a --format '{{.Names}}' | grep -q '^airflow$'; then
    echo "Removing existing airflow container..."
    docker rm -f airflow
fi

# 컨테이너 실행
docker run -it -p 8080:8080 \
    -v /home/ubuntu/new_lib_practice/airflow/download_rocket_launches.py:/opt/airflow/dags/download_rocket_launches.py \
    -e AIRFLOW__CORE__LOAD_EXAMPLES=False \
    -e AIRFLOW__AUTH_MANAGER__AUTH_MANAGER=airflow.auth.managers.simple.simple_auth_manager.SimpleAuthManager \
    -e AIRFLOW__AUTH_MANAGER__SIMPLE_AUTH_MANAGER__USERNAME=admin \
    -e AIRFLOW__AUTH_MANAGER__SIMPLE_AUTH_MANAGER__PASSWORD=admin \
    --entrypoint=/bin/bash \
    --name airflow \
    apache/airflow:latest \
    -c ' \
        airflow db migrate && \
        airflow api-server & \
        airflow scheduler \
    '
