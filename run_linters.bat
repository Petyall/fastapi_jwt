@echo off
REM Передача первого аргумента (название файла) каждому инструменту

python -m black "%~1" --line-length=128
python -m isort "%~1"
python -m flake8 "%~1"