if __name__ == "__main__":
    import os
    import sys
    import subprocess
    
    # requirements 파일 변수
    req_file = "requirements.txt"
    
    # requirements 설치
    if not os.getenv("REQUIREMENTS_INSTALLED"):
        if os.path.exists(req_file):
            subprocess.run(["python", "-m", "pip", "install", "-r", req_file], check=True)
            
            os.environ["REQUIREMENTS_INSTALLED"] = "1"
            
            os.execl(sys.executable, sys.executable, *sys.argv)
            sys.exit()
    
    # main 함수 진입
    from timetable.main import main
    main()