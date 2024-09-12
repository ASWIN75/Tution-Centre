from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, auth
from .models import Course, CustomUser, Teacher, Student,Teacherattendance,Studentattendance,Task,Tasksubmit
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import update_session_auth_hash


# Create your views here.

def home(request):
    return render(request, 'home.html')

def admin_panel(request):
    notifi=CustomUser.objects.filter(status='0').count()
    pending=notifi-1
    return render(request, 'admin_panel.html',{'pen':pending})

def user_login(request):
    return render(request, 'login.html')

def login1(request):
    if request.method == 'POST':
        user_name = request.POST.get('username')
        password1= request.POST.get('password')
        user=authenticate(username=user_name, password=password1)

        if user is not None:
            if user.user_type == '1':
                auth_login(request, user)  # Using auth_login to avoid conflict
                return redirect('admin_panel')
            elif user.user_type == '2':
                auth.login(request, user)
                return redirect('teacher_panel')
        
            elif user.user_type == '3':
                auth.login(request, user)
                return redirect('student_panel')

        else:
            messages.info(request, 'Invalid credentials')
            return redirect('login')

def add_course(request):
    return render(request, 'add_course.html')
def add_coursedb(request):
    if request.method == 'POST':
        course_name = request.POST.get('course_name')
        course_fee = request.POST.get('course_fee')
        course_duration = request.POST.get('course_duration')
        syllabus = request.FILES.get('course_syllabus')

        course = Course(course_name=course_name, fee=course_fee, course_duration=course_duration, syllabus=syllabus)
        course.save()

        messages.success(request, 'Course added successfully!')
        return redirect('add_course')
    
def teacher_register(request):
    courses = Course.objects.all()
    return render(request, 'teacher_register.html',{'course': courses})


#function  for validating mobile number




from django.core.validators import validate_email
from django.core.exceptions import ValidationError

def teacher_registerdb(request):
    if request.method == 'POST':
        # Validate the mobile number
        number = request.POST.get('contact_number')
        if len(number) != 10:
            messages.error(request, 'Phone number should be 10 digits')
            courses = Course.objects.all()
            return render(request, 'teacher_register.html', {'course': courses})
        
        # Validate the email
        email = request.POST.get('email')
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Invalid email format')
            courses = Course.objects.all()
            return render(request, 'teacher_register.html', {'course': courses})

        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        age = request.POST['age']
        sel = request.POST['sel']
        course1 = Course.objects.get(id=sel)
        img = request.FILES.get('img')
        contact_number = request.POST['contact_number']
        user_type = request.POST['text']

        # Check for existing username or email
        if CustomUser.objects.filter(username=username).exists() or CustomUser.objects.filter(email=email ).exists():
            messages.error(request, 'Username or email already exists')
            courses = Course.objects.all()
            return render(request, 'teacher_register.html', {'course': courses})
        
        else:
            user = CustomUser.objects.create_user(username=username, email=email, first_name=first_name, last_name=last_name, user_type=user_type)
            user.save()

            teacher = Teacher(age=age, image=img, number=contact_number, course=course1, user=user)
            teacher.save()
            subject = 'Registration Confirmation'
            message = 'Registration is successful, Please wait for admin approval'
            send_mail(subject, "Hello " + username + ' ' + message, settings.EMAIL_HOST_USER, [email])
            messages.success(request, 'Registration is successful, Please wait for admin approval')
            return redirect('teacher_register')
    
    return render(request, 'teacher_register.html')

from django.db.models import Q


#view for render apd page
def apd(request):
    user =  CustomUser.objects.filter(~Q(user_type=1))
    return render(request, 'apd.html' , {"user" : user})


import random



def approve(request, k):
    print("hello", k)
    usr = CustomUser.objects.get(id=k)
    pas = str(random.randint(100000, 999999))

    if usr.user_type == "2":
        usr.status = 1
        usr.set_password(pas)
        usr.save()
        tea = Teacher.objects.get(user=k)
        subject = 'Admin approved'
        message = f'username: {usr.username}\npassword: {pas}\nemail: {tea.user.email}'
        send_mail(subject, message, settings.EMAIL_HOST_USER, [tea.user.email])

    elif usr.user_type == "3":
        usr.status = 1
        usr.set_password(pas)
        usr.save()
        std = Student.objects.get(user=k)
        subject = 'Admin approved'
        message = f'username: {usr.username}\npassword: {pas}\nemail: {std.user.email}'
        send_mail(subject, message, settings.EMAIL_HOST_USER, [std.user.email])

    messages.success(request, 'User approved successfully.')
    return redirect('apd')




