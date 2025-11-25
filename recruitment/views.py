
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, DeleteView
from django.urls import reverse_lazy
from .models import JobPosition, Criteria, Candidate, Analysis
from .services.file_parser import FileParser
from .services.ai_handler import AIHandler
from .forms import JobForm, CriteriaForm
from django.forms import inlineformset_factory

class DashboardView(ListView):
    model = JobPosition
    template_name = 'recruitment/dashboard.html'
    context_object_name = 'jobs'
    ordering = ['-created_at']

class JobCreateView(CreateView):
    model = JobPosition
    form_class = JobForm
    template_name = 'recruitment/job_form.html'
    success_url = reverse_lazy('dashboard')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        CriteriaFormSet = inlineformset_factory(JobPosition, Criteria, form=CriteriaForm, extra=1, can_delete=True)
        if self.request.POST:
            data['criteria_formset'] = CriteriaFormSet(self.request.POST)
        else:
            data['criteria_formset'] = CriteriaFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        criteria_formset = context['criteria_formset']
        if criteria_formset.is_valid():
            self.object = form.save()
            criteria_formset.instance = self.object
            criteria_formset.save()
            messages.success(self.request, 'Vaga criada com sucesso!')
            return redirect(self.success_url)
        else:
            return self.render_to_response(self.get_context_data(form=form))

class JobDetailView(DetailView):
    model = JobPosition
    template_name = 'recruitment/job_detail.html'
    context_object_name = 'job'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['candidates'] = self.object.candidates.select_related('analysis').order_by('-analysis__total_score')
        return context

class JobDeleteView(DeleteView):
    model = JobPosition
    template_name = 'recruitment/job_confirm_delete.html'
    success_url = reverse_lazy('dashboard')

def upload_candidates(request, job_id):
    job = get_object_or_404(JobPosition, id=job_id)
    if request.method == 'POST':
        files = request.FILES.getlist('cv_files')
        if not files:
            messages.error(request, 'Nenhum arquivo enviado.')
            return redirect('job_detail', pk=job.id)

        parser = FileParser()
        ai_handler = AIHandler()
        criteria_list = list(job.criteria.all())

        processed_count = 0
        for file in files:
            try:
                # Create Candidate
                candidate = Candidate.objects.create(
                    job=job,
                    name=file.name, # Temporary name
                    cv_file=file
                )
                
                # Extract Text
                text = parser.extract_text(candidate.cv_file.path)
                candidate.text_content = text
                candidate.save()

                # Analyze
                analysis_result = ai_handler.analyze_candidate(text, criteria_list)
                
                if "error" in analysis_result:
                    messages.warning(request, f"Erro ao analisar {file.name}: {analysis_result['error']}")
                    continue

                # Calculate Score
                total_score = ai_handler.calculate_total_score(analysis_result, criteria_list)

                # Save Analysis
                Analysis.objects.create(
                    candidate=candidate,
                    total_score=total_score,
                    summary=analysis_result.get('summary', ''),
                    data_json=analysis_result.get('scores', {})
                )
                
                processed_count += 1
            except Exception as e:
                messages.error(request, f"Erro ao processar {file.name}: {str(e)}")

        messages.success(request, f'{processed_count} currículos processados com sucesso!')
        return redirect('job_detail', pk=job.id)

from django.http import HttpResponse
from .services.report_generator import ReportGenerator

def export_job_report(request, job_id):
    wb = ReportGenerator.generate_excel(job_id)
    if not wb:
        messages.error(request, "Erro ao gerar relatório.")
        return redirect('dashboard')
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=relatorio_vaga_{job_id}.xlsx'
    wb.save(response)
    return response
    
    return redirect('job_detail', pk=job.id)

def toggle_job_status(request, pk):
    job = get_object_or_404(JobPosition, pk=pk)
    job.active = not job.active
    job.save()
    status = "ativada" if job.active else "desativada"
    messages.success(request, f'Vaga "{job.title}" {status} com sucesso!')
    return redirect('dashboard')
