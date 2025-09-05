from etlpipeline.pipeline import run_full_pipeline
from multiprocessing import Process
import time, schedule, datetime as dt, os, traceback

# === 설정값 ===
MAX_ATTEMPTS = 2           # 한 회차에서 재시도 횟수
RETRY_BACKOFF = 10         # 재시도 사이 대기(초)
HARD_TIMEOUT = 300         # 파이프라인 하드 타임아웃(초) — 2분30초면 300초면 충분
LOG_FILE = "scheduler.log"

RUNNING = False            # 겹침 방지 플래그


def log(msg: str):
    ts = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass

def _run_pipeline_once():
    """
    파이프라인 1회 실행. 실패 시 예외를 위로 올림.
    run_full_pipeline() 내부에서 예외를 던지도록 구현되어 있으면 가장 깨끗함.
    """
    run_full_pipeline()  # 실패 시 예외 발생(권장)
    
def _run_with_timeout(target, timeout: int):
    """
    별도 프로세스로 파이프라인을 실행하고, timeout을 넘기면 강제 종료.
    성공 시 None(예외 없음), 실패 시 Exception을 main 프로세스에서 만들어서 반환.
    """
    # 파이프라인을 subprocess에서 돌리면, 메인 루프가 hang되지 않음
    p = Process(target=target)
    p.start()
    p.join(timeout)
    if p.is_alive():
        p.terminate()
        p.join(5)
        return TimeoutError(f"Pipeline hard-timeout after {timeout}s")
    # 종료코드 검사(자식 프로세스에서 예외가 나면 종료코드가 1 이상)
    if p.exitcode != 0:
        return RuntimeError(f"Pipeline exited with code {p.exitcode}")
    return None


def schedule_task():
    global RUNNING
    if RUNNING:
        log("이전 작업이 아직 실행 중이라 이번 트리거는 건너뜁니다.")
        return

    RUNNING = True
    start = time.time()
    log(" 스케줄러가 실행되었습니다.")

    try:
        # 재시도 루프
        last_err = None
        for attempt in range(1, MAX_ATTEMPTS + 1):
            log(f"ETL 시도 {attempt}/{MAX_ATTEMPTS}")
            err = _run_with_timeout(_run_pipeline_once, HARD_TIMEOUT)
            if err is None:
                # 성공
                elapsed = time.time() - start
                log(f"ETL 성공, 실행 시간: {elapsed:.1f}s")
                break
            else:
                last_err = err
                log(f"ETL 실패(시도 {attempt}): {err}")
                if attempt < MAX_ATTEMPTS:
                    log(f"⏳ {RETRY_BACKOFF}s 후 재시도합니다…")
                    time.sleep(RETRY_BACKOFF)
        else:
            # 모든 시도 실패 → 여기서 굳이 더 돌리지 않고 다음 스케줄에 맡김
            log(f"이번 회차 최종 실패: {last_err}")
    except Exception as e:
        # 이 블록은 _run_with_timeout 자체가 예외를 던지는 경우에만 들어옴(거의 없음)
        log("스케줄러 레벨 예외 발생")
        log(traceback.format_exc())
    finally:
        RUNNING = False
        log("스케줄러 작업 종료")


if __name__ == "__main__":
    
    log("스케줄러가 시작되었습니다.")
    for hour in range(0, 24):
        schedule.every().day.at(f"{hour:02d}:05").do(schedule_task)
        schedule.every().day.at(f"{hour:02d}:10").do(schedule_task)
        schedule.every().day.at(f"{hour:02d}:15").do(schedule_task)
        schedule.every().day.at(f"{hour:02d}:00").do(schedule_task)
        schedule.every().day.at(f"{hour:02d}:25").do(schedule_task)
        schedule.every().day.at(f"{hour:02d}:30").do(schedule_task)
        schedule.every().day.at(f"{hour:02d}:35").do(schedule_task)
        schedule.every().day.at(f"{hour:02d}:40").do(schedule_task)
        schedule.every().day.at(f"{hour:02d}:45").do(schedule_task)
        schedule.every().day.at(f"{hour:02d}:50").do(schedule_task)
        schedule.every().day.at(f"{hour:02d}:55").do(schedule_task)
        schedule.every().day.at(f"{hour:02d}:20").do(schedule_task)
    
    while True:
        schedule.run_pending()
        time.sleep(1)
        
    print("스케줄러가 종료되었습니다.")