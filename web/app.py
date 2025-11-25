import shutil
import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, session
from werkzeug.utils import secure_filename
import logging
from dotenv import load_dotenv

# Importar lógica do TalentScan
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from talent_scan import TalentScan

# Carregar variáveis de ambiente
load_dotenv()

# Configuração de Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit

# Garantir que diretório de uploads existe
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Instância global do TalentScan (será re-instanciada por requisição se necessário, mas mantemos aqui para referência)
talent_scan_app = TalentScan()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Verificar se arquivos foram enviados
        if 'cv_files' not in request.files:
            flash('Nenhum arquivo enviado', 'error')
            return redirect(request.url)
        
        files = request.files.getlist('cv_files')
        job_description = request.form.get('job_description')
        
        if not files or files[0].filename == '':
            flash('Nenhum arquivo selecionado', 'error')
            return redirect(request.url)
            
        if not job_description:
            flash('Descrição da vaga é obrigatória', 'error')
            return redirect(request.url)

        # Limpar diretório de uploads anterior
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                logger.error(f'Erro ao deletar {file_path}: {e}')

        # Salvar arquivos
        saved_files = []
        for file in files:
            if file:
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                saved_files.append(filename)
        
        # Salvar perfil da vaga temporariamente
        profile_path = os.path.join(app.config['UPLOAD_FOLDER'], 'job_profile.txt')
        with open(profile_path, 'w', encoding='utf-8') as f:
            f.write(job_description)
            
        try:
            # Executar análise
            job_profile = talent_scan_app.load_job_profile(profile_path)
            candidates_data = talent_scan_app.process_candidates(app.config['UPLOAD_FOLDER'], job_profile)
            
            # Armazenar resultados na sessão (simplificado para demo)
            # Em produção, idealmente salvaríamos em banco de dados
            session['results'] = candidates_data
            session['job_profile'] = job_profile
            
            flash(f'Análise concluída! {len(candidates_data)} currículos processados.', 'success')
            return redirect(url_for('results'))
            
        except Exception as e:
            logger.error(f"Erro na análise: {e}")
            flash(f'Erro durante a análise: {str(e)}', 'error')
            return redirect(request.url)

    return render_template('index.html')

@app.route('/results')
def results():
    candidates = session.get('results', [])
    if not candidates:
        flash('Nenhum resultado disponível. Realize uma nova análise.', 'warning')
        return redirect(url_for('index'))
    
    return render_template('results.html', candidates=candidates)

@app.route('/export/<format>')
def export(format):
    candidates = session.get('results', [])
    job_profile = session.get('job_profile', {})
    
    if not candidates:
        flash('Sem dados para exportar', 'error')
        return redirect(url_for('index'))
        
    if format == 'excel':
        try:
            output_file = talent_scan_app.generate_report(candidates, job_profile)
            return send_file(output_file, as_attachment=True)
        except Exception as e:
            flash(f'Erro ao gerar Excel: {e}', 'error')
            return redirect(url_for('results'))
            
    elif format == 'csv':
        # Implementação rápida de CSV usando pandas
        import pandas as pd
        from io import BytesIO
        
        # Reutilizar lógica do ExcelGenerator para criar DataFrame
        df = talent_scan_app.excel_generator._create_dataframe(candidates, job_profile)
        
        output = BytesIO()
        df.to_csv(output, index=False, encoding='utf-8-sig')
        output.seek(0)
        
        return send_file(
            output,
            mimetype='text/csv',
            as_attachment=True,
            download_name='analise_curriculos.csv'
        )
        
    return redirect(url_for('results'))

if __name__ == '__main__':
    app.run(debug=True)
