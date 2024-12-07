@echo off

:: Obtén la ruta del directorio donde se encuentra el archivo .bat
set BAT_DIR=%~dp0
set STREAMLIT_APP=%BAT_DIR%app.py

:: Anaconda
set USER_DIR=%USERPROFILE%
set ANACONDA_DIR=%USER_DIR%\anaconda3
call "%ANACONDA_DIR%\Scripts\activate.bat" py311
python -m pip install -r src/requirements.txt

:: Ejecuta la aplicación Streamlit
streamlit run app.py

:: Pausa para mantener abierta la ventana del terminal si ocurre algún error
pause