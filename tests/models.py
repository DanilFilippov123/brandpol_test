from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse


# Create your models here.

class ThemeModel(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)

    class Meta:
        verbose_name = 'Тема'
        verbose_name_plural = 'Темы'

    def __str__(self):
        return self.name


class TestModel(models.Model):
    name = models.CharField(max_length=255,
                            blank=False,
                            null=False,
                            verbose_name='Название теста')
    theme = models.ForeignKey(ThemeModel,
                              on_delete=models.SET_NULL,
                              null=True,
                              related_name='tests',
                              verbose_name='Тема')

    def get_absolute_url(self):
        return reverse('tests:test', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = 'Тест'
        verbose_name_plural = 'Тесты'

    def __str__(self):
        return self.name


class QuestionModel(models.Model):
    name = models.CharField(max_length=255,
                            blank=False,
                            null=False,
                            verbose_name='Название вопроса')
    test = models.ForeignKey(TestModel,
                             on_delete=models.CASCADE,
                             null=False,
                             related_name='questions',
                             verbose_name='Тест')

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'

    def __str__(self):
        return self.name


class VariantModel(models.Model):
    name = models.CharField(max_length=255,
                            blank=False,
                            null=False,
                            verbose_name='Название варианта')
    is_correct = models.BooleanField(default=False,
                                     verbose_name='Правильный-ли вариант')
    question = models.ForeignKey(QuestionModel,
                                 on_delete=models.CASCADE,
                                 null=False,
                                 related_name='variants',
                                 verbose_name='Вопрос')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Вариант'
        verbose_name_plural = 'Варианты'


class UserTestHistoryModel(models.Model):
    user = models.ForeignKey(get_user_model(),
                             on_delete=models.CASCADE,
                             verbose_name='Пользователь')
    test = models.ForeignKey(TestModel,
                             on_delete=models.CASCADE,
                             null=False,
                             related_name='user_tests',
                             verbose_name='Тест')
    date = models.DateTimeField(auto_now_add=True,
                                verbose_name='Дата прохождения теста')
    score = models.IntegerField(default=0,
                                validators=[MaxValueValidator(100),
                                            MinValueValidator(0)],
                                verbose_name='Оценка')

    def __str__(self):
        return f'{self.user} - {self.test}'

    class Meta:
        verbose_name = 'Пройденный тест'
        verbose_name_plural = 'Пройденные тесты'
