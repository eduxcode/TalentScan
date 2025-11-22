# TalentScan - Instruções Rápidas

## 🚀 Início Rápido

### 1. Configuração e Execução
```bash
# Windows
run_windows.bat

# Linux/macOS
./run_linux.sh
```
O script configura tudo automaticamente na primeira execução.

### 2. Configurar API OpenAI
```bash
# Copiar arquivo de exemplo
cp config.env.example .env

# Editar arquivo .env e adicionar sua chave:
# OPENAI_API_KEY=sua_chave_api_aqui
```

### 3. Usar o Sistema

#### Opção 1: Linha de Comando
```bash
# Análise básica
python talent_scan.py -c curriculos/ -p perfil_vaga.txt

# Com arquivo de saída personalizado
python talent_scan.py -c curriculos/ -p perfil_vaga.txt -o relatorio.xlsx
```

#### Opção 2: Script de Exemplo
```bash
python exemplo_uso.py
```

## 📁 Estrutura de Arquivos

```
TalentScan/
├── talent_scan.py          # Aplicação principal
├── document_reader.py      # Leitura de PDF/DOCX
├── openai_analyzer.py      # Análise com IA
├── excel_generator.py      # Geração de relatórios
├── config.py              # Configurações
├── requirements.txt       # Dependências
├── perfil_vaga_exemplo.txt # Exemplo de perfil
├── activate_env.sh        # Script de ativação
├── setup.py              # Configuração inicial
├── exemplo_uso.py        # Exemplo de uso
├── test_talentscan.py    # Testes
└── README.md             # Documentação completa
```

## 📋 Formato do Perfil da Vaga

Crie um arquivo `.txt` com:

```
PERFIL DA VAGA - NOME DA VAGA

ATRIBUTOS REQUERIDOS:
- Atributo 1
- Atributo 2
- Atributo 3

ATRIBUTOS DESEJÁVEIS:
- Atributo desejável 1
- Atributo desejável 2
```

## 📊 Resultado

O sistema gera um arquivo Excel com:
- **Planilha "Análise de Currículos"**: Dados completos
- **Planilha "Resumo"**: Estatísticas e ranking

## 🔧 Solução de Problemas

### Erro de API Key
```
OPENAI_API_KEY não encontrada
```
**Solução**: Configure no arquivo `.env`

### Nenhum documento encontrado
```
Nenhum documento encontrado no diretório
```
**Solução**: Verifique se há arquivos PDF/DOCX no diretório

### Dependências não instaladas
```bash
# Reinstalar dependências
source venv/bin/activate
pip install -r requirements.txt
```

## 📞 Suporte

Para mais detalhes, consulte o `README.md` completo.
