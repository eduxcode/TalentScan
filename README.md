# TalentScan 1.0 🚀

**TalentScan** é uma plataforma inteligente de recrutamento e seleção que utiliza Inteligência Artificial para analisar currículos, classificar candidatos e gerar insights valiosos para recrutadores.

Esta versão 1.0 marca a migração completa para **Django**, trazendo uma arquitetura mais robusta, interface moderna e novas funcionalidades.

---

## ✨ Novidades da Versão 1.0

### 🏢 Arquitetura & Core
- **Migração para Django 5.x**: Maior estabilidade, segurança e escalabilidade.
- **Estrutura Modular**: Código organizado em apps (`recruitment`) seguindo as melhores práticas.

### 🎯 Gestão de Vagas
- **Critérios Personalizados**: Defina critérios de avaliação com pesos específicos (1-5).
- **Status da Vaga**: Alterne entre **Ativa** e **Inativa** diretamente pelo Dashboard.
- **Exclusão Segura**: Fluxo de exclusão com página de confirmação.

### 📄 Processamento de Candidatos
- **Upload Drag & Drop**: Arraste múltiplos arquivos (PDF, DOCX, TXT) de uma vez.
- **Análise via IA**: Extração de texto e avaliação automática contra os critérios da vaga.
- **Modo Mock Inteligente**: Fallback automático para análises simuladas caso a API da OpenAI esteja indisponível ou sem créditos.
- **Modal de Detalhes**: Visualize a análise completa (pontos fortes, notas por critério) sem sair da listagem.

### 📊 Relatórios e Exportação
- **Exportação Excel Aprimorada**:
    - Aba **"Análise de Currículos"**: Dados completos dos candidatos.
    - Aba **"Resumo"**: Estatísticas gerais e médias por critério.

---

## 🛠️ Instalação e Execução

### Pré-requisitos
- Python 3.10+
- Conta na OpenAI (para análise real via IA)

### Passo a Passo

1. **Clone o repositório**
   ```bash
   git clone https://github.com/seu-usuario/talentscan.git
   cd talentscan
   ```

2. **Crie e ative o ambiente virtual**
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure as variáveis de ambiente**
   Crie um arquivo `.env` na raiz do projeto e adicione sua chave da OpenAI:
   ```env
   OPENAI_API_KEY=sua-chave-aqui
   # Opcional: DEBUG=True para desenvolvimento
   ```

5. **Execute as migrações**
   ```bash
   python manage.py migrate
   ```

6. **Inicie o servidor**
   ```bash
   python manage.py runserver
   ```

7. **Acesse**: `http://127.0.0.1:8000`

---

## 🛡️ Segurança

- **Credenciais**: Nunca commite o arquivo `.env`.
- **Debug**: Em produção, certifique-se de definir `DEBUG=False` no `.env`.

---

## 📝 Licença

Este projeto está sob a licença MIT.
