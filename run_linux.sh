#!/bin/bash

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}==========================================${NC}"
echo -e "${GREEN}     TalentScan - Inicialização (Linux)   ${NC}"
echo -e "${GREEN}==========================================${NC}"

# Função para verificar erros
check_error() {
    if [ $? -ne 0 ]; then
        echo -e "${RED}[ERRO] $1${NC}"
        exit 1
    fi
}

# Verificar Python
if command -v python3 &>/dev/null; then
    PYTHON_CMD=python3
elif command -v python &>/dev/null; then
    PYTHON_CMD=python
else
    echo -e "${RED}[ERRO] Python não encontrado. Instale Python 3.7+.${NC}"
    exit 1
fi

# Verificar/Criar venv
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}[INFO] Criando ambiente virtual...${NC}"
    $PYTHON_CMD -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}[ERRO] Falha ao criar ambiente virtual.${NC}"
        echo -e "${YELLOW}[AJUDA] No Linux, você pode precisar instalar o pacote venv.${NC}"
        echo -e "${YELLOW}[AJUDA] Tente executar: sudo apt install python3-venv (ou equivalente para sua distro)${NC}"
        exit 1
    fi
    echo -e "${GREEN}[OK] Ambiente virtual criado.${NC}"
fi

# Ativar venv
source venv/bin/activate
check_error "Falha ao ativar ambiente virtual."

# Instalar dependências
if [ -f "requirements.txt" ]; then
    echo -e "${YELLOW}[INFO] Verificando dependências...${NC}"
    pip install -r requirements.txt >/dev/null 2>&1
    check_error "Falha ao instalar dependências."
    echo -e "${GREEN}[OK] Dependências verificadas.${NC}"
else
    echo -e "${YELLOW}[AVISO] Arquivo requirements.txt não encontrado.${NC}"
fi

# Verificar .env
if [ ! -f ".env" ]; then
    if [ -f "config.env.example" ]; then
        echo -e "${YELLOW}[INFO] Criando arquivo .env...${NC}"
        cp config.env.example .env
        echo -e "${YELLOW}[AVISO] Edite o arquivo .env com sua chave API.${NC}"
        # Tentar abrir editor padrão ou nano
        if [ -n "$EDITOR" ]; then
            $EDITOR .env
        else
            nano .env
        fi
    fi
fi

# Executar aplicação
echo -e "\n${GREEN}[INFO] Iniciando TalentScan...${NC}\n"
python talent_scan.py "$@"
