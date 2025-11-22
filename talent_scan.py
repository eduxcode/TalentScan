#!/usr/bin/env python3
"""
TalentScan - Sistema de Análise de Currículos
Aplicação principal que integra todos os módulos
"""
import os
import sys
import argparse
import logging
from typing import List, Dict, Any
from pathlib import Path

# Importar módulos locais
from document_reader import DocumentReader
from openai_analyzer import OpenAIAnalyzer
from excel_generator import ExcelGenerator

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('talent_scan.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class TalentScan:
    """Classe principal da aplicação TalentScan"""
    
    def __init__(self):
        self.document_reader = DocumentReader()
        self.openai_analyzer = None
        self.excel_generator = ExcelGenerator()
        
        # Inicializar analisador OpenAI
        try:
            self.openai_analyzer = OpenAIAnalyzer()
            logger.info("Analisador OpenAI inicializado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao inicializar analisador OpenAI: {e}")
            logger.error("Certifique-se de que a variável OPENAI_API_KEY está configurada")
            sys.exit(1)
    
    def load_job_profile(self, profile_file: str) -> Dict[str, List[str]]:
        """
        Carrega o perfil da vaga de um arquivo
        
        Args:
            profile_file: Caminho para o arquivo de perfil
            
        Returns:
            Dicionário com atributos da vaga
        """
        try:
            with open(profile_file, 'r', encoding='utf-8') as f:
                profile_text = f.read()
            
            job_profile = self.openai_analyzer.parse_job_profile(profile_text)
            logger.info(f"Perfil da vaga carregado: {len(job_profile['requeridos'])} atributos requeridos, {len(job_profile['desejaveis'])} desejáveis")
            
            return job_profile
            
        except Exception as e:
            logger.error(f"Erro ao carregar perfil da vaga: {e}")
            sys.exit(1)
    
    def process_candidates(self, directory_path: str, job_profile: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """
        Processa todos os currículos em um diretório
        
        Args:
            directory_path: Caminho para o diretório com currículos
            job_profile: Perfil da vaga
            
        Returns:
            Lista com dados processados dos candidatos
        """
        logger.info(f"Processando currículos em: {directory_path}")
        
        # Ler documentos
        documents = self.document_reader.read_directory(directory_path)
        
        if not documents:
            logger.warning("Nenhum documento encontrado no diretório")
            return []
        
        logger.info(f"Encontrados {len(documents)} documentos para processar")
        
        candidates_data = []
        
        for i, doc in enumerate(documents, 1):
            logger.info(f"Analisando candidato {i}/{len(documents)}: {doc.get('arquivo', 'Desconhecido')}")
            
            try:
                # Analisar currículo
                analysis = self.openai_analyzer.analyze_cv(doc['texto'], job_profile)
                
                # Calcular pontuação total
                total_score = self.openai_analyzer.calculate_total_score(analysis, job_profile)
                
                candidate_data = {
                    'contato': doc['contato'],
                    'arquivo': doc['arquivo'],
                    'analise': analysis,
                    'pontuacao_total': total_score
                }
                
                candidates_data.append(candidate_data)
                
                logger.info(f"Candidato {i} processado - Pontuação: {total_score}")
                
            except Exception as e:
                logger.error(f"Erro ao processar candidato {i}: {e}")
                continue
        
        return candidates_data
    
    def generate_report(self, candidates_data: List[Dict[str, Any]], job_profile: Dict[str, List[str]], output_file: str = None, format: str = 'xlsx') -> str:
        """
        Gera relatório em Excel ou CSV
        
        Args:
            candidates_data: Dados dos candidatos
            job_profile: Perfil da vaga
            output_file: Nome do arquivo de saída
            format: Formato do arquivo ('xlsx' ou 'csv')
            
        Returns:
            Caminho do arquivo gerado
        """
        logger.info(f"Gerando relatório {format.upper()}...")
        
        if format.lower() == 'csv':
            return self.excel_generator.export_to_csv(candidates_data, job_profile, output_file)
        
        # Gerar relatório principal (Excel)
        excel_file = self.excel_generator.create_analysis_report(
            candidates_data, 
            job_profile, 
            output_file
        )
        
        # Adicionar planilha de resumo
        self.excel_generator.create_summary_sheet(candidates_data, job_profile)
        
        # Salvar novamente com a planilha de resumo
        self.excel_generator.workbook.save(excel_file)
        
        logger.info(f"Relatório gerado com sucesso: {excel_file}")
        return excel_file
    
    def run(self, cv_directory: str, profile_file: str, output_file: str = None, format: str = 'xlsx'):
        """
        Executa o processo completo de análise
        
        Args:
            cv_directory: Diretório com currículos
            profile_file: Arquivo com perfil da vaga
            output_file: Arquivo de saída (opcional)
            format: Formato de saída ('xlsx' ou 'csv')
        """
        logger.info("=== INICIANDO TALENTSCAN ===")
        
        try:
            # Validar inputs
            if not cv_directory or not isinstance(cv_directory, str):
                logger.error("Diretório de currículos inválido")
                sys.exit(1)
                
            if not profile_file or not isinstance(profile_file, str):
                logger.error("Arquivo de perfil inválido")
                sys.exit(1)

            # Verificar se diretório existe
            if not os.path.exists(cv_directory):
                logger.error(f"Diretório não encontrado: {cv_directory}")
                sys.exit(1)
            
            if not os.path.isdir(cv_directory):
                logger.error(f"O caminho especificado não é um diretório: {cv_directory}")
                sys.exit(1)
            
            # Verificar se arquivo de perfil existe
            if not os.path.exists(profile_file):
                logger.error(f"Arquivo de perfil não encontrado: {profile_file}")
                sys.exit(1)
                
            if not os.path.isfile(profile_file):
                logger.error(f"O caminho do perfil não é um arquivo: {profile_file}")
                sys.exit(1)
            
            # Carregar perfil da vaga
            job_profile = self.load_job_profile(profile_file)
            
            # Processar candidatos
            candidates_data = self.process_candidates(cv_directory, job_profile)
            
            if not candidates_data:
                logger.warning("Nenhum candidato foi processado com sucesso")
                return
            
            # Gerar relatório
            excel_file = self.generate_report(candidates_data, job_profile, output_file, format)
            
            # Estatísticas finais
            total_candidates = len(candidates_data)
            if total_candidates > 0:
                avg_score = sum(c.get('pontuacao_total', 0) for c in candidates_data) / total_candidates
                best_candidate = max(candidates_data, key=lambda x: x.get('pontuacao_total', 0))
                
                logger.info("=== ANÁLISE CONCLUÍDA ===")
                logger.info(f"Total de candidatos processados: {total_candidates}")
                logger.info(f"Pontuação média: {avg_score:.2f}")
                logger.info(f"Melhor candidato: {best_candidate.get('contato', {}).get('nome', 'N/A')} - {best_candidate.get('pontuacao_total', 0)} pontos")
                logger.info(f"Relatório salvo em: {excel_file}")
            else:
                logger.warning("Análise concluída, mas sem dados para estatísticas.")
            
        except KeyboardInterrupt:
            logger.info("\nOperação interrompida pelo usuário")
            sys.exit(0)
        except Exception as e:
            logger.critical(f"Erro crítico durante a execução: {e}", exc_info=True)
            sys.exit(1)

def main():
    """Função principal"""
    try:
        parser = argparse.ArgumentParser(
            description="TalentScan - Sistema de Análise de Currículos",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Exemplos de uso:
  python talent_scan.py -c curriculos/ -p perfil_vaga.txt
  python talent_scan.py -c curriculos/ -p perfil_vaga.txt -o relatorio.xlsx
  python talent_scan.py --help
            """
        )
        
        parser.add_argument(
            '-c', '--curriculos',
            required=True,
            help='Diretório contendo os currículos (PDF e DOCX)'
        )
        
        parser.add_argument(
            '-p', '--perfil',
            required=True,
            help='Arquivo de texto com o perfil da vaga'
        )
        
        parser.add_argument(
            '-o', '--output',
            help='Nome do arquivo Excel de saída (opcional)'
        )
        
        parser.add_argument(
            '-f', '--format',
            choices=['xlsx', 'csv'],
            default='xlsx',
            help='Formato do arquivo de saída (padrão: xlsx)'
        )
        
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Modo verboso (mais detalhes no log)'
        )
        
        args = parser.parse_args()
        
        # Configurar nível de log
        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        
        # Criar e executar aplicação
        app = TalentScan()
        app.run(args.curriculos, args.perfil, args.output, args.format)
        
    except Exception as e:
        print(f"Erro fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
