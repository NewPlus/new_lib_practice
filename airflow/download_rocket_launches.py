import json
import pathlib
from datetime import datetime, timedelta

import requests
import requests.exceptions as requests_exceptions
from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.python import PythonOperator


dag=DAG(
    dag_id="download_rocket_launches",
    start_date=datetime.now() - timedelta(days=14),
    schedule=None,
)

download_launches=BashOperator(
    task_id="download_launches",
    bash_command="curl -o /tmp/launches.json -L https://ll.thespacedevs.com/2.2.0/launch/upcoming/",
    dag=dag,
)


def _get_pictures():
    # 경로가 존재하는지 확인
    pathlib.Path("/tmp/images").mkdir(parents=True, exist_ok=True)

    # launches.json 파일에 있는 모든 그림 파일을 다운로드
    with open("/tmp/launches.json") as f:
        launches=json.load(f)
        
        # API throttle 에러 체크
        if "detail" in launches:
            print(f"API Error: {launches['detail']}")
            return
        
        # results 키가 있는지 확인
        if "results" not in launches:
            print(f"Error: 'results' key not found in API response. Available keys: {list(launches.keys())}")
            return
            
        image_urls=[launch["image"] for launch in launches["results"]]
        print(f"Found {len(image_urls)} images to download")
        
        for image_url in image_urls:
            if not image_url:  # None or empty string check
                print(f"Skipping empty image URL")
                continue
                
            try:
                response=requests.get(image_url)
                response.raise_for_status()  # HTTP 에러 체크
                image_filename=image_url.split("/")[-1]
                target_file=f"/tmp/images/{image_filename}"
                with open(target_file, "wb") as f:
                    f.write(response.content)
                print(f"Downloaded {image_url} to {target_file}")
            except requests_exceptions.MissingSchema:
                print(f"{image_url} appears to be an invalid URL.")
            except requests_exceptions.ConnectionError:
                print(f"Could not connect to {image_url}.")
            except Exception as e:
                print(f"Error downloading {image_url}: {str(e)}")

get_pictures = PythonOperator(
    task_id="get_pictures",
    python_callable=_get_pictures,
    dag=dag,
)

notify = BashOperator(
    task_id="notify",
    bash_command='echo "There are now $(ls /tmp/images | wc -l) images."',
    dag=dag,
)

download_launches >> get_pictures >> notify
