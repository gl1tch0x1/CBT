from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.core.models import Subject, StudentClass, AcademicTerm, AcademicSession
from apps.exam.models import Question, Choice, Exam

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate the database with sample data for testing'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating sample data...'))

        # Create Academic Sessions
        session, created = AcademicSession.objects.get_or_create(name="2024/2025")
        if created:
            self.stdout.write(f'Created session: {session.name}')

        # Create Academic Terms
        terms_data = ["First Term", "Second Term", "Third Term"]
        for term_name in terms_data:
            term, created = AcademicTerm.objects.get_or_create(name=term_name)
            if created:
                self.stdout.write(f'Created term: {term.name}')

        # Create Subjects
        subjects_data = ["Mathematics", "English", "Science", "History", "Geography"]
        for subject_name in subjects_data:
            subject, created = Subject.objects.get_or_create(name=subject_name)
            if created:
                self.stdout.write(f'Created subject: {subject.name}')

        # Create Student Classes
        classes_data = ["Grade 10", "Grade 11", "Grade 12"]
        for class_name in classes_data:
            student_class, created = StudentClass.objects.get_or_create(name=class_name)
            if created:
                self.stdout.write(f'Created class: {student_class.name}')

        # Create Staff User
        if not User.objects.filter(username='teacher').exists():
            teacher = User.objects.create_user(
                username='teacher',
                email='teacher@example.com',
                password='teacher123',
                first_name='John',
                last_name='Teacher',
                is_staff=True
            )
            self.stdout.write(f'Created staff user: {teacher.username}')

        # Create Student Users
        grade_10 = StudentClass.objects.get(name="Grade 10")
        student_data = [
            ('student1', 'Alice', 'Johnson'),
            ('student2', 'Bob', 'Smith'),
            ('student3', 'Carol', 'Davis'),
        ]
        
        for username, first_name, last_name in student_data:
            if not User.objects.filter(username=username).exists():
                student = User.objects.create_user(
                    username=username,
                    email=f'{username}@example.com',
                    password='student123',
                    first_name=first_name,
                    last_name=last_name,
                    student_class=grade_10
                )
                self.stdout.write(f'Created student: {student.username}')

        # Create Sample Questions
        math_subject = Subject.objects.get(name="Mathematics")
        teacher_user = User.objects.get(username='teacher')
        
        # Sample Math Questions
        math_questions = [
            {
                'question': 'What is 2 + 2?',
                'choices': [
                    ('3', False),
                    ('4', True),
                    ('5', False),
                    ('6', False)
                ]
            },
            {
                'question': 'What is the square root of 16?',
                'choices': [
                    ('2', False),
                    ('3', False),
                    ('4', True),
                    ('5', False)
                ]
            },
            {
                'question': 'What is 10 × 5?',
                'choices': [
                    ('45', False),
                    ('50', True),
                    ('55', False),
                    ('60', False)
                ]
            }
        ]

        for q_data in math_questions:
            question, created = Question.objects.get_or_create(
                question=q_data['question'],
                subject=math_subject,
                class_group=grade_10,
                author=teacher_user
            )
            
            if created:
                self.stdout.write(f'Created question: {question.question[:30]}...')
                
                # Create choices for the question
                for choice_text, is_correct in q_data['choices']:
                    Choice.objects.create(
                        question=question,
                        body=choice_text,
                        is_correct=is_correct
                    )

        # Create Sample Exam
        first_term = AcademicTerm.objects.get(name="First Term")
        exam, created = Exam.objects.get_or_create(
            title="Mathematics Mid-Term Test",
            defaults={
                'class_group': grade_10,
                'session': session,
                'term': first_term,
                'subject': math_subject,
                'exam_type': 'exam',
                'duration': 30,
                'choices_per_question': 4,
                'number_of_questions': 3,
                'author': teacher_user,
                'published': True,
                'description': 'A sample mathematics exam for testing the CBT system.'
            }
        )
        
        if created:
            self.stdout.write(f'Created exam: {exam.title}')
            # Add questions to the exam
            questions = Question.objects.filter(subject=math_subject)
            exam.questions.set(questions)

        self.stdout.write(
            self.style.SUCCESS('Successfully created sample data!')
        )
        self.stdout.write('Login credentials:')
        self.stdout.write('Admin: admin / admin123')
        self.stdout.write('Teacher: teacher / teacher123')
        self.stdout.write('Student: student1 / student123')
