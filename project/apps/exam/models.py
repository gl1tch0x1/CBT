from datetime import timedelta
from django.conf import settings
from django.db import models
from django.urls import reverse
from apps.core.models import (
    AcademicSession,
    AcademicTerm,
    StudentClass,
    Subject,
    User,
)


class Question(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    class_group = models.ForeignKey(StudentClass, on_delete=models.CASCADE)
    question = models.TextField()
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.question[:50]


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    body = models.TextField()
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.body[:30]


class Exam(models.Model):
    EXAM_TYPE_CHOICES = [
        ("ca2", "CA 2"),
        ("exam", "Exam"),
    ]

    title = models.CharField(max_length=200)
    class_group = models.ForeignKey(StudentClass, on_delete=models.CASCADE)
    session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE)
    term = models.ForeignKey(AcademicTerm, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    exam_type = models.CharField(max_length=100, choices=EXAM_TYPE_CHOICES)
    duration = models.IntegerField(help_text="Number of minutes.")
    choices_per_question = models.IntegerField(
        help_text="Number of choices per question.", default=4
    )
    number_of_questions = models.IntegerField(default=10)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
    )
    published = models.BooleanField(default=True)
    show_feedback = models.BooleanField(default=True)
    show_result = models.BooleanField(default=True)
    show_on_report = models.BooleanField(default=True)
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    questions = models.ManyToManyField(Question, blank=True)

    class Meta:
        ordering = ["-published", "-created"]

    def __str__(self):
        return f"{self.title}"

    def get_absolute_url(self):
        return reverse("exam-detail", args=(self.id,))

    @property
    def get_duration(self):
        a = timedelta(minutes=self.duration)
        return str(a)

    @property
    def question_count(self):
        return self.questions.count()


class Answer(models.Model):
    EXAM_STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('terminated', 'Terminated'),
    ]

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
    )
    time_created = models.DateTimeField(auto_now_add=True)  # When answer record was created
    time_started = models.DateTimeField(null=True, blank=True)  # When exam actually started
    time_completed = models.DateTimeField(null=True, blank=True)
    is_complete = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=EXAM_STATUS_CHOICES, default='not_started')
    termination_reason = models.TextField(blank=True, null=True)  # Reason for termination if applicable
    choices = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"Score for {self.user} in {self.exam}"

    @property
    def score(self):
        total = 0
        for q, v in self.choices.items():
            if v[1] == True:
                total += 1
        return total

    @property
    def total_questions(self):
        return self.exam.questions.count()

    def percent(self):
        if self.total_questions > 0:
            return round((self.score / self.total_questions) * 100, 1)
        return 0
