from django import forms


class CheckboxWidget(forms.CheckboxInput):
    template_name = 'tests/widgets/checkbox.html'


class ReadOnlyTextInput(forms.TextInput):
    template_name = 'tests/widgets/read_only_text.html'


class VariantForm(forms.Form):
    template_name_div = 'tests/variant_form.html'

    is_correct = forms.BooleanField(initial=False, widget=CheckboxWidget(), required=False)
    name = forms.CharField(max_length=255, widget=ReadOnlyTextInput())
    pk = forms.IntegerField(widget=forms.HiddenInput())


VariantsFormset = forms.formset_factory(VariantForm, extra=0)
VariantsFormset.template_name_div = 'tests/variant_formset.html'
