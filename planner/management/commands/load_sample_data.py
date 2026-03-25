import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from planner.models import Subject, Topic, Exam, StudyPlan
from django.utils import timezone
from planner.timetable import generate_study_plan

class Command(BaseCommand):
    help = 'Pre-populates the database with professional sample data for a student project demo'

    def handle(self, *args, **kwargs):
        self.stdout.write("🚀 Starting sample data injection...")

        # 1. Get or create a demo user
        user, created = User.objects.get_or_create(username='student')
        if created:
            user.set_password('student123')
            user.save()
            self.stdout.write(self.style.SUCCESS(f"✅ Created user 'student' with password 'student123'"))
        else:
            self.stdout.write(f"ℹ️ Using existing user 'student'")

        # 2. Clear existing data for this user to avoid duplicates
        Subject.objects.filter(user=user).delete()
        Exam.objects.filter(user=user).delete()
        StudyPlan.objects.filter(user=user).delete()

        # 3. Create Sample Subjects
        cs = Subject.objects.create(user=user, name="Computer Science", description="Core concepts of algorithms and databases.")
        math = Subject.objects.create(user=user, name="Mathematics", description="Calculus and Linear Algebra syllabus.")
        physics = Subject.objects.create(user=user, name="Physics", description="Quantum Mechanics and Electromagnetism.")

        self.stdout.write("📚 Created 3 subjects: Computer Science, Mathematics, Physics")

        # 4. Create Topics for Computer Science
        Topic.objects.create(subject=cs, name="Data Structures", difficulty='hard', estimated_hours=10)
        Topic.objects.create(subject=cs, name="Big-O Notation", difficulty='medium', estimated_hours=4)
        Topic.objects.create(subject=cs, name="SQL Queries", difficulty='easy', estimated_hours=3)
        Topic.objects.create(subject=cs, name="Django Fundamentals", difficulty='medium', estimated_hours=8)

        # 5. Create Topics for Mathematics
        Topic.objects.create(subject=math, name="Integrals & Derivatives", difficulty='hard', estimated_hours=15)
        Topic.objects.create(subject=math, name="Matrix Multiplication", difficulty='easy', estimated_hours=5)
        Topic.objects.create(subject=math, name="Probability Theory", difficulty='medium', estimated_hours=7)

        # 6. Create Topics for Physics
        Topic.objects.create(subject=physics, name="Schrodinger Equation", difficulty='hard', estimated_hours=20)
        Topic.objects.create(subject=physics, name="Gauss's Law", difficulty='medium', estimated_hours=6)
        Topic.objects.create(subject=physics, name="Newtonian Mechanics", difficulty='easy', estimated_hours=4)

        self.stdout.write("📝 Created 10 syllabus topics with varying difficulties")

        # 7. Create Exams
        today = timezone.now().date()
        Exam.objects.create(user=user, subject=physics, exam_date=today + datetime.timedelta(days=4), notes="Bring calculator!")
        Exam.objects.create(user=user, subject=cs, exam_date=today + datetime.timedelta(days=10), notes="Focused on backend logic.")
        Exam.objects.create(user=user, subject=math, exam_date=today + datetime.timedelta(days=15))

        self.stdout.write("🎯 Created 3 exam dates (Physics is most urgent!)")

        # 8. Generate the AI Timetable
        count = generate_study_plan(user)
        self.stdout.write(self.style.SUCCESS(f"📅 AI Timetable generated: {count} sessions added to the calendar"))

        self.stdout.write(self.style.SUCCESS("\n✨ ALL DONE! Your project now looks professionally populated."))
        self.stdout.write("Login URL: /login/")
        self.stdout.write("Credentials: student / student123")
