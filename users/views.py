from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.auth.decorators import login_required
from blog.models import Post 
from .models import Profile, FriendRequest
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.conf import settings
from django.http import HttpResponseRedirect

User = get_user_model()

def friend_list(request):
	p = request.user.profile
	friends = p.friends.all()
	rec_friend_requests = FriendRequest.objects.filter(to_user=p.user)
	user_req_list = []
	for r in rec_friend_requests:
		user_req_list.append(getattr(r,'from_user'))
	context={
		'friends': friends,
		'randusers' : User.objects.order_by('?')[:5],
		'user_req_list': user_req_list,
	} 
	return render(request, "users/friend_list.html", context)

@login_required
def send_friend_request(request, id):
	user = get_object_or_404(User, id=id)
	frequest, created = FriendRequest.objects.get_or_create(
			from_user=request.user,
			to_user=user)
	return HttpResponseRedirect('/profile/{}'.format(user.id))

@login_required
def cancel_friend_request(request, id):
	user = get_object_or_404(User, id=id)
	frequest = FriendRequest.objects.filter(
			from_user=request.user,
			to_user=user).first()
	frequest.delete()
	return HttpResponseRedirect('/profile/{}'.format(user.id))

@login_required
def accept_friend_request(request, id):
	from_user = get_object_or_404(User, id=id)
	frequest = FriendRequest.objects.filter(from_user=from_user, to_user=request.user).first()
	user1 = frequest.to_user
	user2 = from_user
	user1.profile.friends.add(user2.profile)
	user2.profile.friends.add(user1.profile)
	if(FriendRequest.objects.filter(from_user=request.user, to_user=from_user).first()):
		request_rev = FriendRequest.objects.filter(from_user=request.user, to_user=from_user).first()
		request_rev.delete()
	frequest.delete()
	return HttpResponseRedirect('/profile/{}'.format(user2.id))

@login_required
def delete_friend_request(request, id):
	from_user = get_object_or_404(User, id=id)
	frequest = FriendRequest.objects.filter(from_user=from_user, to_user=request.user).first()
	frequest.delete()
	return HttpResponseRedirect('/profile/{}'.format(request.user.id))

def delete_friend(request, id):
	user_profile = request.user.profile
	friend_user = get_object_or_404(User, id=id)
	friend_profile = friend_user.profile
	user_profile.friends.remove(friend_profile)
	friend_profile.friends.remove(user_profile)
	return HttpResponseRedirect('/profile/{}'.format(friend_profile.user.id))


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
	p = profileuser.profile
	u = p.user
	user_posts = Post.objects.filter(author=profileuser).order_by('-date_posted')
	sent_friend_requests = FriendRequest.objects.filter(from_user=p.user)
	rec_friend_requests = FriendRequest.objects.filter(to_user=p.user)
	friends = p.friends.all();
	# is this user our friend
	button_status = 'none'
	if p not in request.user.profile.friends.all():
		button_status = 'not_friend'

		# if we have sent him a friend request
		if len(FriendRequest.objects.filter(
			from_user=request.user).filter(to_user=p.user)) == 1:
				button_status = 'friend_request_sent'

		# if we have recieved a friend request
		if len(FriendRequest.objects.filter(
			from_user=p.user).filter(to_user=request.user)) == 1:
				button_status = 'friend_request_received'


	context = {
		'u' : u,
		'u_form': u_form,
		'p_form': p_form,
		'button_status': button_status,
		'user_posts' : user_posts,
		'user' : user,
		'profileuser' : profileuser,
		'randusers' : User.objects.order_by('?')[:5],
		'sent_friend_requests': sent_friend_requests,
		'rec_friend_requests': rec_friend_requests,
	}

	return render(request, 'users/profile.html', context)

@login_required
def search_users(request):
	query = request.GET.get('q')
	object_list = User.objects.filter(username__icontains=query)
	context ={
		'users': object_list,
		'randusers' : User.objects.order_by('?')[:5],
	}
	return render(request, "users/search_users.html", context)
