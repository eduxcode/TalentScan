# TalentScan - Guia de Instalação

## 📋 Pré-requisitos

- Python 3.7 ou superior
- Chave da API OpenAI
- Sistema operacional: Linux, macOS ou Windows

## 🚀 Instalação Simplificada

### 1. Clonar/Baixar o Projeto
```bash
# Se usando git:
git clone <url-do-repositorio>
cd TalentScan
```

### 2. Executar (Windows)
Dê um duplo clique no arquivo `run_windows.bat` ou execute no terminal:
```cmd
run_windows.bat
```

### 3. Executar (Linux/macOS)
```bash
# Dar permissão de execução (primeira vez)
chmod +x run_linux.sh

# Executar
./run_linux.sh
```

O script irá automaticamente:
1. Verificar o Python
2. Criar o ambiente virtual
3. Instalar as dependências
4. Executar a aplicação

### 4. Configurar API OpenAI
Na primeira execução, o script criará o arquivo `.env`. Edite-o para adicionar sua chave:
```bash
OPENAI_API_KEY=sua_chave_api_aqui
```

## 🔧 Instalação Manual (Alternativa)

Se preferir fazer manualmente:

### 1. Criar Ambiente Virtual
```bash
python3 -m venv venv
```

### 2. Ativar Ambiente Virtual
```bash
# Linux/macOS:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### 3. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 4. Executar
```bash
python talent_scan.py --help
```

### Teste Completo
```bash
source venv/bin/activate
python test_talentscan.py
```

### Teste com Exemplo
```bash
source venv/bin/activate
python exemplo_uso.py
```

## 🚨 Solução de Problemas

### Erro: "python: comando não encontrado"
```bash
# Use python3 em vez de python
python3 --version
python3 -m venv venv
```

### Erro: "externally-managed-environment"
```bash
# Use ambiente virtual
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Erro: "No module named 'PyPDF2'"
```bash
# Reinstalar dependências
source venv/bin/activate
pip install -r requirements.txt
```

### Erro: "OPENAI_API_KEY não encontrada"
```bash
# Verificar arquivo .env
cat .env
# Deve conter: OPENAI_API_KEY=sua_chave_aqui
```

## 🔑 Obter Chave da API OpenAI

1. Acesse: https://platform.openai.com/
2. Faça login ou crie uma conta
3. Vá para "API Keys"
4. Clique em "Create new secret key"
5. Copie a chave e adicione no arquivo `.env`

## 📞 Suporte

Se encontrar problemas:

1. Verifique se seguiu todos os passos
2. Execute os testes: `python test_talentscan.py`
3. Consulte o `README.md` para mais detalhes
4. Verifique os logs em `talent_scan.log`

## ✅ Instalação Concluída

Após a instalação bem-sucedida, você pode:

1. **Usar a aplicação principal:**
   ```bash
   python talent_scan.py -c curriculos/ -p perfil_vaga.txt
   ```

2. **Executar exemplos:**
   ```bash
   python exemplo_uso.py
   ```

3. **Consultar documentação:**
   - `README.md` - Documentação completa
   - `INSTRUCOES_RAPIDAS.md` - Guia rápido
   - `RESUMO_PROJETO.md` - Resumo do projeto
