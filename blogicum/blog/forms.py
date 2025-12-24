from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ('author', 'created_at')
        widgets = {
            'pub_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local'}
            ),
            'text': forms.Textarea(attrs={'rows': 7}),
        }
        help_texts = {
            'pub_date': 'Если установить дату и время в будущем — '
                        'можно делать отложенные публикации.',
            'is_published': 'Снимите галочку, чтобы скрыть публикацию.',
            'image': 'Загрузите изображение для поста (необязательно).',
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'text': 'Текст комментария',
        }


class DeleteConfirmForm(forms.Form):
    """Форма подтверждения удаления (пустая)."""

    pass
