"""
Tests for anti-cheating functionality in the Django exam system
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from apps.core.models import Subject, StudentClass, AcademicSession, AcademicTerm
from .models import Exam, Question, Choice, Answer

User = get_user_model()


class AntiCheatTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Create academic data
        self.subject = Subject.objects.create(name='Mathematics')
        self.student_class = StudentClass.objects.create(name='Grade 10')
        self.session = AcademicSession.objects.create(name='2024/2025')
        self.term = AcademicTerm.objects.create(name='First Term')
        
        # Assign user to class
        self.user.student_class = self.student_class
        self.user.save()
        
        # Create exam
        self.exam = Exam.objects.create(
            title='Test Exam',
            class_group=self.student_class,
            session=self.session,
            term=self.term,
            subject=self.subject,
            exam_type='exam',
            duration=60,  # 60 minutes
            author=self.user,
            description='Test exam for anti-cheating'
        )
        
        # Create test question
        self.question = Question.objects.create(
            subject=self.subject,
            class_group=self.student_class,
            question='What is 2 + 2?',
            author=self.user
        )
        
        # Create choices
        self.choice1 = Choice.objects.create(
            question=self.question,
            body='3',
            is_correct=False
        )
        self.choice2 = Choice.objects.create(
            question=self.question,
            body='4',
            is_correct=True
        )
        self.choice3 = Choice.objects.create(
            question=self.question,
            body='5',
            is_correct=False
        )
        
        # Add question to exam
        self.exam.questions.add(self.question)
        
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')

    def test_pre_exam_warning_display(self):
        """Test that pre-exam warning is displayed for new exam attempts"""
        response = self.client.get(reverse('take', args=[self.exam.id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ANTI-CHEATING WARNING')
        self.assertContains(response, 'Start Exam')
        self.assertContains(response, 'acknowledgment-checkbox')

    def test_exam_start_flow(self):
        """Test that exam starts properly after clicking Start Exam"""
        # First request should show pre-exam warning
        response = self.client.get(reverse('take', args=[self.exam.id]))
        self.assertContains(response, 'Start Exam')
        
        # Start the exam
        response = self.client.post(reverse('take', args=[self.exam.id]), {
            'start_exam': 'true'
        })
        
        # Should redirect back to take exam page
        self.assertEqual(response.status_code, 302)
        
        # Check that answer record was created and started
        answer = Answer.objects.get(exam=self.exam, user=self.user)
        self.assertEqual(answer.status, 'in_progress')
        self.assertIsNotNone(answer.time_started)

    def test_exam_in_progress_display(self):
        """Test that exam questions are displayed when exam is in progress"""
        # Start the exam first
        self.client.post(reverse('take', args=[self.exam.id]), {
            'start_exam': 'true'
        })
        
        # Now get the exam page
        response = self.client.get(reverse('take', args=[self.exam.id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'What is 2 + 2?')
        self.assertContains(response, 'anti-cheating.js')
        self.assertContains(response, 'Submit Exam')

    def test_exam_termination(self):
        """Test exam termination functionality"""
        # Start the exam
        self.client.post(reverse('take', args=[self.exam.id]), {
            'start_exam': 'true'
        })
        
        # Terminate the exam
        response = self.client.post(reverse('take', args=[self.exam.id]), {
            'terminate_exam': 'true',
            'termination_reason': 'Test termination'
        })
        
        # Should redirect to score detail
        self.assertEqual(response.status_code, 302)
        
        # Check that answer record was terminated
        answer = Answer.objects.get(exam=self.exam, user=self.user)
        self.assertEqual(answer.status, 'terminated')
        self.assertEqual(answer.termination_reason, 'Test termination')
        self.assertTrue(answer.is_complete)

    def test_terminated_exam_access(self):
        """Test that terminated exams cannot be accessed"""
        # Create terminated answer
        answer = Answer.objects.create(
            exam=self.exam,
            user=self.user,
            status='terminated',
            termination_reason='Previous violation',
            is_complete=True,
            time_started=timezone.now(),
            time_completed=timezone.now()
        )
        
        # Try to access exam
        response = self.client.get(reverse('take', args=[self.exam.id]))
        
        # Should redirect to score detail
        self.assertEqual(response.status_code, 302)

    def test_completed_exam_access(self):
        """Test that completed exams cannot be retaken"""
        # Create completed answer
        answer = Answer.objects.create(
            exam=self.exam,
            user=self.user,
            status='completed',
            is_complete=True,
            time_started=timezone.now(),
            time_completed=timezone.now()
        )
        
        # Try to access exam
        response = self.client.get(reverse('take', args=[self.exam.id]))
        
        # Should redirect to score detail
        self.assertEqual(response.status_code, 302)

    def test_exam_submission(self):
        """Test normal exam submission"""
        # Start the exam
        self.client.post(reverse('take', args=[self.exam.id]), {
            'start_exam': 'true'
        })
        
        # Submit the exam with answers
        response = self.client.post(reverse('take', args=[self.exam.id]), {
            'submit_exam': 'true',
            str(self.question.id): str(self.choice2.id)  # Correct answer
        })
        
        # Should redirect to score detail
        self.assertEqual(response.status_code, 302)
        
        # Check that answer was recorded correctly
        answer = Answer.objects.get(exam=self.exam, user=self.user)
        self.assertEqual(answer.status, 'completed')
        self.assertTrue(answer.is_complete)
        self.assertIn(str(self.question.id), answer.choices)

    def test_ajax_termination_endpoint(self):
        """Test AJAX termination endpoint"""
        # Start the exam
        self.client.post(reverse('take', args=[self.exam.id]), {
            'start_exam': 'true'
        })
        
        # Call AJAX termination endpoint
        response = self.client.post(reverse('terminate-exam', args=[self.exam.id]), {
            'reason': 'AJAX test termination'
        })
        
        self.assertEqual(response.status_code, 200)
        
        # Check response content
        data = response.json()
        self.assertTrue(data['success'])
        
        # Check that answer was terminated
        answer = Answer.objects.get(exam=self.exam, user=self.user)
        self.assertEqual(answer.status, 'terminated')
        self.assertEqual(answer.termination_reason, 'AJAX test termination')

    def test_answer_model_status_choices(self):
        """Test that Answer model has correct status choices"""
        answer = Answer.objects.create(
            exam=self.exam,
            user=self.user
        )
        
        # Test default status
        self.assertEqual(answer.status, 'not_started')
        
        # Test status changes
        answer.status = 'in_progress'
        answer.save()
        self.assertEqual(answer.status, 'in_progress')
        
        answer.status = 'completed'
        answer.save()
        self.assertEqual(answer.status, 'completed')
        
        answer.status = 'terminated'
        answer.termination_reason = 'Test reason'
        answer.save()
        self.assertEqual(answer.status, 'terminated')
        self.assertEqual(answer.termination_reason, 'Test reason')


class AntiCheatJavaScriptTestCase(TestCase):
    """
    Test cases for JavaScript anti-cheating functionality
    Note: These would typically be run with Selenium for full browser testing
    """
    
    def test_static_file_exists(self):
        """Test that anti-cheating JavaScript file exists"""
        import os
        from django.conf import settings
        js_path = os.path.join(settings.BASE_DIR, 'static', 'js', 'anti-cheating.js')
        self.assertTrue(os.path.exists(js_path), f"Anti-cheating JavaScript file should exist at {js_path}")

    def test_template_includes_anti_cheat_script(self):
        """Test that exam template includes anti-cheating script"""
        import os
        from django.conf import settings
        template_path = os.path.join(settings.BASE_DIR, 'templates', 'exam', 'take.html')
        with open(template_path, 'r') as f:
            content = f.read()
            self.assertIn('anti-cheating.js', content)
            self.assertIn('AntiCheatMonitor', content)
