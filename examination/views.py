from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Category, QuestionSet, Question, Candidate, Exam, ExamHistory
from django.db import transaction
from django.contrib import messages
from django.core.mail import send_mail
from django.db.models import Count, Avg
import json
from django.utils import timezone
from datetime import timedelta

def welcome(request):
    return render(request, 'welcome.html')

def loginUser(request):
    if request.method == "POST":
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')

        if not email or not password:
            return redirect('login')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return redirect('login')
        
        user = authenticate(request, username=user.username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return redirect('login')

    return render(request, 'login.html')

def registerUser(request):
    if request.method == "POST":
        username = request.POST.get('username', '')
        first_name = request.POST.get('firstname', '')
        last_name = request.POST.get('lastname', '')
        email = request.POST.get('email', '')
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        if not username or not first_name or not last_name or not email or not password1 or not password2 or (password1 != password2):
            return redirect('register')

        try:
            User.objects.create_superuser(username=username, first_name=first_name, last_name=last_name, email=email, password=password1)
            return redirect('login')
        except:
            return redirect('register')
        
    return render(request, 'register.html')

def logoutUser(request):
    logout(request)
    return redirect("welcome")

def dashboard(request):
    total_categories = Category.objects.count()
    total_sets = QuestionSet.objects.count()
    total_questions = Question.objects.count()
    active_exams = Exam.objects.filter(status=False, verified=False).count()

    # Performance Over Time (last 6 months)
    six_months_ago = timezone.now() - timedelta(days=180)
    exams_by_month = Exam.objects.filter(
        created_at__gte=six_months_ago, score__isnull=False
    ).extra(
        select={'month': "strftime('%%Y-%%m', created_at)"}
    ).values('month').annotate(avg_score=Avg('score')).order_by('month')
    
    months = [entry['month'] for entry in exams_by_month]
    scores = [entry['avg_score'] for entry in exams_by_month]
    if not months:
        months = [(timezone.now() - timedelta(days=i*30)).strftime('%Y-%m') for i in range(5, -1, -1)]
        scores = [0] * 6

    category_stats = QuestionSet.objects.values('category__name').annotate(count=Count('questions')).order_by('-count')
    category_names = [stat['category__name'] for stat in category_stats]
    category_counts = [stat['count'] for stat in category_stats]
    if not category_names:
        category_names = ['No Categories']
        category_counts = [0]

    # Recent Activity
    recent_activities = Candidate.objects.order_by('-created_at')[:5]
   
    context = {
        'total_categories': total_categories,
        'total_sets': total_sets,
        'total_questions': total_questions,
        'active_exams': active_exams,
        'months': json.dumps(months),
        'scores': json.dumps(scores),
        'category_names': json.dumps(category_names),
        'category_counts': json.dumps(category_counts),
        'recent_activities': recent_activities,
    }
    return render(request, 'dashboard.html', context)

def categories(request):
    if request.method == "POST":
        name = request.POST.get('name', '')
        description = request.POST.get('description', '')

        if not name or not description:
            return redirect("categories")
        else:
            try:
                Category.objects.create(name=name, description=description, created_by=request.user)
                return redirect("categories")
            except Exception as e:
                print(e)

    categories = Category.objects.all()
    return render(request, 'categories.html', {'categories': categories})

def editCategory(request, category_id):
    category = get_object_or_404(Category, id=category_id, created_by=request.user)
    name = request.POST.get('name')
    description = request.POST.get('description')
    if name and description:
        category.name = name
        category.description = description
        category.save()
        messages.success(request, "Category updated successfully!")
    else:
        messages.error(request, "Please fill in all fields.")
    return redirect('categories')

def deleteCategory(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    category.delete()
    messages.success(request, "Category deleted successfully!")
    return redirect('categories')

def sets(request):
    if request.method == "POST":
        category_id = request.POST.get('category', '')
        name = request.POST.get('name', '')
        level = request.POST.get('level', '')

        if not name or not level or not category_id:
            return redirect("sets")
        else:
            category = Category.objects.get(id=category_id)
            QuestionSet.objects.create(category=category, name=name, level=level)
            return redirect("sets")

    sets = QuestionSet.objects.all()
    categories = Category.objects.all()
    return render(request, 'sets.html', {'sets': sets, 'categories': categories})

def editSet(request):
    if request.method == "POST":
        id = request.POST.get('id', '').strip()
        name = request.POST.get('name', '').strip()
        level = request.POST.get('level', '').strip()
        
        if not request or not level:
            return redirect('sets')
        
        instance = QuestionSet.objects.get(id=int(id))
        instance.level = level
        instance.name = name
        instance.save()

    return redirect('sets')
            
def removeSet(request):
    if request.method == "POST":
        id = request.POST.get('id', '').strip()
        if not id:
            return redirect('sets')
        
        instance = QuestionSet.objects.get(id=int(id))
        instance.delete()

    return redirect('sets')

def questions(request):
    if request.method == "POST":
        set_id = request.POST.get('set', '')
        question = request.POST.get('question', '')
        option1 = request.POST.get('option1', '')
        option2 = request.POST.get('option2', '')
        option3 = request.POST.get('option3', '')
        option4 = request.POST.get('option4', '')
        answer = request.POST.get('answer', '')

        if not set or not question or not option1 or not option2 or not option3 or not option4:
            return redirect("questions")
        else:
            set_ins = QuestionSet.objects.get(id=set_id)
            Question.objects.create(
                set = set_ins, 
                question = question, 
                option1 = option1,
                option2 = option2,
                option3 = option3,
                option4 = option4,
                answer = answer,
            )
            return redirect('questions')
    
    categories = Category.objects.all()
    sets = QuestionSet.objects.all()
    questions = Question.objects.all()
    return render(request, 'questions.html', {'categories': categories, 'sets': sets, 'questions': questions})

def editQuestion(request):
    question_id = request.POST.get('id')
    question_text = request.POST.get('question')
    option1 = request.POST.get('option1')
    option2 = request.POST.get('option2')
    option3 = request.POST.get('option3')
    option4 = request.POST.get('option4')
    answer = request.POST.get('answer')
    
    if question_id and question_text and option1 and option2 and option3 and option4 and answer:
        question = get_object_or_404(Question, id=question_id, set__category__created_by=request.user)
        question.question = question_text
        question.option1 = option1
        question.option2 = option2
        question.option3 = option3
        question.option4 = option4
        question.answer = answer
        question.save()
        messages.success(request, "Question updated successfully!")
    else:
        messages.error(request, "Please fill in all fields.")
    return redirect('questions')

def deleteQuestion(request):
    question_id = request.POST.get('id')
    if question_id:
        question = get_object_or_404(Question, id=question_id)
        question.delete()
        messages.success(request, "Question deleted successfully!")
    return redirect('questions')

def candidates(request):
    categories = Category.objects.all()
    sets = QuestionSet.objects.all()
    candidates = Candidate.objects.filter(exam__isnull=True)
    return render(request, 'candidates.html', {'categories': categories, 'sets': sets, 'candidates': candidates})

def addStudent(request):
    if request.method == "POST":
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        gender = request.POST.get('gender', '')
        category_id = request.POST.get('category', '')
        profession_type = request.POST.get('profession_type', '')
        previous_status = request.POST.get('previous_status', '')

        if not name or not email or not phone or not gender or not category_id or not profession_type:
            return redirect("candidates")

        category = Category.objects.get(id=category_id)
        Candidate.objects.create(
            name = name, 
            email = email, 
            phone = phone,
            gender = gender,
            category = category,
            profession_type = profession_type,
            previous_status = True if previous_status == "on" else False,
        )
        
        return redirect('candidates')

def registerStudent(request):
    if request.method == "POST":
        name = request.POST["name"]
        email = request.POST["email"]
        phone = request.POST["phone"]
        gender = request.POST["gender"]
        category_id = request.POST["category"]
        profession_type = request.POST["profession_type"]
        previous_status = request.POST.get("previous_status") == "on"

        category = Category.objects.get(id=category_id)

        ins = Candidate.objects.create(
            name=name, email=email, phone=phone,
            gender=gender, category=category,
            profession_type=profession_type, previous_status=previous_status
        )
        return redirect("thankyou", candidate_id=ins.id)

    categories = Category.objects.all()
    return render(request, "register-candidate.html", {"categories": categories})

def rejectStudent(request, id):
    candidate = Candidate.objects.get(id=id)

    send_mail(
        "Exam Status",
        message=f"Dear {candidate.name},\n\nHope this mail finds you well.\nYou are not selected for the exam. Please try after 6 months.\n\nBest Regards\nExam Team",
        from_email="Exam Coordinator <adityapatel8912@gmail.com>",
        recipient_list=[candidate.email],
        fail_silently=False
    )
    
    candidate.delete()
    return redirect('candidates')

def sendExamLink(request, id=None):
    candidate = get_object_or_404(Candidate, id=id)
    link = f"http://127.0.0.1:8000/candidate/{candidate.id}/exam-room/"

    if request.method == "POST":
        set_id = request.POST.get('question_set', '')
        set = QuestionSet.objects.get(id=set_id)
        exam = Exam.objects.create(candidate=candidate, set=set)
        code = f"C{candidate.id}E#" + str(exam.id)

        send_mail(
            "🎉 Congratulations on Your Selection – Exam Link Inside!",
            message=f"Dear {candidate.name},\n\nHope this mail finds you well.\nYou are selected for the exam. Please complete the exam in next 24 hours, here is the exam details: \n\nExam Link: {link}\nExam Code: {code}\n\nBest Regards\nExam Team",
            from_email="Exam Coordinator <adityapatel8912@gmail.com>",
            recipient_list=[candidate.email],
            fail_silently=False
        )

    return redirect('candidates')

def examLogin(request, id=None):
    candidate = get_object_or_404(Candidate, id=id)
    
    if request.method == "POST":
        email = request.POST.get('email', '')
        code = request.POST.get('code', '')
        try:
            valid_code = f"C{candidate.id}E#{candidate.exam.id}"
        except:
            print("Unshortlisted profile found")
            return redirect("exam-login", id=id)
        
        if not email or not code or candidate.email != email or code != valid_code:
            return redirect('exam-login', id=id) 
        
        candidate.exam.verified = True
        candidate.exam.save()
        
        if not candidate.exam.status:
            return redirect("exam-instructions", id=id)
        else:
            return redirect("exam-results", id=id)
        
    return render(request, 'exam/exam-login.html')

def instructions(request, id=None):
    candidate = get_object_or_404(Candidate, id=id)      

    if candidate.exam.status:
        return redirect("exam-results", id=id)
    
    return render(request, 'exam/exam-instructions.html', {"candidate": candidate})

def examRoom(request, id=None):
    candidate = get_object_or_404(Candidate, id=id)

    if not candidate.exam.verified:
        return redirect("exam-login", id=candidate.id)
    
    if candidate.exam.status:
        return redirect("exam-results", id=id)

    questions = Question.objects.filter(set=candidate.exam.set)
    return render(request, 'exam/exam-room.html', {'questions': questions, 'candidate': candidate})

def submitExam(request, id=None):
    candidate = get_object_or_404(Candidate, id=id)

    if not request.POST:
        messages.error(request, "No answers submitted.")
        return redirect('exam-room', id=id)

    try:
        exam = candidate.exam
        with transaction.atomic():
            for key, value in request.POST.items():
                if key.startswith('question_') and value in ['1', '2', '3', '4']:
                    question_id = int(key.split('_')[1])
                    question = get_object_or_404(Question, id=question_id)
                    
                    if ExamHistory.objects.filter(exam=exam, question=question).exists():
                        continue

                    correct = (question.answer == f"option{value}")

                    ExamHistory.objects.create(
                        exam=exam,
                        question=question,
                        marked_answer=f"option{value}",
                        correct=correct
                    )

            total = ExamHistory.objects.filter(exam=exam).count()
            correct_answers = ExamHistory.objects.filter(exam=exam, correct=True).count()
            score = (correct_answers / total) * 100 if total > 0 else 0

            exam.score = score
            exam.status = True
            exam.save()

    except Exception as e:
        messages.error(request, f"Error submitting exam: {str(e)}")
        return redirect('exam-room', id=id)

    return redirect('exam-results', id=candidate.id)

def examResults(request, id=None):
    candidate = get_object_or_404(Candidate, id=id)
    total = Question.objects.filter(set=candidate.exam.set).count()
    history = ExamHistory.objects.filter(exam=candidate.exam)
    answered = history.count()
    unanswered = total-answered
    correct = history.filter(correct=True).count()
    incorrect = answered-correct
    score = (correct / total) * 100 if total > 0 else 0
    
    context = {
        'candidate': candidate,
        'history': history,
        'score': score,
        'total': total,
        'answered': answered,
        'unanswered': unanswered,
        'correct': correct,
        'incorrect': incorrect
    }
    return render(request, 'exam/exam_results.html', context)

def history(request):
    exam_histories = Exam.objects.all()

    total_exams = Exam.objects.count()
    unique_candidates = Exam.objects.values('candidate').distinct().count()
    total_questions = ExamHistory.objects.count()
    avg_score = Exam.objects.filter(score__isnull=False).aggregate(Avg('score'))['score__avg'] or 0

    six_months_ago = timezone.now() - timedelta(days=180)
    exams_by_month = Exam.objects.filter(
        created_at__gte=six_months_ago, score__isnull=False
    ).extra(
        select={'month': "strftime('%%Y-%%m', created_at)"}
    ).values('month').annotate(avg_score=Avg('score')).order_by('month')
    
    months = [entry['month'] for entry in exams_by_month]
    avg_scores = [entry['avg_score'] for entry in exams_by_month]
    if not months:
        months = [(timezone.now() - timedelta(days=i*30)).strftime('%Y-%m') for i in range(5, -1, -1)]
        avg_scores = [0] * 6

    context = {
        'exam_histories': exam_histories,
        'total_exams': total_exams,
        'unique_candidates': unique_candidates,
        'total_questions': total_questions,
        'avg_score': avg_score,
        'months': json.dumps(months),
        'avg_scores': json.dumps(avg_scores),
    }
    return render(request, 'history.html', context)

def userSettings(request):
    return render(request, 'settings.html')

def thankyou(request, candidate_id):
    candidate = Candidate.objects.get(id=candidate_id)
    return render(request, "thankyou.html", {'candidate': candidate})
