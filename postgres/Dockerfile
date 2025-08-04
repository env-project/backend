# postgres/Dockerfile

# 1. 공식 PostgreSQL 16 이미지를 기반
FROM postgres:16

# 2. 확장 프로그램을 빌드하는 데 필요한 도구들을 설치
#    --no-cache: 불필요한 캐시를 남기지 않음
#    --virtual .build-deps: 나중에 이 그룹 전체를 한번에 삭제하기 위해 가상 패키지로 묶음
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    postgresql-server-dev-16 \
    curl \
    tar \
    ca-certificates \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 3. pg_uuidv7 확장 프로그램을 다운로드하고 설치
RUN cd /tmp && \
    curl -LO "https://github.com/fboulnois/pg_uuidv7/archive/refs/tags/v1.6.0.tar.gz" && \
    tar -xzf v1.6.0.tar.gz && \
    cd pg_uuidv7-1.6.0 && \
    make && make install

# 4. 설치가 끝났으므로 이미지 용량을 줄이기 위해 불필요한 빌드 도구들과 소스 코드를 모두 삭제
RUN rm -rf /tmp/pg_uuidv7-1.6.0 /tmp/v1.6.0.tar.gz
