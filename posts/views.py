from django.shortcuts import get_object_or_404, render
from .models import Group, Post
from . forms import PostForm
from django.shortcuts import redirect
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.urls import reverse

User = get_user_model()


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)

    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'index.html',
        {'page': page, 'paginator': paginator}
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {'group': group, 'page': page,
                                          'paginator': paginator})


@login_required
def new_post(request):
    if request.method != 'POST':
        form = PostForm()
        return render(request, 'newpost.html', {'form': form})
    form = PostForm(request.POST)
    if not form.is_valid():
        return render(request, 'newpost.html', {'form': form})
    new_item = form.save(commit=False)
    new_item.author = request.user
    new_item.save()
    return redirect('index')


def profile(request, username):
    post_user = get_object_or_404(User, username=username)
    posts = post_user.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'profile.html', {'page': page,
                  'paginator': paginator, 'author': post_user})


def post_view(request, username, post_id):
    post_user = User.objects.get(username=username)
    cnt = post_user.posts.all().count()
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    return render(request, 'post.html', {'post': post,
                  'count': cnt, 'post_user': post_user})


def check_author(func):
    def wrapper(request, username, post_id):
        if request.user.get_username() != username:
            url = reverse('post', kwargs={'username': username,
                          'post_id': post_id})
            return redirect(url)
        return func(request, username, post_id)
    return wrapper


@login_required
@check_author
def post_edit(request, username, post_id):
    if request.method != 'POST':
        post = Post.objects.get(pk=post_id)
        form = PostForm(instance=post)
        return render(request, 'newpost.html', {'form': form, 'post': post})
    edited_post = Post.objects.get(pk=post_id)
    form = PostForm(request.POST, instance=edited_post)
    if not form.is_valid():
        return render(request, 'newpot.html',
                      {'form': form, 'post': edited_post})
    form.save()
    url = reverse('post', kwargs={'username': username, 'post_id': post_id})
    return redirect(url)
