@echo off

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created.
) else (
    echo Virtual environment already exists.
)

call venv\Scripts\activate
echo Virtual environment activated.

REM Install pip packages here from requirements.txt
