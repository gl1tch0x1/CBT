from django import forms
from django.forms.models import BaseInlineFormSet
from django.utils.translation import gettext_lazy as _
from apps.core.forms import ResponsiveForm
from .models import Choice, Exam, Question


class ExamForm(forms.ModelForm, ResponsiveForm):
    class Meta:
        model = Exam
        exclude = ("author", "questions")
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class QuestionForm(forms.ModelForm, ResponsiveForm):
    class Meta:
        model = Question
        exclude = ("author",)
        widgets = {
            'question': forms.Textarea(attrs={'rows': 4}),
        }


class QuestionChoiceForm(forms.ModelForm, ResponsiveForm):
    class Meta:
        model = Choice
        exclude = ("question",)
        widgets = {
            'body': forms.Textarea(attrs={'rows': 2}),
        }


# Formset for creating multiple choices for a question
QuestionChoiceFormset = forms.modelformset_factory(
    Choice, 
    form=QuestionChoiceForm, 
    extra=4, 
    max_num=5,
    can_delete=True
)


# Inline formset for updating question choices
QuestionUpdateChoiceFormset = forms.inlineformset_factory(
    Question,
    Choice,
    exclude=("question",),
    can_delete=True,
    extra=0,
    widgets={
        "body": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
    },
)