def disapprove(request, k):
    usr = CustomUser.objects.get(id=k)
    if usr.user_type == "2":
        usr.status = 0
        usr.save()
        tea = Teacher.objects.get(user=k)
        tea.delete()
        email = usr.email
        subject = 'Admin Disapproved'
        message = f'Dear {usr.first_name},\n\nYour account has been disapproved by the admin.'
        send_mail(subject, message, settings.EMAIL_HOST_USER, [email])
        passw = CustomUser.objects.get(id=k)
        passw.delete()
        messages.info(request, 'User Disapproved')
        return redirect('apd')

    if usr.user_type == "3":
        usr.status = 0
        usr.save()
        std = Student.objects.get(user=k)
        std.delete()
        email = usr.email
        subject = 'Admin Disapproved'
        message = f'Dear {usr.first_name},\n\nYour account has been disapproved by the admin.'
        send_mail(subject, message, settings.EMAIL_HOST_USER, [email])
        passw = CustomUser.objects.get(id=k)
        passw.delete()
        messages.info(request, 'User Disapproved')
        return redirect('apd')

    

def student_register(request):
    courses = Course.objects.all()
    return render(request, 'student_register.html',{'course': courses})

def student_registerdb(request):
    if request.method == 'POST':
        # Validate the mobile number
        number = request.POST.get('contact_number')
        if len(number) != 10:
            messages.error(request, 'Phone number should be 10 digits')
            courses = Course.objects.all()
            return render(request, 'student_register.html', {'course': courses})
        
        # Validate the email
        email = request.POST.get('email')
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Invalid email format')
            courses = Course.objects.all()
            return render(request, 'student_register.html', {'course': courses})

        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        age = request.POST['age']
        sel = request.POST['sel']
        course1 = Course.objects.get(id=sel)
        img = request.FILES.get('img')
        contact_number = request.POST['contact_number']
        user_type = request.POST['text']

        # Check for existing username or email
        if CustomUser.objects.filter(username=username).exists() or CustomUser.objects.filter(email=email ).exists():
            messages.error(request, 'Username or email already exists')
            courses = Course.objects.all()
            return render(request, 'student_register.html', {'course': courses})
        
        else:
            user = CustomUser.objects.create_user(username=username, email=email, first_name=first_name, last_name=last_name, user_type=user_type)
            user.save()

            student = Student(age=age, image=img, number=contact_number, course=course1, user=user)
            student.save()
            subject = 'Registration Confirmation'
            message = 'Registration is successful, Please wait for admin approval'
            send_mail(subject, "Hello " + username + ' ' + message, settings.EMAIL_HOST_USER, [email])
            messages.success(request, 'Registration is successful, Please wait for admin approval')
            return redirect('student_register')
    
    return render(request, 'student_register.html')

def manage_course(request):
    cour = Course.objects.all()
    return render(request, 'manage_course.html', {'co': cour})

def teacher_details(request):
    teach=Teacher.objects.all()
    ute=CustomUser.objects.all()
    cte=Course.objects.all()
    return render(request, 'teacher_details.html', {'tea':teach,'ut':ute,'ct':cte})

def delete_teacher(request, k):
    teacher = Teacher.objects.get(user=k)
    user = CustomUser.objects.get(id=k)  # Get the associated CustomUser
    teacher.delete() 
     # Delete the Teacher instance
    user.delete()  # Delete the associated CustomUser instance
    return redirect('teacher_details')

def student_details(request):
    std=Student.objects.all()
    ust=CustomUser.objects.all()
    cst=Course.objects.all()
    return render(request, 'student_details.html', {'stu':std,'ut':ust,'ct':cst})

def delete_student(request, k):
    student = Student.objects.get(id=k)
    user = student.user  # Get the associated CustomUser
    student.delete()  # Delete the Teacher instance
    user.delete()  # Delete the associated CustomUser instance
    return redirect('student_details')

def teacher_attendance(request):
    tcr=CustomUser.objects.filter(user_type=2)
    return render(request, 'teacher_attendance.html',{'tc':tcr})

