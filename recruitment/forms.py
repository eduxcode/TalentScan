from django import forms
from .models import JobPosition, Criteria

class JobForm(forms.ModelForm):
    class Meta:
        model = JobPosition
        fields = ['title', 'description', 'active']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'mt-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md text-gray-900 bg-white'
            }),
            'description': forms.Textarea(attrs={
                'class': 'mt-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md text-gray-900 bg-white',
                'rows': 4
            }),
            'active': forms.CheckboxInput(attrs={
                'class': 'focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300 rounded'
            })
        }

class CriteriaForm(forms.ModelForm):
    class Meta:
        model = Criteria
        fields = ['name', 'type', 'description', 'weight']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'mt-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md text-gray-900 bg-white',
                'placeholder': 'Ex: Python'
            }),
            'type': forms.Select(attrs={
                'class': 'mt-1 block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm text-gray-900'
            }),
            'description': forms.Textarea(attrs={
                'class': 'mt-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md text-gray-900 bg-white',
                'rows': 2,
                'placeholder': 'O que a IA deve avaliar?'
            }),
            'weight': forms.Select(attrs={
                'class': 'mt-1 block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm text-gray-900'
            })
        }
