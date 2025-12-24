from django.contrib import admin
from .models import Category, Location, Post
from .models import Comment
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

admin.site.site_header = 'Панель администратора'
admin.site.index_title = 'Блог'
admin.site.site_title = 'Администрирование Блога'


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published', 'created_at')
    list_editable = ('is_published',)
    list_filter = ('is_published',)
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}


class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_published', 'created_at')
    list_editable = ('is_published',)
    list_filter = ('is_published',)
    search_fields = ('name',)


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'pub_date',
        'author',
        'category',
        'location',
        'is_published',
        'created_at'
    )
    list_editable = ('is_published',)
    list_filter = ('is_published', 'category', 'location')
    search_fields = ('title', 'text')
    filter_horizontal = ()
    date_hierarchy = 'pub_date'
    ordering = ('-pub_date',)
    fieldsets = (
        (None, {
            'fields': ('title', 'text', 'author')
        }),
        ('Дополнительные опции', {
            'fields': ('category', 'location', 'pub_date', 'is_published'),
            'classes': ('collapse',)
        }),
    )


# Регистрация моделей
admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Post, PostAdmin)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'created_at', 'text_preview')
    list_filter = ('created_at', 'author')
    search_fields = ('text', 'author__username', 'post__title')
    readonly_fields = ('created_at',)

    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Текст'


admin.site.register(Comment, CommentAdmin)
admin.site.unregister(User)  
admin.site.register(User, UserAdmin)  