def teach_attend(request):
    if request.method == 'POST':
        tname = request.POST['se']
        tn=CustomUser.objects.get(id=tname)
        tdat=request.POST['da']
        tatt=request.POST['at']
        teach=Teacherattendance(teacher_name=tn,date=tdat,attendance=tatt)
        teach.save()
        messages.info(request, 'Attendance added successfully')
        return redirect('teacher_attendance')
    
def vta(request):
    tename=CustomUser.objects.filter(user_type=2)
    return render(request, 'vta.html',{'te':tename})

def view_teach_attend(request):
    if request.method == 'POST':
        opt=request.POST['tse']
        tec=Teacher.objects.get(user=opt)
        teach=tec.user
        startdate=request.POST['sd']
        enddate=request.POST['ed']
        attend=Teacherattendance.objects.filter(teacher_name=teach,date__range=[startdate,enddate])
        return render(request, 'show_teach_attend.html',{'tea':teach,'atd':attend})
    
def show_teach_attend(request):
    return render(request, 'show_teach_attend.html')

def assign(request):
    course=Course.objects.all()
    teacher=Teacher.objects.all()
    student=Student.objects.all()
    return render(request, 'assign_teacher.html',{'course':course,'teacher':teacher,'student':student})

def assign_teacher(request, student_id, teacher_id):
    student=CustomUser.objects.get(id=student_id)
    teacher=CustomUser.objects.get(id=teacher_id)
    user=Student.objects.get(user=student)
    user.teacher=teacher
    user.save()
    return redirect('assign')

def teacher_panel(request):
    return render(request, 'teacher_panel.html')

def student_attendence(request):
    tusr=request.user.id
    tcr=Student.objects.filter(teacher__id=tusr) #filterrr
    return render(request, 'student_attendence.html',{'tc':tcr})

def stud_attend(request):
    if request.method == 'POST':
        tname=request.POST['se']
        tn=CustomUser.objects.get(id=tname)
        tdat=request.POST['da']
        tatt=request.POST['at']
        teach=Studentattendance(student_name=tn,date=tdat,attendance=tatt)
        teach.save()
        messages.info(request, 'Attendance added successfully')
        return redirect('student_attendence')
    
def vsta(request):
    tea=request.user.id
    stname=Student.objects.filter(teacher=tea)
    return render(request, 'vsta.html',{'st':stname})

def view_stud_attend(request):
    if request.method == 'POST':
        opt=request.POST['tse']
        tec=Student.objects.get(user=opt)
        teach=tec.user
        startdate=request.POST['sd']
        enddate=request.POST['ed']
        attend=Studentattendance.objects.filter(student_name=teach,date__range=[startdate,enddate])
        return render(request, 'show_stud_attend.html',{'tea':teach,'atd':attend})
    
def show_stud_attend(request):
    return render(request, 'show_stud_attend.html')

def teach_attendence(request):
    cur=request.user.id
    usr=Teacherattendance.objects.filter(teacher_name_id=cur)
    return render(request, 'show_tt_attend.html',{'us':usr})
def show_tt_attend(request):
    return render(request, 'show_tt_attend.html')

def view_syllabus(request):
    return render(request, 'view_syllabus.html')

def view_sylla(request):
    tsr=request.user.id
    syll=Course.objects.filter(teacher__user_id=tsr)
    return render(request, 'view_syllabus.html',{'sy':syll})

def teacher_student(request):
    tea=request.user.id
    stu=Student.objects.filter(teacher=tea)
    return render(request, 'teacher_student.html',{'st':stu})



from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import update_session_auth_hash
from TutionApp.models import CustomUser  

def reset_password(request):
    if request.method == 'POST':
        pas = request.POST['np']
        cpas = request.POST['cp']
        if pas == cpas:
            if len(pas) < 6 or not any(char.isupper() for char in pas) \
                    or not any(char.isdigit() for char in pas) \
                    or not any(char in '!@#$%^&*()_+-=[]{}|;:,.<>?/~' for char in pas):
                messages.error(request, 'Password must be at least 6 characters long and contain at least one uppercase letter, one lowercase letter, one digit, and one special character.')
                return redirect('re_pas')
            else:
                usr = request.user.id
                tsr = CustomUser.objects.get(id=usr)
                tsr.set_password(pas)  
                tsr.save()
                update_session_auth_hash(request, tsr)  
                messages.success(request, 'Your password was successfully updated!')
                return redirect('re_pas')
        else:
            messages.error(request, 'Passwords do not match.')
            return redirect('re_pas')
    else:
        return redirect('re_pas')  

            
