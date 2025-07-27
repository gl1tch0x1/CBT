from django.contrib import admin
from .models import Question, Choice, Exam, Answer


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question', 'subject', 'class_group', 'author')
    list_filter = ('subject', 'class_group', 'author')
    search_fields = ('question',)
    inlines = [ChoiceInline]


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'class_group', 'exam_type', 'duration', 'published', 'created')
    list_filter = ('subject', 'class_group', 'exam_type', 'published', 'session', 'term')
    search_fields = ('title', 'description')
    filter_horizontal = ('questions',)


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('user', 'exam', 'score', 'percent', 'is_complete', 'time_started')
    list_filter = ('exam', 'is_complete')
    search_fields = ('user__username', 'exam__title')
    readonly_fields = ('score', 'percent')
