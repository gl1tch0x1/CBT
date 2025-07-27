from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.generic import ListView, View
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.urls import reverse_lazy

from .forms import (
    AcademicSessionForm,
    AcademicTermForm,
    StaffCreateForm,
    StaffUpdateForm,
    StudentClassForm,
    SubjectForm,
    UserCreateForm,
    UserUpdateForm,
)
from .models import AcademicSession, AcademicTerm, StudentClass, Subject, User
from apps.exam.models import Exam


class OnlyAdminMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Helper mixin to restrict view access to admin only"""
    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect('login')
        else:
            return render(self.request, 'error/403.html', status=403)


class StaffAndAdminMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Helper mixin to restrict view access to admin and staff only"""
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect('login')
        else:
            return render(self.request, 'error/403.html', status=403)


class DashboardView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user = self.request.user
        query = Exam.objects.select_related(
            "class_group", "session", "term", "subject", "author"
        )

        if user.is_superuser:
            return self.admin_page(query)
        elif user.is_staff:
            return self.staff_page(query)
        return self.student_page(query)

    def admin_page(self, query):
        paginator = Paginator(query, 20)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        context = {"exams": page_obj}
        return render(self.request, "admin_dashboard.html", context)

    def staff_page(self, query):
        paginator = Paginator(query.filter(author=self.request.user), 20)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        context = {"exams": page_obj}
        return render(self.request, "admin_dashboard.html", context)

    def student_page(self, query):
        exams = query.filter(
            class_group=self.request.user.student_class,
            published=True
        )
        context = {"exams": exams}
        return render(self.request, "dashboard.html", context)


class StudentListView(OnlyAdminMixin, ListView):
    """Student Listview"""
    queryset = User.objects.filter(is_staff=False, is_superuser=False).order_by('first_name', 'last_name', 'username')
    template_name = "core/student_list.html"
    context_object_name = "students"
    paginate_by = 20


class StudentCreateView(OnlyAdminMixin, CreateView):
    model = User
    form_class = UserCreateForm
    template_name = "modal_create.html"
    success_url = reverse_lazy("student_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Add new student"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Student created successfully.")
        return super().form_valid(form)


class StudentUpdateView(OnlyAdminMixin, SuccessMessageMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = "modal_create.html"
    success_message = "Student successfully updated."
    success_url = reverse_lazy("student_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Update student"
        return context


class UserDeleteView(OnlyAdminMixin, DeleteView):
    model = User
    template_name = "delete.html"
    success_url = reverse_lazy("student_list")

    def form_valid(self, form):
        messages.success(self.request, "User deleted successfully.")
        return super().form_valid(form)


class StaffListView(OnlyAdminMixin, ListView):
    queryset = User.objects.filter(is_staff=True, is_superuser=False).order_by('first_name', 'last_name', 'username')
    template_name = "core/staff_list.html"
    context_object_name = "staff_members"
    paginate_by = 20


class StaffCreateView(OnlyAdminMixin, CreateView):
    model = User
    form_class = StaffCreateForm
    template_name = "modal_create.html"
    success_url = reverse_lazy("staff_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Add new staff"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Staff member created successfully.")
        return super().form_valid(form)


class StaffUpdateView(OnlyAdminMixin, SuccessMessageMixin, UpdateView):
    model = User
    form_class = StaffUpdateForm
    template_name = "modal_create.html"
    success_message = "Staff member successfully updated."
    success_url = reverse_lazy("staff_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Update staff"
        return context


class TermSessionView(OnlyAdminMixin, View):
    template_name = "core/term_session_list.html"

    def get(self, request):
        context = {
            "terms": AcademicTerm.objects.all(),
            "sessions": AcademicSession.objects.all(),
            "subjects": Subject.objects.all(),
            "classes": StudentClass.objects.all(),
        }
        return render(request, self.template_name, context)


class AcademicTermCreateView(OnlyAdminMixin, CreateView):
    model = AcademicTerm
    form_class = AcademicTermForm
    template_name = "modal_create.html"
    success_url = reverse_lazy("term_session")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Add new Term"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Term created successfully.")
        return super().form_valid(form)


class TermUpdateView(OnlyAdminMixin, SuccessMessageMixin, UpdateView):
    model = AcademicTerm
    form_class = AcademicTermForm
    template_name = "modal_create.html"
    success_message = "Term successfully updated."
    success_url = reverse_lazy("term_session")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Update Term"
        return context


class AcademicTermDeleteView(OnlyAdminMixin, SuccessMessageMixin, DeleteView):
    model = AcademicTerm
    template_name = "modal_delete.html"
    success_url = reverse_lazy("term_session")
    success_message = "Term successfully deleted."

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super().form_valid(form)


class AcademicSessionCreateView(OnlyAdminMixin, CreateView):
    model = AcademicSession
    form_class = AcademicSessionForm
    template_name = "modal_create.html"
    success_url = reverse_lazy("term_session")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Add new session"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Session created successfully.")
        return super().form_valid(form)


class AcademicSessionDeleteView(OnlyAdminMixin, SuccessMessageMixin, DeleteView):
    model = AcademicSession
    template_name = "modal_delete.html"
    success_url = reverse_lazy("term_session")
    success_message = "Session successfully deleted."

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super().form_valid(form)


class SessionUpdateView(OnlyAdminMixin, SuccessMessageMixin, UpdateView):
    model = AcademicSession
    form_class = AcademicSessionForm
    template_name = "modal_create.html"
    success_message = "Session successfully updated."
    success_url = reverse_lazy("term_session")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Update Session"
        return context


class SubjectCreateView(OnlyAdminMixin, CreateView):
    model = Subject
    form_class = SubjectForm
    template_name = "modal_create.html"
    success_url = reverse_lazy("term_session")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Add new subject"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Subject created successfully.")
        return super().form_valid(form)


class SubjectDeleteView(OnlyAdminMixin, SuccessMessageMixin, DeleteView):
    model = Subject
    template_name = "modal_delete.html"
    success_url = reverse_lazy("term_session")
    success_message = "Subject successfully deleted."

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super().form_valid(form)


class SubjectUpdateView(OnlyAdminMixin, SuccessMessageMixin, UpdateView):
    model = Subject
    form_class = SubjectForm
    template_name = "modal_create.html"
    success_message = "Subject successfully updated."
    success_url = reverse_lazy("term_session")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Update subject"
        return context


class ClassCreateView(OnlyAdminMixin, CreateView):
    model = StudentClass
    form_class = StudentClassForm
    template_name = "modal_create.html"
    success_url = reverse_lazy("term_session")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Add new class"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Class created successfully.")
        return super().form_valid(form)


class ClassDeleteView(OnlyAdminMixin, SuccessMessageMixin, DeleteView):
    model = StudentClass
    template_name = "modal_delete.html"
    success_url = reverse_lazy("term_session")
    success_message = "Class successfully deleted."

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super().form_valid(form)


class ClassUpdateView(OnlyAdminMixin, SuccessMessageMixin, UpdateView):
    model = StudentClass
    form_class = StudentClassForm
    template_name = "modal_create.html"
    success_message = "Class successfully updated."
    success_url = reverse_lazy("term_session")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Update class"
        return context


# Error handling views
def error_404(request, exception):
    return render(request, 'error/404.html', status=404)


def error_500(request):
    return render(request, 'error/500.html', status=500)


def error_503(request):
    return render(request, 'error/503.html', status=503)


def error_401(request, exception=None):
    return render(request, 'error/401.html', status=401)


def error_403(request, exception=None):
    return render(request, 'error/403.html', status=403)
