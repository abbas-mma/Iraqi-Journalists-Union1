from django import forms
from .models import Note

class NoteForm(forms.ModelForm):
    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'مثلاً: عاجل, داخلي, تعميم',
            'class': 'form-input'
        }),
        help_text='اكتب الوسوم مفصولة بفاصلة'
    )

    expiry_date = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-input'
        }),
        help_text='(اختياري) متى تنتهي صلاحية الوثيقة'
    )

    recipient_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'اسم الجهة المستلمة',
            'class': 'form-input'
        }),
        label='إلى (الجهة المستلمة)'
    )

    class Meta:
        model = Note
        fields = ['title', 'content', 'doc_type', 'file', 'stamp', 'signature', 'expiry_date', 'recipient_name']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'content': forms.Textarea(attrs={'class': 'form-textarea'}),
            'doc_type': forms.Select(attrs={'class': 'form-select'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-input'}),
            'stamp': forms.ClearableFileInput(attrs={'class': 'form-input'}),
            'signature': forms.ClearableFileInput(attrs={'class': 'form-input'}),
        }
