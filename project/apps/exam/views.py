from django_filters.views import FilterView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Case, IntegerField, Prefetch, Value, When
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import DetailView, ListView, View
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from apps.core.views import StaffAndAdminMixin
from . import forms
from .filters import QuestionFilter
from .models import Answer, Choice, Exam, Question


class QuestionBankListView(StaffAndAdminMixin, FilterView):
    queryset = Question.objects.select_related("subject", "class_group")
    template_name = "exam/questionbank.html"
    filterset_class = QuestionFilter
    paginate_by = 50
    context_object_name = "questions"

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            return queryset.filter(author=self.request.user)
        return queryset


class QuestionCreateView(StaffAndAdminMixin, View):
    template_name = "exam/question_form.html"
    question_form_class = forms.QuestionForm
    choice_formset_class = forms.QuestionChoiceFormset

    def get(self, request, *args, **kwargs):
        formset = self.choice_formset_class(queryset=Choice.objects.none())
        context = {
            "form": self.question_form_class(),
            "formset": formset,
            "title": "Add new question",
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        question_form = self.question_form_class(request.POST)
        choice_formset = self.choice_formset_class(
            request.POST, queryset=Choice.objects.none()
        )

        if question_form.is_valid() and choice_formset.is_valid():
            question = question_form.save(commit=False)
            question.author = request.user
            question.save()

            choices = choice_formset.save(commit=False)
            for choice in choices:
                choice.question = question
                choice.save()

            messages.success(request, "Question created successfully.")
            return redirect("questionbank")

        context = {
            "form": question_form,
            "formset": choice_formset,
            "title": "Add new question",
        }
        return render(request, self.template_name, context)


class QuestionDeleteView(StaffAndAdminMixin, SuccessMessageMixin, DeleteView):
    model = Question
    template_name = "delete.html"
    success_message = "Question successfully deleted"
    success_url = reverse_lazy("questionbank")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["item"] = context["object"]
        return context


class ExamCreateView(StaffAndAdminMixin, SuccessMessageMixin, CreateView):
    model = Exam
    form_class = forms.ExamForm
    template_name = "exam/create.html"
    success_message = "Exam successfully added."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Add new Exam"
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class ExamUpdateView(StaffAndAdminMixin, SuccessMessageMixin, UpdateView):
    model = Exam
    form_class = forms.ExamForm
    template_name = "exam/create.html"
    success_message = "Exam successfully updated."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Update Exam"
        return context


class ExamDeleteView(StaffAndAdminMixin, DeleteView):
    model = Exam
    template_name = "delete.html"
    success_url = reverse_lazy("dashboard")
    success_message = "Exam successfully deleted"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["item"] = context["object"]
        return context

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super().form_valid(form)


class ExamDetailView(LoginRequiredMixin, DetailView):
    model = Exam
    template_name = "exam/exam_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        exam = self.get_object()
        context["questions"] = exam.questions.all().prefetch_related('choice_set')
        return context


class AddQuestionView(StaffAndAdminMixin, View):
    """Add question to exam directly. This creates the question to question banks and also adds it to the exam."""
    template_name = "exam/question_form.html"
    question_form_class = forms.QuestionForm
    choice_formset_class = forms.QuestionChoiceFormset

    def get(self, request, *args, **kwargs):
        exam = self.get_exam
        formset = self.choice_formset_class(queryset=Choice.objects.none())
        formset.extra = exam.choices_per_question
        formset.max_num = exam.choices_per_question

        context = {
            "exam": exam,
            "form": self.question_form_class(),
            "formset": formset,
            "title": "Add new question",
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        exam = self.get_exam
        question_form = self.question_form_class(request.POST)
        choice_formset = self.choice_formset_class(
            request.POST, queryset=Choice.objects.none()
        )

        if question_form.is_valid() and choice_formset.is_valid():
            question = question_form.save(commit=False)
            question.author = request.user
            question.save()

            choices = choice_formset.save(commit=False)
            for choice in choices:
                choice.question = question
                choice.save()

            exam.questions.add(question)
            messages.success(request, "Question added to exam successfully.")
            return redirect(exam)

        context = {
            "exam": exam,
            "form": question_form,
            "formset": choice_formset,
            "title": "Add new question",
        }
        return render(request, self.template_name, context)

    @property
    def get_exam(self):
        return get_object_or_404(Exam, pk=self.kwargs["exam_id"])


class AddQuestionFromBankView(StaffAndAdminMixin, View):
    """Page responsible for picking question from question bank to an exam."""
    template_name = "exam/add_question_from_bank.html"

    def get(self, request, **kwargs):
        exam = get_object_or_404(Exam, pk=kwargs["exam_id"])
        existing_questions = exam.questions.values_list("id", flat=True)
        questions = Question.objects.filter(subject=exam.subject).exclude(
            id__in=existing_questions
        ).prefetch_related('choice_set')

        context = {
            "exam": exam,
            "questions": questions
        }
        return render(request, self.template_name, context)

    def post(self, request, **kwargs):
        questions = request.POST.getlist("question[]")
        exam = get_object_or_404(Exam, pk=kwargs["exam_id"])
        exam.questions.add(*questions)
        messages.success(request, "Questions successfully added.")
        return redirect(exam)


class QuestionUpdateView(StaffAndAdminMixin, View):
    form_class = forms.QuestionForm
    formset_class = forms.QuestionUpdateChoiceFormset
    template_name = "exam/question_form.html"

    def get_question(self):
        return get_object_or_404(Question, pk=self.kwargs["pk"])

    def get(self, request, *args, **kwargs):
        question = self.get_question()
        context = {
            "title": "Update Question",
            "form": self.form_class(instance=question),
            "formset": self.formset_class(
                instance=question,
                queryset=Choice.objects.filter(question=question),
            ),
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        question = self.get_question()
        form = self.form_class(request.POST, instance=question)
        formset = self.formset_class(
            request.POST,
            instance=question,
            queryset=Choice.objects.filter(question=question),
        )

        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, "Question successfully updated.")

            if kwargs.get("exam_id"):
                exam = get_object_or_404(Exam, pk=self.kwargs["exam_id"])
                return redirect(exam)
            return redirect("questionbank")

        context = {
            "title": "Update Question",
            "form": form,
            "formset": formset
        }
        return render(request, self.template_name, context)


class RemoveQuestionFromExamView(StaffAndAdminMixin, DeleteView):
    model = Question
    template_name = "delete.html"
    success_message = "Question successfully removed."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["item"] = context["object"]
        return context

    def form_valid(self, form):
        exam = get_object_or_404(Exam, pk=self.kwargs["exam_id"])
        exam.questions.remove(self.object)
        messages.success(self.request, "Question removed from exam successfully.")
        return HttpResponseRedirect(exam.get_absolute_url())


class TakeExamView(LoginRequiredMixin, View):
    template_name = "exam/take.html"

    @property
    def get_exam(self):
        return Exam.objects.prefetch_related(
            Prefetch("questions__choice_set", queryset=Choice.objects.order_by("?"))
        ).get(pk=self.kwargs["exam_id"])

    @property
    def get_score(self):
        score, created = Answer.objects.get_or_create(
            exam=self.get_exam, user=self.request.user,
        )
        return score

    def get(self, request, *args, **kwargs):
        exam = self.get_exam
        score = self.get_score

        # Check if user has already completed the exam
        if score.is_complete:
            messages.warning(request, "You have already submitted this exam.")
            return redirect("score-detail", exam.id, request.user.id)

        # Calculate expiry time
        alloted = timezone.timedelta(minutes=exam.duration)
        expiry_time = score.time_started + alloted

        # Check if exam time has expired
        if timezone.now() > expiry_time:
            score.is_complete = True
            score.time_completed = timezone.now()
            score.save()
            messages.warning(request, "Exam time has expired. Your answers have been auto-submitted.")
            return redirect("score-detail", exam.id, request.user.id)

        context = {
            "exam": exam,
            "score": score,
            "expiry_time": expiry_time,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        data = request.POST
        exam = self.get_exam
        questions = exam.questions.all()
        choices = {}

        for question in questions:
            choice = data.get(str(question.id), "")
            if choice:
                is_correct = Choice.objects.get(pk=int(choice)).is_correct
                choices[question.id] = [choice, is_correct]

        score = self.get_score
        score.time_completed = timezone.now()
        score.is_complete = True
        score.choices = choices
        score.save()

        messages.success(request, "Exam submitted successfully!")
        return redirect("score-detail", kwargs["exam_id"], request.user.id)


class ExamScoreView(LoginRequiredMixin, View):
    template_name = "exam/scores.html"

    def get(self, request, *args, **kwargs):
        exam = get_object_or_404(Exam, pk=kwargs["exam_id"])
        scores = Answer.objects.filter(exam=exam).select_related('user')

        context = {
            "exam": exam,
            "scores": scores
        }
        return render(request, self.template_name, context)


class ExamScoreDetailView(LoginRequiredMixin, View):
    template_name = "exam/score_detail.html"

    def get(self, request, *args, **kwargs):
        exam = get_object_or_404(Exam, pk=kwargs["exam_id"])
        answer = get_object_or_404(Answer, exam=exam, user_id=kwargs["uid"])

        # Get submission data
        submission = answer.choices

        # Get exam with questions and annotate with user's choices
        exam_with_questions = Exam.objects.prefetch_related(
            Prefetch(
                "questions",
                queryset=Question.objects.annotate(
                    mychoice=Case(
                        *[When(id=k, then=Value(v[0])) for k, v in submission.items()],
                        default=0,
                        output_field=IntegerField()
                    )
                ),
            ),
            "questions__choice_set",
        ).get(pk=kwargs["exam_id"])

        context = {
            "exam": exam_with_questions,
            "answer": answer,
        }
        return render(request, self.template_name, context)


class ScoreDeleteView(StaffAndAdminMixin, DeleteView):
    model = Answer
    template_name = "modal_delete.html"
    success_message = "Score successfully deleted"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["item"] = context["object"]
        return context

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("scores", kwargs={"exam_id": self.object.exam.id})


class MyExamsView(LoginRequiredMixin, View):
    template_name = "exam/myexams.html"

    def get(self, request, *args, **kwargs):
        exams = Exam.objects.filter(
            published=True,
            class_group=request.user.student_class
        ).select_related('subject', 'class_group')

        context = {"exams": exams}
        return render(request, self.template_name, context)
