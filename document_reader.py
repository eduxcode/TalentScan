"""
Módulo para leitura de arquivos PDF e DOCX
"""
import os
import re
from typing import List, Dict, Optional
import PyPDF2
from docx import Document
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentReader:
    """Classe para leitura de documentos PDF e DOCX"""
    
    def __init__(self):
        self.supported_extensions = ['.pdf', '.docx', '.txt']
    
    def sanitize_text(self, text: str) -> str:
        """
        Remove caracteres de controle e normaliza o texto
        
        Args:
            text: Texto original
            
        Returns:
            Texto sanitizado
        """
        if not text:
            return ""
        
        # Remover caracteres nulos e outros controles não imprimíveis (exceto \n, \r, \t)
        # Mantém caracteres acentuados e pontuação
        text = "".join(char for char in text if char.isprintable() or char in ['\n', '\r', '\t'])
        return text.strip()

    def read_pdf(self, file_path: str) -> str:
        """
        Lê o conteúdo de um arquivo PDF
        
        Args:
            file_path: Caminho para o arquivo PDF
            
        Returns:
            Texto extraído do PDF
        """
        try:
            # Verificar se arquivo está vazio
            if os.path.getsize(file_path) == 0:
                logger.warning(f"Arquivo vazio: {file_path}")
                return ""

            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Verificar se PDF é válido/encriptado
                if pdf_reader.is_encrypted:
                    logger.warning(f"PDF encriptado (não suportado): {file_path}")
                    return ""
                    
                text = ""
                for page_num in range(len(pdf_reader.pages)):
                    try:
                        page = pdf_reader.pages[page_num]
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                    except Exception as e:
                        logger.warning(f"Erro ao ler página {page_num} de {file_path}: {e}")
                        continue
                
                return self.sanitize_text(text)
        except Exception as e:
            logger.error(f"Erro ao ler PDF {file_path}: {str(e)}")
            return ""
    
    def read_docx(self, file_path: str) -> str:
        """
        Lê o conteúdo de um arquivo DOCX
        
        Args:
            file_path: Caminho para o arquivo DOCX
            
        Returns:
            Texto extraído do DOCX
        """
        try:
            # Verificar se arquivo está vazio
            if os.path.getsize(file_path) == 0:
                logger.warning(f"Arquivo vazio: {file_path}")
                return ""

            doc = Document(file_path)
            text = ""
            
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return self.sanitize_text(text)
        except Exception as e:
            logger.error(f"Erro ao ler DOCX {file_path}: {str(e)}")
            return ""
    
    def read_txt(self, file_path: str) -> str:
        """
        Lê o conteúdo de um arquivo TXT
        
        Args:
            file_path: Caminho para o arquivo TXT
            
        Returns:
            Texto extraído do TXT
        """
        try:
            # Verificar se arquivo está vazio
            if os.path.getsize(file_path) == 0:
                logger.warning(f"Arquivo vazio: {file_path}")
                return ""

            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
            
            return self.sanitize_text(text)
        except Exception as e:
            logger.error(f"Erro ao ler TXT {file_path}: {str(e)}")
            return ""

    def extract_contact_info(self, text: str) -> Dict[str, Optional[str]]:
        """
        Extrai informações de contato do texto do currículo
        
        Args:
            text: Texto do currículo
            
        Returns:
            Dicionário com nome, email e telefone
        """
        contact_info = {
            'nome': None,
            'email': None,
            'telefone': None
        }
        
        if not text:
            return contact_info
        
        # Extrair email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            contact_info['email'] = email_match.group()
        
        # Extrair telefone (formato brasileiro)
        phone_pattern = r'(\(?\d{2}\)?\s?\d{4,5}-?\d{4})'
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            contact_info['telefone'] = phone_match.group()
        
        # Tentar extrair nome (primeira linha ou após "Nome:")
        lines = text.split('\n')
        for line in lines[:5]:  # Verificar as primeiras 5 linhas
            line = line.strip()
            if line and not re.search(r'[0-9@]', line) and len(line) > 3:
                # Verificar se não é um cabeçalho comum
                if not any(header in line.lower() for header in ['curriculum', 'curriculo', 'cv', 'resume']):
                    contact_info['nome'] = line
                    break
        
        return contact_info
    
    def read_document(self, file_path: str) -> Dict[str, str]:
        """
        Lê um documento e extrai informações
        
        Args:
            file_path: Caminho para o arquivo
            
        Returns:
            Dicionário com texto e informações de contato
        """
        if not os.path.exists(file_path):
            logger.error(f"Arquivo não encontrado: {file_path}")
            return {'texto': '', 'contato': {}}
        
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.pdf':
            texto = self.read_pdf(file_path)
        elif file_extension == '.docx':
            texto = self.read_docx(file_path)
        elif file_extension == '.txt':
            texto = self.read_txt(file_path)
        else:
            logger.error(f"Formato não suportado: {file_extension}")
            return {'texto': '', 'contato': {}}
        
        if not texto:
            logger.warning(f"Nenhum texto extraído de: {file_path}")
        
        contato = self.extract_contact_info(texto)
        
        return {
            'texto': texto,
            'contato': contato,
            'arquivo': os.path.basename(file_path)
        }
    
    def read_directory(self, directory_path: str) -> List[Dict[str, str]]:
        """
        Lê todos os documentos suportados em um diretório
        
        Args:
            directory_path: Caminho para o diretório
            
        Returns:
            Lista de dicionários com informações dos documentos
        """
        if not os.path.exists(directory_path):
            logger.error(f"Diretório não encontrado: {directory_path}")
            return []
            
        if not os.path.isdir(directory_path):
            logger.error(f"Caminho não é um diretório: {directory_path}")
            return []
        
        documentos = []
        
        try:
            for filename in os.listdir(directory_path):
                file_path = os.path.join(directory_path, filename)
                
                if os.path.isfile(file_path):
                    file_extension = os.path.splitext(filename)[1].lower()
                    
                    if file_extension in self.supported_extensions:
                        logger.info(f"Processando arquivo: {filename}")
                        doc_info = self.read_document(file_path)
                        if doc_info['texto']: # Só adiciona se conseguiu extrair texto
                            documentos.append(doc_info)
        except Exception as e:
            logger.error(f"Erro ao ler diretório {directory_path}: {e}")
        
        return documentos
