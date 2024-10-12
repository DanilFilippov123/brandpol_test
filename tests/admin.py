from django.contrib import admin

from tests.models import TestModel, ThemeModel, QuestionModel, VariantModel


# Register your models here.

class VariantInline(admin.StackedInline):
    model = VariantModel

    verbose_name = 'Вариант'
    verbose_name_plural = 'Варианты'


class QuestionInline(admin.TabularInline):
    model = QuestionModel
    show_change_link = True

    verbose_name = 'Вопрос'
    verbose_name_plural = 'Вопросы'


@admin.register(TestModel)
class TestModelAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]

    verbose_name = 'Тест'
    verbose_name_plural = 'Тесты'


@admin.register(ThemeModel)
class ThemeModelAdmin(admin.ModelAdmin):
    verbose_name = 'Тема'
    verbose_name_plural = 'Темы'


@admin.register(QuestionModel)
class QuestionModelAdmin(admin.ModelAdmin):
    inlines = [VariantInline]

    verbose_name = 'Вопрос'
    verbose_name_plural = 'Вопросы'


@admin.register(VariantModel)
class VariantModelAdmin(admin.ModelAdmin):
    verbose_name = 'Вариант'
    verbose_name_plural = 'Варианты'
