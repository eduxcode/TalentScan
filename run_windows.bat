@echo off
setlocal

echo ==========================================
echo      TalentScan - Inicializacao
echo ==========================================

REM Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python nao encontrado. Por favor, instale o Python 3.7 ou superior.
    pause
    exit /b 1
)

REM Verificar se o ambiente virtual existe
if not exist "venv" (
    echo [INFO] Criando ambiente virtual...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERRO] Falha ao criar ambiente virtual.
        pause
        exit /b 1
    )
    echo [OK] Ambiente virtual criado.
)

REM Ativar ambiente virtual
call venv\Scripts\activate
if %errorlevel% neq 0 (
    echo [ERRO] Falha ao ativar ambiente virtual.
    pause
    exit /b 1
)

REM Atualizar pip
python -m pip install --upgrade pip >nul 2>&1

REM Instalar dependencias
if exist "requirements.txt" (
    echo [INFO] Verificando dependencias...
    pip install -r requirements.txt >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERRO] Falha ao instalar dependencias.
        pause
        exit /b 1
    )
    echo [OK] Dependencias verificadas.
) else (
    echo [AVISO] Arquivo requirements.txt nao encontrado.
)

REM Verificar arquivo .env
if not exist ".env" (
    if exist "config.env.example" (
        echo [INFO] Criando arquivo .env a partir do exemplo...
        copy config.env.example .env >nul
        echo [AVISO] Por favor, edite o arquivo .env com sua chave da API OpenAI.
        notepad .env
    ) else (
        echo [AVISO] Arquivo de configuracao nao encontrado.
    )
)

REM Executar a aplicacao
echo.
echo [INFO] Iniciando TalentScan...
echo.

python talent_scan.py %*

if %errorlevel% neq 0 (
    echo.
    echo [ERRO] A aplicacao encerrou com erro.
)

echo.
echo Pressione qualquer tecla para sair...
pause >nul
