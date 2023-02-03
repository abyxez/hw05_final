from django import forms

from .models import Post, Comment

words_not_to_be_used = [
    "лох",
    "дебил",
    "чмо",
    "мразь",
    "сдохни",
    "сосать",
    "хутин пуй",
]


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("text", "group", "image")

    def clean_text(self):
        data = self.cleaned_data["text"]
        bad_words = []
        for i in words_not_to_be_used:
            if i in data.lower():
                bad_words += i + " "
        if bad_words:
            bad_list = ",".join(bad_words)
            raise forms.ValidationError(
                "Поле должно быть заполнено,"
                "но без ругани, "
                f'"{bad_list}" запрещено использовать!'
            )
        return data


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("text",)

    def clean_subject(self):
        data = self.cleaned_data["text"]
        for i in words_not_to_be_used:
            if i in data.lower():
                bad_words = ""
                bad_words += i
            raise forms.ValidationError(
                "Поле должно быть заполнено,"
                "но без ругани, слова "
                f'"{bad_words}" запрещено использовать!'
            )
        return data
