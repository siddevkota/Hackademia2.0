from django.shortcuts import render, redirect, get_object_or_404
from .models import Course, Lecture, Section, LectureComment, Quiz
from student.models import CourseSubscription, StudentInfo, PaymentProcess
from django.http import HttpResponseRedirect, JsonResponse
import razorpay
import json
import requests
import markdown
import logging


# FastAPI endpoints
FASTAPI_SUMMARY_URL = "http://127.0.0.1:8080/summarize_study_material"
FASTAPI_DETAILED_URL = "http://127.0.0.1:8080/get_detailed_content"

def summarize_study_material(request):
    if request.method == "POST":
        # Get the topic from the POST request (assuming you pass it from the form)
        selected_topic = request.POST.get('topic', '')
        

        # Call FastAPI endpoint with the selected topic
        response = requests.post(FASTAPI_SUMMARY_URL, json={'topic': selected_topic})

        if response.status_code == 200:
            data = response.json()
            summary = data.get('summary', 'No summary available.')
            detailed_option = data.get('detailed_option', '')

            # Render the response in the template
            return render(request, 'pdf_summary.html', {
                'summary': summary,
                'detailed_option': detailed_option,
                'topic': selected_topic,
                 # Pass the topic to the template for later use
            })
        else:
            return JsonResponse({'error': 'Error occurred while communicating with the FastAPI API'}, status=500)

    return render(request, 'topic_selection.html')  # Render topic selection form


def get_detailed_study_material(request):
    if request.method == "POST":
        # Get the topic from the POST request (assuming you pass it from the form)
        selected_topic = request.POST.get('topic', '')
       

        # Call FastAPI endpoint with the selected topic for detailed content
        response = requests.post(FASTAPI_DETAILED_URL, json={'topic': selected_topic})

        if response.status_code == 200:
            data = response.json()
            detailed_content = data.get('detailed_content', 'No detailed content available.')

            # Render the detailed content in the template
            return render(request, 'detailed_pdf_summary.html', {
                'detailed_content': detailed_content,
                'topic': selected_topic,
                  # Pass the topic to the template for context
            })
        else:
            return JsonResponse({'error': 'Error occurred while fetching detailed content'}, status=500)


# Create your views here.
def home(request):
    return render(request, 'course/index.html')

def courses(request):
    course = Course.objects.all()
    context = {
        "course": course
    }
    return render(request, 'course/courses.html', context)

def course_detail(request, slug):
    if not Course.objects.filter(course_slug=slug).exists():
        return render(request, '404.html')
    else:
        course = Course.objects.filter(course_slug=slug).first()
        section = Section.objects.filter(course=course)
        lecture = Lecture.objects.filter(course=course)
        if request.user.is_authenticated == True:
            subscription_course = CourseSubscription.objects.filter(student=StudentInfo.objects.filter(username=request.user).first(), 
            course=course).first()
        else:
            subscription_course = None
        context = {
            "course":course,
            "section":section,
            "lecture":lecture,
            "subscription_course":subscription_course,
        }
        return render(request, 'course/course_detail.html', context)
    
# def quiz_page(request):

#     return render(request, 'course/quiz.html', context={"section_id": section_id})

def quiz_page(request, section_id):
    # Retrieve the section and related quiz questions
    section = get_object_or_404(Section, id=section_id)
    questions = Quiz.objects.filter(section=section)

    # Render the quiz template with the questions
    return render(request, 'course/quiz_template.html', {
        'section': section,
        'questions': questions
    })
def submit_quiz(request, section_id):
    # Retrieve the section and related quiz questions
    section = get_object_or_404(Section, id=section_id)
    questions = Quiz.objects.filter(section=section)

    # Initialize the score
    score = 0
    total_questions = questions.count()

    # Check if the method is POST
    if request.method == 'POST':
        for question in questions:
            selected_option = request.POST.get(f'question_{question.id}')
            
            # Compare user's answer with the correct one
            if selected_option == question.answer:
                score += 1

        # Calculate percentage score
        percentage_score = (score / total_questions) * 100

        # Render the result page with the score
        return render(request, 'course/quiz_result.html', {
            'section': section,
            'score': score,
            'total_questions': total_questions,
            'percentage_score': percentage_score
        })

    # Redirect back to the quiz page if method is not POST
    return redirect('quiz_page', section_id=section.id)


