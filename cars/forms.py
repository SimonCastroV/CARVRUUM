from django import forms
from .models import Car, CarList


class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ["make", "model", "year", "price", "mileage_km", "city", "description"]


class CarListForm(forms.ModelForm):
    class Meta:
        model = CarList
        fields = ["name", "description"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "w-full rounded-xl border border-slate-200 px-4 py-2 text-sm text-slate-900 dark:border-slate-700 dark:bg-slate-950 dark:text-white",
                "placeholder": "Ej: Carros familiares",
            }),
            "description": forms.Textarea(attrs={
                "class": "w-full rounded-xl border border-slate-200 px-4 py-2 text-sm text-slate-900 dark:border-slate-700 dark:bg-slate-950 dark:text-white",
                "placeholder": "Descripción opcional",
                "rows": 3,
            }),
        }


class AddCarToListsForm(forms.Form):
    lists = forms.ModelMultipleChoiceField(
        queryset=CarList.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Listas",
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["lists"].queryset = CarList.objects.filter(user=user).order_by("name")


class MultipleFileInput(forms.ClearableFileInput):
    # Esto habilita múltiples archivos en Django 5
    allow_multiple_selected = True


class CarImagesForm(forms.Form):
    images = forms.FileField(
        widget=MultipleFileInput(attrs={"multiple": True, "accept": "image/*"}),
        required=True,
    )

    def clean_images(self):
        files = self.files.getlist("images")

        if not files or len(files) < 1:
            raise forms.ValidationError("Debes subir al menos 1 foto.")
        if len(files) > 10:
            raise forms.ValidationError("Máximo 10 fotos por publicación.")

        for f in files:
            content_type = getattr(f, "content_type", "") or ""
            if not content_type.startswith("image/"):
                raise forms.ValidationError("Solo se permiten archivos de imagen.")

        return files