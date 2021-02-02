from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.auth.decorators import login_required
from blog.models import Post 
from django.contrib.auth.models import User


def register(request):
	if(request.method == 'POST'):
		form = UserRegisterForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data.get('username')
			messages.success(request, f'Account created for {username}. Please login to proceed!')
			return redirect('login')
	else:
		form = UserRegisterForm()
	return render(request, 'users/register.html', {'form': form})

@login_required
def profile(request, pk):
	if(request.method == 'POST'):
		u_form = UserUpdateForm(request.POST, instance=request.user)
		p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

		if u_form.is_valid() and p_form.is_valid():
			u_form.save()
			p_form.save()
			messages.success(request, f'Your account has been updated!')
			return redirect('profile', request.user.id)

	else:
		u_form = UserUpdateForm(instance=request.user)
		p_form = ProfileUpdateForm(instance=request.user.profile)

	user = request.user
	profileuser = User.objects.get(pk=pk)
	user_posts = Post.objects.filter(author=profileuser).order_by('-date_posted')
	context = {
		'u_form': u_form,
		'p_form': p_form,
		'user_posts' : user_posts,
		'user' : user,
		'profileuser' : profileuser,
		'randusers' : User.objects.order_by('?')[:4]
	}

	return render(request, 'users/profile.html', context)
