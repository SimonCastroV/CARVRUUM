from django import forms


class MessageForm(forms.Form):
    text = forms.CharField(
        max_length=2000,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Escribe un mensaje...",
                "class": "flex-1 rounded-2xl border border-slate-300 px-4 py-3 outline-none focus:border-blue-500 dark:border-slate-700 dark:bg-slate-950",
            }
        ),
    )