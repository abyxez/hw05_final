from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm, CommentForm
from .models import Group, Post, User, Follow

POSTS_SHOWN = 10


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, POSTS_SHOWN)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {"page_obj": page_obj}
    return render(request, "posts/index.html", context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group)
    paginator = Paginator(posts, POSTS_SHOWN)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "page_obj": page_obj,
        "group": group
    }
    return render(request, "posts/group_list.html", context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=author)
    paginator = Paginator(post_list, POSTS_SHOWN)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    to_follow = (
        request.user.is_authenticated
        and Follow.objects.filter(
            user=request.user,
            author=author
        ).exists()
    )
    context = {
        "page_obj": page_obj,
        "author": author,
        "following": to_follow
    }
    return render(request, "posts/profile.html", context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()
    form = CommentForm()
    context = {
        "post": post,
        "comments": comments,
        "form": form
    }
    return render(request, "posts/post_detail.html", context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        form.save()
        return redirect("posts:profile", request.user)
    return render(request, "posts/create_post.html", {"form": form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect("posts:post_detail", post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("posts:post_detail", post_id)
    context = {"form": form, "post": post, "is_edit": True}
    return render(request, "posts/create_post.html", context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect("posts:post_detail", post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts, POSTS_SHOWN)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "page_obj": page_obj
    }
    return render(request, "posts/follow.html", context)


@login_required
def profile_follow(request, username):
    authorObj = get_object_or_404(User, username=username)
    if request.user != authorObj:
        Follow.objects.get_or_create(user=request.user, author=authorObj)
    return redirect("posts:profile", username=authorObj.username)


@login_required
def profile_unfollow(request, username):
    authorObj = get_object_or_404(User, username=username)
    if request.user != authorObj:
        Follow.objects.get(user=request.user, author=authorObj).delete()
    return redirect("posts:profile", username=authorObj.username)
