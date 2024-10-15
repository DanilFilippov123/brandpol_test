from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet, ModelForm

from tests.models import TestModel, ThemeModel, QuestionModel, VariantModel


# Register your models here.
class AdminVariantsInlineFormSet(BaseInlineFormSet):

    def clean(self):
        super().clean()

        # if question dont activated then return without check
        if not self.instance.activated:
            return

        q: QuestionModel = self.instance
        curr_correct = q.variants.filter(is_correct=True).count()
        all_variants = q.variants.count()
        add_correct = 0
        form: ModelForm
        for form in self.forms:
            if len(form.cleaned_data) == 0:
                continue
            if form.cleaned_data["DELETE"]:
                all_variants -= 1
                if form.cleaned_data["is_correct"]:
                    add_correct -= 1
                continue

            if form.instance.pk is None:
                # new variant
                all_variants += 1
                if form.cleaned_data["is_correct"]:
                    add_correct += 1
                continue

            if 'is_correct' in form.changed_data:
                # changed variant correctness
                if form.cleaned_data["is_correct"]:
                    add_correct += 1
                else:
                    add_correct -= 1

        new_correct = curr_correct + add_correct
        if new_correct < 1:
            raise ValidationError("Необходимо выбрать хотя бы один верный вариант")
        if new_correct >= all_variants:
            raise ValidationError("Необходимо выбрать хотя бы один неверный вариант")


class VariantInline(admin.StackedInline):
    model = VariantModel

    verbose_name = 'Вариант'
    verbose_name_plural = 'Варианты'

    formset = AdminVariantsInlineFormSet


class QuestionInline(admin.StackedInline):
    model = QuestionModel
    fields = ['name']
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
