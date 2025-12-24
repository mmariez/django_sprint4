from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views import View
from django.utils.decorators import method_decorator
from blogicum.utils import send_welcome_email
from blog.models import Post
from .forms import CreationForm, EditProfileForm, StaticPageForm
from .models import StaticPage
from blog.utils import get_published_posts_with_comments, paginate_posts


# Кастомные обработчики ошибок
def csrf_failure(request, reason=''):
    return render(request, 'pages/403csrf.html', status=403)


def page_not_found(request, exception):
    return render(request, 'pages/404.html', status=404)


def server_error(request):
    return render(request, 'pages/500.html', status=500)


# Регистрация
def signup(request):
    if request.method == 'POST':
        form = CreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Отправляем приветственное письмо
            if user.email:
                try:
                    send_welcome_email(user)
                except Exception:
                    pass  # Игнорируем ошибки отправки почты в разработке
            return redirect('blog:index')
    else:
        form = CreationForm()
    return render(request,
                  'pages/registration/registration_form.html',
                  {'form': form})


def user_profile(request, username):
    profile = get_object_or_404(User, username=username)

    # Проверяем, является ли текущий пользователь владельцем профиля
    is_owner = request.user.is_authenticated and request.user == profile

    if is_owner:
        posts = get_published_posts_with_comments(
            queryset=profile.posts.all(),  
            include_unpublished_for_author=profile  # Показываем неопубликованные автору
        )
    else:
        # Остальные видят только опубликованные посты
        posts = get_published_posts_with_comments(
            queryset=profile.posts.all()  
        )

    page_obj = paginate_posts(request, posts)

    context = {
        'profile': profile,
        'page_obj': page_obj,
        'is_owner': is_owner,
    }
    return render(request, 'blog/profile.html', context)


# Редактирование профиля
@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('pages:profile', username=request.user.username)
    else:
        form = EditProfileForm(instance=request.user)
    return render(request, 'blog/user.html', {'form': form})


# CBV для статичных страниц
class StaticPageListView(ListView):
    model = StaticPage
    template_name = 'pages/staticpage_list.html'
    context_object_name = 'pages'

    def get_queryset(self):
        return StaticPage.objects.filter(is_published=True)


class StaticPageDetailView(DetailView):
    model = StaticPage
    template_name = 'pages/staticpage_detail.html'
    context_object_name = 'page'

    def get_queryset(self):
        return StaticPage.objects.filter(is_published=True)


class StaticPageCreateView(LoginRequiredMixin, CreateView):
    model = StaticPage
    form_class = StaticPageForm
    template_name = 'pages/staticpage_form.html'
    success_url = reverse_lazy('pages:staticpage_list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class StaticPageUpdateView(LoginRequiredMixin, UpdateView):
    model = StaticPage
    form_class = StaticPageForm
    template_name = 'pages/staticpage_form.html'

    def get_success_url(self):
        return reverse_lazy('pages:staticpage_detail',
                            kwargs={'slug': self.object.slug})


class AboutView(TemplateView):
    template_name = 'pages/about.html'


class RulesView(TemplateView):
    template_name = 'pages/rules.html'


class SignUpView(View):
    def dispatch(self, request, *args, **kwargs):
        return signup(request)


class EditProfileView(View):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return edit_profile(request)


class ProfileView(View):
    def dispatch(self, request, *args, **kwargs):
        username = kwargs.get('username')
        return user_profile(request, username)
