#!/usr/bin/env bash
set -eo pipefail

COLOR_GREEN=`tput setaf 2;`
COLOR_NC=`tput sgr0;` # No Color

echo "Starting black"
poetry run black .
echo "OK"

echo "Starting ruff"
poetry run ruff check --select I --fix  # isort import 정렬
poetry run ruff check --fix  # flake linter
echo "OK"

#echo "Starting mypy"  # 정적 분석 도구
#poetry run mypy .
#echo "OK"
#
#echo "Starting pytest with coverage"
#poetry run coverage run -m pytest
#poetry run coverage report -m
#poetry run coverage html

echo "${COLOR_GREEN}All tests passed successfully!${COLOR_NC}"