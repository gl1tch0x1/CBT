from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Subject, StudentClass, AcademicTerm, AcademicSession


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'student_class')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'student_class')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('gender', 'student_class')}),
    )


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(StudentClass)
class StudentClassAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(AcademicTerm)
class AcademicTermAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(AcademicSession)
class AcademicSessionAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
