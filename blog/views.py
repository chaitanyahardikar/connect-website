from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post
from django.contrib.auth.models import User
from users.models import Profile
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

import random

items = Profile.objects.all()
# change 3 to how many random items you want
#if items.count() >= 5:
#	randusers = random.sample(list(items), 5) REASON FOR NOT USING: this causes problems
# in creating new columns in db

# if you want only a single random item
#random_item = random.choice(items)


#uses cbv
def home(request):
	print("1")
	print(randusers)
	context = {
        'posts': Post.objects.all(),
        'randusers' : User.objects.order_by('?')[:5],
    }
	return render(request, 'blog/home.html', context)

class PostListView(LoginRequiredMixin, ListView):
	model = Post
	template_name = 'blog/home.html'
	context_object_name = 'posts'
	ordering = '-date_posted'
	paginate_by = 4

	def get_context_data(self, **kwargs):
		context = super(PostListView, self).get_context_data(**kwargs)
		context['randusers'] = User.objects.order_by('?')[:5]
		
		# likes_connected = get_object_or_404(Post, id=self.kwargs['pk'])
		# liked = False
		# if likes_connected.likes.filter(id=self.request.user.id).exists():
		# 	liked = True
		# context['number_of_likes'] = likes_connected.number_of_likes()
		# context['post_is_liked'] = liked
		return context


class PostDetailView(DetailView):
	model = Post
	context_object_name = 'post'
	def get_context_data(self, **kwargs):
		context = super(PostDetailView, self).get_context_data(**kwargs)

		likes_connected = get_object_or_404(Post, id=self.kwargs['pk'])
		liked = False
		if likes_connected.likes.filter(id=self.request.user.id).exists():
			liked = True
		context['number_of_likes'] = likes_connected.number_of_likes()
		context['post_is_liked'] = liked
		context['randusers'] = User.objects.order_by('?')[:5]
		return context

class PostCreateView(LoginRequiredMixin, CreateView):
	model = Post
	fields = ['title', 'content', 'image']

	def get_context_data(self, **kwargs):
		context = super(PostCreateView, self).get_context_data(**kwargs)
		context['randusers'] = User.objects.order_by('?')[:5]
		return context

	def form_valid(self, form):
		form.instance.author = self.request.user
		return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
	model = Post
	fields = ['title', 'content', 'image']

	def get_context_data(self, **kwargs):
		context = super(PostUpdateView, self).get_context_data(**kwargs)
		context['randusers'] = User.objects.order_by('?')[:5]
		return context

	def form_valid(self, form):
		form.instance.author = self.request.user
		return super().form_valid(form)

	def test_func(self):
		post = self.get_object()
		if self.request.user == post.author:
			return True
		return False

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
	model = Post
	context_object_name = 'post'
	success_url = '/'

	def get_context_data(self, **kwargs):
		context = super(PostDeleteView, self).get_context_data(**kwargs)
		context['randusers'] = User.objects.order_by('?')[:5]
		return context

	def test_func(self):
		post = self.get_object()
		if self.request.user == post.author:
			return True
		return False


def about(request):
	return render(request, 'blog/about.html', {'title': 'About'})

def PostLike(request, pk):
    post = get_object_or_404(Post, id=request.POST.get('post_id'))
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)

    return HttpResponseRedirect(reverse('post-detail', args=[str(pk)]))
