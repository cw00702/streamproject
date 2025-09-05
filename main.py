# main.py
from etlpipeline.pipeline import run_full_pipeline  # 전체 ETL 함수
# (스케줄 루프가 별도라면) from pipeline import run_scheduler_loop
import os

def main():
    run_full_pipeline()

if __name__ == "__main__":
    RUN_ONCE = os.getenv("RUN_ONCE", "0") == "1"
    if RUN_ONCE:
        # GitHub Actions에서 단발 실행
        main()
    else:
        # 로컬에서 계속 돌리고 싶을 때만 사용(기존처럼)
        # run_scheduler_loop()
        main()  # 필요 없으면 이 줄만 유지