def lecture_detail(request, slug, lecture_slug):
    if not Course.objects.filter(course_slug=slug).exists() or not Lecture.objects.filter(lecture_slug=lecture_slug).exists():
        return render(request, '404.html')
    else:
        course = Course.objects.filter(course_slug=slug).first()
        section = Section.objects.filter(course=course)
        lecture = Lecture.objects.filter(course=course)
        video = Lecture.objects.filter(lecture_slug=lecture_slug).first()
        lecture_comment = LectureComment.objects.filter(lecture=video)

        # Call FastAPI to summarize the lecture (based on the video title)
        fastapi_response = None
        simplified_response = None
        if video:
            selected_topic = video.title
            # Use the video title as the topic for FastAPI
            response = requests.post(FASTAPI_SUMMARY_URL, json={'topic': selected_topic})

            if response.status_code == 200:
                fastapi_response = response.json().get('summary', 'No summary available.')
                html_content = markdown.markdown(fastapi_response)  # Convert markdown to HTML

         

            # Return JSON response for AJAX
            # return JsonResponse({'simplified_explanation': simplified_explanation})
        context = {
            "course": course,
            "section": section,
            "lecture": lecture,
            "video": video,
            "lecture_comment": lecture_comment,
            # "fastapi_response": fastapi_response,
            "html_content": html_content,  # Add FastAPI response to context
            # "simplified_summary": simplified_summary,
        }
        return render(request, 'course/lecture.html', context)
def simplified_explanation(request, slug, lecture_slug):
    """Handle the request to get a simplified explanation."""
    
    if not Course.objects.filter(course_slug=slug).exists() or not Lecture.objects.filter(lecture_slug=lecture_slug).exists():
        return render(request, '404.html')
    
    course = Course.objects.filter(course_slug=slug).first()
    lecture = Lecture.objects.filter(course=course)
    video = Lecture.objects.filter(lecture_slug=lecture_slug).first()

    simplified_response = None
    if video:
        selected_topic = video.title

        # Call FastAPI for the simplified explanation
        response = requests.post(FASTAPI_DETAILED_URL, json={'topic': selected_topic})

        if response.status_code == 200:
            simplified_response = response.json().get('detailed_content', 'No simplified explanation available.')
        else:
            simplified_response = 'Failed to get simplified explanation.'

    context = {
        "course": course,
        "lecture": lecture,
        "video": video,
        "simplified_response": markdown.markdown(simplified_response),  # Convert to HTML
    }
    return render(request, 'course/simplified_explanation.html', context)

import requests
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

# Proxy view to forward requests to Flowise API
@csrf_exempt  # Allow this view to accept requests without CSRF token, since it's acting as a proxy
def flowise_proxy(request, path):
    # The base URL for the Flowise API (running on port 3000)
    flowise_url = f'http://localhost:3000/{path}'

    # Determine the request method and forward accordingly
    if request.method == 'GET':
        # Forward GET request to Flowise
        response = requests.get(flowise_url)
    elif request.method == 'POST':
        # Forward POST request to Flowise, along with the POST data
        response = requests.post(flowise_url, data=request.body, headers=request.headers)
    else:
        return HttpResponse("Unsupported request method.", status=405)

    # Return the response from Flowise back to the client
    return JsonResponse(response.json(), safe=False)


def pricing(request):
    course = Course.objects.filter(course_type="PAID")
    context = {
        "course": course
    }
    return render(request, 'course/pricing.html', context)

def videoComment(request):
    if request.user.is_authenticated == True:
        if request.method == 'POST':
            comment = request.POST['comment']
            lecture_id = request.POST['lecture_id']
            video = Lecture.objects.filter(id= lecture_id).first()
            new_comment = LectureComment(comment=comment, user=request.user, lecture=video)
            new_comment.save()

            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return redirect('home')

def Checkout(request, slug):
    if not Course.objects.filter(course_slug = slug).exists():
        return render(request, '404.html')
    else:
        if request.user.is_authenticated == True:
            course = Course.objects.filter(course_slug = slug).first()
            if course.course_price == 0:
                context = {
                    "course":course,
                }
            else:
                with open("secret key.json",'r') as secret:
                    key = json.load(secret)['razorpay']
                student = StudentInfo.objects.filter(username=request.user).first()
                client = razorpay.Client(auth=(key['key id'],key['key secret']))
                payment_id = client.order.create({'amount':course.course_price*100, 'currency':'INR','payment_capture':'1'})
                new_payment = PaymentProcess(student=student, course=course, order_id=payment_id['id'])
                new_payment.save()
                context = {
                    "course":course,
                    "payment":payment_id,
                    "student":student,
                    "key":key['key id'],
                }
            return render(request, 'course/checkout.html', context)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))