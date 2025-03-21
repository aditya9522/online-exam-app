from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, EmailValidator


class BaseModel(models.Model):
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract=True           # it will not created as a table in DB 


class Category(BaseModel):
    name = models.CharField(max_length=50, unique=True, null=False, blank=False)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')
    
    def __str__(self):
        return self.name
    
class QuestionSet(BaseModel):
    LEVEL_CHOICES = [
        ('Easy', "Easy"),
        ('Medium', "Medium"),
        ('Hard', "Hard"),
        ('Hybrid', "Hybrid"),
    ]
    
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='sets')
    name = models.CharField(max_length=30, null=False, blank=False)
    level = models.CharField(choices=LEVEL_CHOICES, max_length=10, null=False, blank=False)

    def __str__(self):
        return f"{self.name} for {self.category.name}"

class Question(BaseModel):
    OPTION_CHOICES = [
        ('option1', 'Option 1'),
        ('option2', 'Option 2'),
        ('option3', 'Option 3'),
        ('option4', 'Option 4'),
    ]

    set = models.ForeignKey(QuestionSet, on_delete=models.CASCADE, related_name='questions')
    question = models.TextField(null=False, blank=False)
    option1 = models.CharField(max_length=255, null=False, blank=False)
    option2 = models.CharField(max_length=255, null=False, blank=False)
    option3 = models.CharField(max_length=255, null=False, blank=False)
    option4 = models.CharField(max_length=255, null=False, blank=False)
    answer = models.CharField(choices=OPTION_CHOICES, max_length=10)

    def __str__(self):
        return self.question

class Candidate(BaseModel):
    PF_CHOICES = [
        ('Student', 'Student'),
        ('Fresher', 'Fresher'),
        ('Experienced', 'Experienced'),
    ]

    name = models.CharField(max_length=30, null=False, blank=False)
    email = models.EmailField(unique=True, validators=[EmailValidator()], db_index=True)
    phone = models.CharField(max_length=10, null=False, blank=False, validators=[RegexValidator(r'^\d{10}$', message="Phone number must be 10 digits.")])
    gender = models.CharField(choices=[('Male', 'Male'), ('Female', 'Female'), ('Others', 'Others')], max_length=10, null=False, blank=False)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name='candidates', null=True)
    profession_type = models.CharField(choices=PF_CHOICES, max_length=15)
    previous_status = models.BooleanField(null=False, blank=False)

    def __str__(self):
        return self.name

class Exam(BaseModel):
    candidate = models.OneToOneField(Candidate, on_delete=models.CASCADE, related_name='exam')
    set = models.ForeignKey(QuestionSet, on_delete=models.CASCADE, related_name='exams')
    verified = models.BooleanField(default=False)
    status = models.BooleanField(default=False)
    score = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Exam for {self.candidate.name} on {self.set.name}"


class ExamHistory(BaseModel):
    MARKED_CHOICES = [
        ('option1', 'Option 1'),
        ('option2', 'Option 2'),
        ('option3', 'Option 3'),
        ('option4', 'Option 4'),
    ]
    
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='exam_history')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    marked_answer = models.CharField(choices=MARKED_CHOICES, max_length=10, null=False, blank=False)
    correct = models.BooleanField(null=False, blank=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['exam', 'question'], 
                name='unique_exam_question'
            )
        ]

    def __str__(self):
        return f"History for Exam {self.exam.id}, Question {self.question.id}"


