# 1. Python 3.13 slim 버전을 기반으로 시작
FROM python:3.13-slim

# 2. 작업 디렉토리를 /app으로 설정
WORKDIR /app

# 3. 시스템 패키지를 업데이트하고, pipx를 설치
RUN apt-get update && \
    apt-get install -y pipx && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# 4. pipx를 사용하여 Poetry를 설치
RUN pipx install poetry
ENV PATH="/root/.local/bin:$PATH"

# 5. 의존성 파일들을 먼저 복사
COPY pyproject.toml poetry.lock* ./

# 6. Poetry를 사용하여 의존성을 설치
RUN poetry install --no-root --no-interaction --no-ansi

# 7. 나머지 모든 소스 코드를 복사
COPY . .

# 8. 컨테이너가 시작될 때 실행할 기본 명령어를 설정
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
