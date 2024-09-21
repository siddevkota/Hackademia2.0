from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.utils.timezone import now
import string, random
import re

def get_random_string(lenght):
    letter = string.ascii_letters
    return ''.join(random.choice(letter) for i in range(lenght))

# Create your models here.

COURSE_TYPE = [
    ("FREE","FREE"),
    ("PAID","PAID"),
]

class Course(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    # thumbnail_url = models.CharField(max_length=100)
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)  # New image field

    course_type = models.CharField(max_length=4,choices=COURSE_TYPE, default="FREE")
    course_length = models.CharField(max_length=20)
    course_slug = models.SlugField(default="-")
    course_price = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.course_type} - {self.title}."

    def save(self, *args, **kwargs):
        self.course_slug = slugify(self.title)
        self.course_slug += f"-{get_random_string(10)}"
        if self.course_type == "FREE":
            course_price = 0
        super().save(*args, **kwargs)

class Section(models.Model):
    title = models.CharField(max_length=100)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.title} - {self.course}"
    

LECTURE_TYPE = [
    ("PREMIUM","PREMIUM"),
    ("NOT PREMIUM","NOT PREMIUM"),
]

class Lecture(models.Model):
    title = models.CharField(max_length=100)
    video_url = models.CharField(max_length=255)  # Increased length for URLs
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, blank=True)
    lecture_slug = models.SlugField(default="-")
    lecture_type = models.CharField(max_length=12, choices=LECTURE_TYPE, default="PREMIUM")
    
    def save(self, *args, **kwargs):
        # Automatically set the course from the section
        self.course = self.section.course
        # Slugify the lecture title and append a random string to avoid conflicts
        self.lecture_slug = slugify(self.title)
        self.lecture_slug += f"-{get_random_string(10)}"
        # Automatically set lecture type based on course type
        if self.section.course.course_type == "FREE":
            self.lecture_type = "NOT PREMIUM"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.id} - {self.title} - {self.section} - {self.lecture_type}"

    def get_youtube_id(self):
        """
        Extract the YouTube video ID from the video URL.
        Assumes the URL is in the form: https://www.youtube.com/watch?v=VIDEO_ID
        or https://youtu.be/VIDEO_ID
        """
        youtube_regex = (
            r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/'
            r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
        match = re.search(youtube_regex, self.video_url)
        if match:
            return match.group(6)
        return None
class LectureComment(models.Model):
    comment = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.id} - {self.user.username} - {self.comment[0:15]} ..."
    
class AIContent(models.Model):
    lesson = models.ForeignKey(Lecture, on_delete=models.CASCADE, related_name='ai_contents')
    prompt = models.TextField()
    generated_content = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"AI Content for {self.lesson.title}"
    
class Quiz(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    question = models.TextField()
    option1 = models.CharField(max_length=100)
    option2 = models.CharField(max_length=100)
    option3 = models.CharField(max_length=100)
    option4 = models.CharField(max_length=100)
    answer = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.question[0:15]} ..."