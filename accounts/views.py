from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login (request, user)
            return redirect('dashboard_redirect')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})
    
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard_redirect')
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard_redirect(request):
    role = request.user.role
    if role == 'student':
        return redirect('student_dashboard')
    elif role == 'instructor':
        return redirect('instructor_dashboard')
    elif role == 'admin':
        return redirect('admin_dashboard')


