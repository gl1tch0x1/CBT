import django_filters
from django import forms
from .models import Question
from apps.core.models import Subject, StudentClass


class QuestionFilter(django_filters.FilterSet):
    subject = django_filters.ModelChoiceFilter(
        queryset=Subject.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="All Subjects"
    )
    class_group = django_filters.ModelChoiceFilter(
        queryset=StudentClass.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="All Classes"
    )
    question = django_filters.CharFilter(
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search questions...'})
    )

    class Meta:
        model = Question
        fields = ['subject', 'class_group', 'question']
