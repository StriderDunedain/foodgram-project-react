from django.forms import Form

from recipes.models import Tag


class TagForm(Form):
    class Meta:
        model = Tag
        fields = ('name', 'color', 'slug')
