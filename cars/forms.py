from django import forms
from .models import Car


class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ["make", "model", "year", "price", "mileage_km", "city", "description"]


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