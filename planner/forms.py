"""
AIStudyPlanner - Django Forms
================================
Forms handle user input and validation.
We use ModelForms which auto-generate fields from models.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Subject, Topic, Exam


# ─────────────────────────────────────────────────────────────
# REGISTRATION FORM — extends Django's built-in UserCreationForm
# ─────────────────────────────────────────────────────────────
class RegisterForm(UserCreationForm):
    # Add email field (not in base UserCreationForm by default)
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'your@email.com',
            'autocomplete': 'email',
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add placeholders and CSS classes to each field
        self.fields['username'].widget.attrs.update({
            'placeholder': 'Choose a username',
            'autocomplete': 'username',
        })
        self.fields['password1'].widget.attrs.update({
            'placeholder': 'Create a password',
            'autocomplete': 'new-password',
        })
        self.fields['password2'].widget.attrs.update({
            'placeholder': 'Confirm your password',
            'autocomplete': 'new-password',
        })
        # Remove default help texts for cleaner UI
        for field in self.fields.values():
            field.help_text = None

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


# ─────────────────────────────────────────────────────────────
# SUBJECT FORM — add/edit a subject
# ─────────────────────────────────────────────────────────────
class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'e.g., Artificial Intelligence',
                'autofocus': True,
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Brief description of the subject (optional)',
                'rows': 3,
            }),
        }
        labels = {
            'name': 'Subject Name',
            'description': 'Description (optional)',
        }


# ─────────────────────────────────────────────────────────────
# TOPIC FORM — add/edit a topic under a subject
# ─────────────────────────────────────────────────────────────
class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['name', 'difficulty', 'estimated_hours']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'e.g., Neural Networks',
                'autofocus': True,
            }),
            'difficulty': forms.Select(attrs={
                'class': 'form-select',
            }),
            'estimated_hours': forms.NumberInput(attrs={
                'placeholder': '2.0',
                'min': '0.5',
                'max': '20',
                'step': '0.5',
            }),
        }
        labels = {
            'name': 'Topic Name',
            'difficulty': 'Difficulty Level',
            'estimated_hours': 'Estimated Study Hours',
        }


# ─────────────────────────────────────────────────────────────
# EXAM FORM — set exam date for a subject
# ─────────────────────────────────────────────────────────────
class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['subject', 'exam_date', 'notes']
        widgets = {
            'exam_date': forms.DateInput(attrs={
                'type': 'date',  # HTML5 date picker
            }),
            'notes': forms.Textarea(attrs={
                'placeholder': 'Any notes about this exam (optional)',
                'rows': 3,
            }),
        }
        labels = {
            'subject': 'Select Subject',
            'exam_date': 'Exam Date',
            'notes': 'Notes (optional)',
        }

    def __init__(self, user, *args, **kwargs):
        """Filter subjects to show only the logged-in user's subjects."""
        super().__init__(*args, **kwargs)
        self.fields['subject'].queryset = Subject.objects.filter(user=user)

    def clean_exam_date(self):
        """Validate that exam date is not in the past."""
        exam_date = self.cleaned_data.get('exam_date')
        if exam_date and exam_date < timezone.now().date():
            raise forms.ValidationError("Exam date cannot be in the past!")
        return exam_date
