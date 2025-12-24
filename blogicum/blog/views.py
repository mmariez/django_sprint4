from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.http import Http404
from .forms import PostForm, CommentForm
from .models import Post, Category, Comment
from blogicum.utils import send_comment_notification
from .utils import get_published_posts_with_comments, paginate_posts
from django.utils import timezone


def index(request):
    """Главная страница со всеми опубликованными постами."""
    posts = get_published_posts_with_comments()
    page_obj = paginate_posts(request, posts)
    return render(request, 'blog/index.html', {'page_obj': page_obj})


def post_detail(request, post_id):
    """Детальная страница поста."""
    post = get_object_or_404(Post, id=post_id)

    if request.user != post.author and not request.user.is_superuser:
        try:
            published_post = Post.objects.get(
                id=post_id,
                is_published=True
            )
        except Post.DoesNotExist:
            raise Http404("Этот пост снят с публикации")
        post = published_post
    
    comments = post.comments.all()

    comment_form = None
    if request.user.is_authenticated:
        comment_form = CommentForm()

    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    """Посты определенной категории."""
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    
    posts = get_published_posts_with_comments(
        queryset=category.posts.all()  
    )
    page_obj = paginate_posts(request, posts)
    
    return render(request, 'blog/category.html', {
        'category': category,
        'page_obj': page_obj
    })


@login_required
def create_post(request):
    """Создание нового поста."""
    
    form = PostForm(request.POST or None, request.FILES or None)
    
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('pages:profile', username=request.user.username)
    
    return render(request, 'blog/create.html', {'form': form})


def edit_post(request, post_id):
    """Редактирование поста."""
    if not request.user.is_authenticated:
        return redirect_to_login(
            request.get_full_path(),
            login_url='/auth/login/',
            redirect_field_name='next'
        )

    post = get_object_or_404(Post, id=post_id)

    if not (request.user == post.author or request.user.is_superuser):
        return redirect('blog:post_detail', post_id=post.id)

    form = PostForm(
        request.POST or None, 
        request.FILES or None, 
        instance=post
    )
    
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post.id)
    
    return render(request, 'blog/create.html', {'form': form})


@login_required
def add_comment(request, post_id):
    """Добавление комментария к посту."""
    post = get_object_or_404(Post, id=post_id)

    if (not post.is_published and request.user != post.author
            and not request.user.is_superuser):
        return redirect('blog:index')

    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()

        # Отправляем уведомление автору поста
        if comment.author != post.author:
            try:
                send_comment_notification(post, comment)
            except Exception:
                pass  # Игнорируем ошибки отправки почты

        return redirect('blog:post_detail', post_id=post.id)

    return redirect('blog:post_detail', post_id=post.id)


@login_required
def edit_comment(request, post_id, comment_id):
    """Редактирование комментария."""
    comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)

    # Проверка прав: только автор может редактировать
    if request.user != comment.author and not request.user.is_superuser:
        return redirect('blog:post_detail', post_id=post_id)

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id=post_id)
    else:
        form = CommentForm(instance=comment)

    return render(request, 'blog/comment.html', {
        'form': form,
        'comment': comment,
        'post_id': post_id,
    })


@login_required
def delete_post(request, post_id):
    """Удаление поста."""
    post = get_object_or_404(Post, id=post_id)

    # Проверка прав: только автор или суперпользователь
    if request.user != post.author and not request.user.is_superuser:
        return redirect('blog:post_detail', post_id=post_id)

    if request.method == 'POST':
        post.delete()
        return redirect('blog:index')

    # GET запрос - показываем страницу подтверждения
    return render(request, 'blog/detail.html', {
        'post': post,
        'is_delete_confirmation': True,
    })


@login_required
def delete_comment(request, post_id, comment_id):
    """Удаление комментария."""
    comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)

    if request.user != comment.author and not request.user.is_superuser:
        return redirect('blog:post_detail', post_id=post_id)

    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)

    # GET запрос - показываем страницу подтверждения
    return render(request, 'blog/comment.html', {
        'comment': comment,
    })