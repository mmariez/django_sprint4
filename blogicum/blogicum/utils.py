# blogicum/utils.py
from django.core.mail import send_mail
from django.conf import settings


def send_welcome_email(user):
    """Отправляет приветственное письмо новому пользователю."""
    subject = f'{settings.EMAIL_SUBJECT_PREFIX}Добро пожаловать в Блогикум!'
    message = f"""
    Здравствуйте, {user.username}!

    Добро пожаловать в Блогикум - платформу для ведения блогов!

    Ваш аккаунт успешно создан. Теперь вы можете:
    - Публиковать посты
    - Комментировать публикации других пользователей
    - Редактировать свой профиль

    Приятного использования!

    С уважением,
    Команда Блогикум
    """
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )


def send_comment_notification(post, comment):
    """Отправляет уведомление автору поста о новом комментарии."""
    if post.author.email:
        subject = f'{settings.EMAIL_SUBJECT_PREFIX}Новый комментарий'
        message = f"""
        Здравствуйте, {post.author.username}!

        Пользователь {comment.author.username} оставил комментарий к
        вашему посту "{post.title}":

        "{comment.text}"

        Посмотреть комментарий: http://127.0.0.1:8000/posts/{post.id}/

        С уважением,
        Блогикум
        """
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [post.author.email],
            fail_silently=False,
        )
