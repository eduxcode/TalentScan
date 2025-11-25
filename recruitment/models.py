from django.db import models
from django.utils import timezone

class JobPosition(models.Model):
    """Vaga em aberto"""
    title = models.CharField("Título", max_length=200)
    description = models.TextField("Descrição")
    created_at = models.DateTimeField("Criado em", default=timezone.now)
    active = models.BooleanField("Ativa", default=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Vaga"
        verbose_name_plural = "Vagas"
        ordering = ['-created_at']

class Criteria(models.Model):
    """Critério de avaliação para uma vaga"""
    CRITERIA_TYPES = [
        ('required', 'Obrigatório'),
        ('desired', 'Desejável'),
    ]

    job = models.ForeignKey(JobPosition, on_delete=models.CASCADE, related_name='criteria')
    name = models.CharField("Nome", max_length=100)
    description = models.TextField("Descrição", help_text="O que a IA deve procurar exatamente")
    weight = models.IntegerField("Peso", default=1, choices=[(i, str(i)) for i in range(1, 6)])
    type = models.CharField("Tipo", max_length=10, choices=CRITERIA_TYPES, default='desired')

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"

    class Meta:
        verbose_name = "Critério"
        verbose_name_plural = "Critérios"

class Candidate(models.Model):
    """Candidato aplicado a uma vaga"""
    job = models.ForeignKey(JobPosition, on_delete=models.CASCADE, related_name='candidates')
    name = models.CharField("Nome", max_length=200, blank=True)
    email = models.EmailField("E-mail", blank=True, null=True)
    phone = models.CharField("Telefone", max_length=50, blank=True, null=True)
    cv_file = models.FileField("Arquivo CV", upload_to='uploads/cvs/%Y/%m/')
    text_content = models.TextField("Conteúdo Extraído", blank=True)
    created_at = models.DateTimeField("Enviado em", default=timezone.now)

    def __str__(self):
        return self.name or f"Candidato {self.id}"

    class Meta:
        verbose_name = "Candidato"
        verbose_name_plural = "Candidatos"
        ordering = ['-created_at']

class Analysis(models.Model):
    """Resultado da análise da IA"""
    candidate = models.OneToOneField(Candidate, on_delete=models.CASCADE, related_name='analysis')
    total_score = models.FloatField("Pontuação Total", default=0.0)
    summary = models.TextField("Resumo das Qualidades")
    data_json = models.JSONField("Dados Detalhados", default=dict)
    processed_at = models.DateTimeField("Processado em", default=timezone.now)

    def __str__(self):
        return f"Análise de {self.candidate}"

    class Meta:
        verbose_name = "Análise"
        verbose_name_plural = "Análises"
        ordering = ['-total_score']
