from django.core.management.base import BaseCommand
from django.template.loader import get_template
from django.template.exceptions import TemplateDoesNotExist
import os


class Command(BaseCommand):
    help = 'Check for missing templates'

    def handle(self, *args, **options):
        templates_to_check = [
            'base.html',
            'dashboard.html',
            'admin_dashboard.html',
            'registration/login.html',
            'registration/logged_out.html',
            'delete.html',
            'modal_create.html',
            'modal_delete.html',
            'core/student_list.html',
            'core/staff_list.html',
            'core/term_session_list.html',
            'exam/create.html',
            'exam/exam_detail.html',
            'exam/take.html',
            'exam/score_detail.html',
            'exam/scores.html',
            'exam/questionbank.html',
            'exam/question_form.html',
            'exam/myexams.html',
            'exam/add_question_from_bank.html',
            'error/401.html',
            'error/403.html',
            'error/404.html',
            'error/500.html',
            'error/503.html',
        ]

        missing_templates = []
        existing_templates = []

        for template_name in templates_to_check:
            try:
                get_template(template_name)
                existing_templates.append(template_name)
                self.stdout.write(
                    self.style.SUCCESS(f'✓ {template_name}')
                )
            except TemplateDoesNotExist:
                missing_templates.append(template_name)
                self.stdout.write(
                    self.style.ERROR(f'✗ {template_name} - MISSING')
                )

        self.stdout.write('\n' + '='*50)
        self.stdout.write(f'Total templates checked: {len(templates_to_check)}')
        self.stdout.write(
            self.style.SUCCESS(f'Existing templates: {len(existing_templates)}')
        )
        
        if missing_templates:
            self.stdout.write(
                self.style.ERROR(f'Missing templates: {len(missing_templates)}')
            )
            self.stdout.write('\nMissing templates:')
            for template in missing_templates:
                self.stdout.write(f'  - {template}')
        else:
            self.stdout.write(
                self.style.SUCCESS('All templates are present!')
            )
