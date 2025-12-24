# pages/models.py
from django.db import models


class StaticPage(models.Model):
    title = models.CharField('Заголовок', max_length=200)
    slug = models.SlugField('URL', unique=True)
    content = models.TextField('Содержание')
    is_published = models.BooleanField('Опубликовано', default=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'статичная страница'
        verbose_name_plural = 'Статичные страницы'
        ordering = ['title']

    def __str__(self):
        return self.title
