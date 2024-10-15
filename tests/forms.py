from django import forms
from django.core.exceptions import ValidationError
from django.forms import BaseFormSet


class CheckboxWidget(forms.CheckboxInput):
    template_name = 'tests/widgets/checkbox.html'


class ReadOnlyTextInput(forms.TextInput):
    template_name = 'tests/widgets/read_only_text.html'


class VariantForm(forms.Form):
    template_name_div = 'tests/variant_form.html'

    is_correct = forms.BooleanField(initial=False, widget=CheckboxWidget(), required=False)
    name = forms.CharField(max_length=255,
                           widget=ReadOnlyTextInput(),
                           required=False,
                           initial='')
    pk = forms.IntegerField(widget=forms.HiddenInput())


class BaseVariantsFormset(BaseFormSet):
    template_name_div = 'tests/variant_formset.html'

    def clean(self):
        super().clean()
        if any(self.errors):
            return
        if not any(form.cleaned_data['is_correct'] for form in self.forms):
            raise ValidationError('Необходимо выбрать хотя бы один вариант')


VariantsFormset = forms.formset_factory(VariantForm, extra=0, formset=BaseVariantsFormset)