def re_pas(request):
    return render(request, 'reset_password.html')


def student_panel(request):
    return render(request, 'student_panel.html')

def show_st_attend(request):
    return render(request, 'show_st_attend.html')

def std_attendence(request):
    cusr=request.user.id
    ussr=Studentattendance.objects.filter(student_name_id=cusr)
    return render(request, 'show_st_attend.html',{'uss':ussr})

def view_st_syllabus(request):
    return render(request, 'view_st_syllabus.html')

def view_st_sylla(request):
    ssr=request.user.id
    sylla=Course.objects.filter(student__user_id=ssr)
    return render(request, 'view_st_syllabus.html',{'syl':sylla})


def reset_st_password(request):
    if request.method == 'POST':
        pas = request.POST['np']
        cpas = request.POST['cp']
        if pas == cpas:
            if len(pas) < 6 or not any(char.isupper() for char in pas) \
                    or not any(char.isdigit() for char in pas) \
                    or not any(char in '!@#$%^&*()_+-=[]{}|;:,.<>?/~' for char in pas):
                messages.error(request, 'Password must be at least 6 characters long and contain at least one uppercase letter, one lowercase letter, one digit, and one special character.')
                return redirect('re_paswd')
            else:
                usr = request.user.id
                tsr = CustomUser.objects.get(id=usr)
                tsr.set_password(pas)  
                tsr.save()
                update_session_auth_hash(request, tsr)  
                messages.success(request, 'Your password was successfully updated!')
                return redirect('re_paswd')
        else:
            messages.error(request, 'Passwords do not match.')
            return redirect('re_paswd')
    else:
        return redirect('re_paswd')  

            
def re_paswd(request):
    return render(request, 'reset_st_password.html')

def student_profile(request):
    user = request.user.id
    student = Student.objects.get(user=user)
    return render(request, 'student_profile.html', {'stud': student})


def student_attendence_admin(request):
    st=Studentattendance.objects.all()
    return render(request, 'student_attendence_admin.html',{'st':st})

def task(request):
    return render(request, 'assign_task.html')

def assign_task(request):
    if request.method == 'POST':
        tname = request.POST['tna']
        stda = request.POST['sd']
        etda = request.POST['ed']
        tcr = request.user.id
        tea = CustomUser.objects.get(id=tcr)
        tas = Task(task_name=tname, start_date=stda, end_date=etda, teacher=tea)
        tas.save()
        messages.info(request, 'Task assigned successfully!')
        return redirect('task')
    else:
        return render(request, 'assign_task.html')

    
def view_task(request):
    tec=request.user.id
    tas=Task.objects.filter(teacher=tec)
    return render(request, 'view_task.html',{'ta':tas})
    

# def tasks(request):
#     tusr=request.user.id
#     tcr=Student.objects.get(user=tusr)
#     tea=tcr.teacher
#     tas=Task.objects.filter(teacher=tea)
#     return render(request, 'tasks.html',{'ta':tas})

def tasks(request):
    tusr = request.user.id
    tcr = Student.objects.get(user=tusr)
    tea = tcr.teacher
    
    # Get all tasks assigned to the student by the teacher
    assigned_tasks = Task.objects.filter(teacher=tea)
    
    # Get all tasks already submitted by the student
    submitted_tasks = Tasksubmit.objects.filter(student=request.user).values_list('task', flat=True)
    
    # Exclude the submitted tasks from the assigned tasks
    pending_tasks = assigned_tasks.exclude(task_name__in=submitted_tasks)
    
    return render(request, 'tasks.html', {'ta': pending_tasks})


def submit_task(request):
    return render(request, 'submit_task.html')

def submit(request):
    if request.method == 'POST':
        name=request.POST['tna']
        file=request.FILES['fil']
        desc=request.POST['des']
        stu=request.user.id
        stud=CustomUser.objects.get(id=stu)
        task=Tasksubmit(task=name, File=file, Description=desc, student=stud)
        task.save()
        messages.info(request, 'Task submitted successfully!')
        return redirect('submit_task')
    
def submitted(request):
    tas=Tasksubmit.objects.all()
    return render(request, 'submitted_task.html',{'ta':tas})












        


