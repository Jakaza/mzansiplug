from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import RecommendedJob, SavedJob, Application, UserSettings , CandidateProfile , Education
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.contrib.auth import logout

from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

# import get_object_or_404 

from django.shortcuts import get_object_or_404


from .forms import CandidateRegisterForm , CandidateProfileForm , EducationForm

User = get_user_model()



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import CandidateProfile, Education, WorkExperience, Skill
from .forms import CandidateProfileForm, EducationForm, WorkExperienceForm, SkillForm

@csrf_exempt
@login_required
def update_personal_info(request):
    if request.method == 'POST':
        profile, _ = CandidateProfile.objects.get_or_create(user=request.user)
        form = CandidateProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success', 'data': form.cleaned_data})
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)



@csrf_exempt
@login_required
def add_education(request):
    if request.method == 'POST':
        form = EducationForm(request.POST)
        if form.is_valid():
            edu = form.save(commit=False)
            edu.user = request.user
            edu.save()
            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)

@csrf_exempt
@login_required
def add_work_experience(request):
    if request.method == 'POST':
        form = WorkExperienceForm(request.POST)
        if form.is_valid():
            exp = form.save(commit=False)
            exp.user = request.user
            exp.save()
            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)

@csrf_exempt
@login_required
def add_skill(request):
    if request.method == 'POST':
        form = SkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.user = request.user
            skill.save()
            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)


@csrf_exempt
@login_required
def delete_skill(request, skill_id):
    if request.method == 'POST':
        skill = get_object_or_404(Skill, id=skill_id, user=request.user)
        skill.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)



@csrf_exempt
@login_required
def delete_work_experience(request, experience_id):
    if request.method == 'POST':
        experience = get_object_or_404(WorkExperience, id=experience_id, user=request.user)
        experience.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@csrf_exempt
@login_required
def delete_education(request, edu_id):
    if request.method == 'POST':
        edu = get_object_or_404(Education, id=edu_id, user=request.user)
        edu.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


def logout_candidate(request):
    logout(request)
    return redirect('index') 


def login_candidate(request):

    if request.user.is_authenticated and request.user.user_type == 'candidate':
        return redirect('profile')


    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # Get cleaned data
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None and user.user_type == 'candidate':
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect('profile')  # Change to your candidate dashboard url name
            else:
                messages.error(request, "Invalid credentials or user is not a candidate.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'login.html', {'form': form})




def register_candidate(request):

    if request.user.is_authenticated and request.user.user_type == 'candidate':
        return redirect('profile')

    if request.method == 'POST':
        form = CandidateRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Deactivate until email is verified
            user.user_type = 'candidate'
            user.save()

            # Prepare verification email
            current_site = get_current_site(request)
            subject = 'Activate your MzansiPlug account'
            message = render_to_string('email_verification.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })

            print(f"Message: {message} : link {current_site.domain}/activate/{urlsafe_base64_encode(force_bytes(user.pk))}/{default_token_generator.make_token(user)}")

            # send_mail(subject, message, 'aiinvigilate@gmail.com', [user.email])

            messages.success(request, 'Account created! Please check your email to activate your account.')
            return redirect('login')
    else:
        form = CandidateRegisterForm()

    return render(request, 'register.html', {'form': form})


def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError, OverflowError):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Your account has been activated. You can now log in.')
        return redirect('login')
    else:
        messages.error(request, 'Activation link is invalid or expired.')
        return redirect('register')



@login_required
def profile_dashboard(request):
    # recommended_jobs = RecommendedJob.objects.filter(user=request.user)
    # saved_jobs = SavedJob.objects.filter(user=request.user)
    # applications = Application.objects.filter(user=request.user)

    # context = {
    #     'recommended_jobs': recommended_jobs,
    #     'saved_jobs': saved_jobs,
    #     'applications': applications
    # }
    return render(request, 'profile_dashboard.html')


@login_required
def profile_details(request):
    profile, _ = CandidateProfile.objects.get_or_create(user=request.user)
    educations = Education.objects.filter(user=request.user)
    experiences = WorkExperience.objects.filter(user=request.user)
    skills = Skill.objects.filter(user=request.user)

    return render(request, 'profile_details.html', {
        'profile': profile,
        'educations': educations,
        'experiences': experiences,
        'skills': skills
    })



@login_required
def settings_page(request):
    # settings, created = UserSettings.objects.get_or_create(user=request.user)

    # if request.method == 'POST':
    #     phone = request.POST.get('phone')
    #     notify = request.POST.get('notifications_enabled') == 'on'

    #     settings.phone_number = phone
    #     settings.notifications_enabled = notify
    #     settings.save()
    #     return redirect('settings')

    # context = {'settings': settings}
    return render(request, 'settings.html')


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()  # saves new password
            update_session_auth_hash(request, user)  # keeps user logged in
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change-password')  # redirect to profile or any other page
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'change_password.html', {'form': form})

