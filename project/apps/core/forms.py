from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, Subject, StudentClass, AcademicTerm, AcademicSession


class ResponsiveForm:
    """Mixin to add Bootstrap classes to form fields"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.widgets.Select):
                field.widget.attrs['class'] = 'form-select'
            elif isinstance(field.widget, forms.widgets.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
            elif isinstance(field.widget, forms.widgets.Textarea):
                field.widget.attrs['class'] = 'form-control'
                field.widget.attrs['rows'] = 4
            else:
                field.widget.attrs['class'] = 'form-control'


class UserCreateForm(UserCreationForm, ResponsiveForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'gender', 'student_class', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True


class UserUpdateForm(UserChangeForm, ResponsiveForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'gender', 'student_class', 'is_active')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove the password field from the form
        if 'password' in self.fields:
            del self.fields['password']


class StaffCreateForm(UserCreationForm, ResponsiveForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'gender', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = True
        if commit:
            user.save()
        return user


class StaffUpdateForm(UserChangeForm, ResponsiveForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'gender', 'is_active')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove the password field from the form
        if 'password' in self.fields:
            del self.fields['password']


class SubjectForm(forms.ModelForm, ResponsiveForm):
    class Meta:
        model = Subject
        fields = ['name']


class StudentClassForm(forms.ModelForm, ResponsiveForm):
    class Meta:
        model = StudentClass
        fields = ['name']


class AcademicTermForm(forms.ModelForm, ResponsiveForm):
    class Meta:
        model = AcademicTerm
        fields = ['name']


class AcademicSessionForm(forms.ModelForm, ResponsiveForm):
    class Meta:
        model = AcademicSession
        fields = ['name']
