from flask.ext.babel import lazy_gettext
from flask.ext.htmlbuilder import html
from quokka import admin
from quokka.core.admin import _l, _, ModelAdmin
from quokka.modules.posts.admin import PostAdmin
from quokka.modules.question.models import Question


class QuestionAdmin(PostAdmin):
    column_list = ('title', 'slug', 'pretty_slug', 'channel', 'published', 'created_at',
                   'view_on_site')

    #form_columns = ['title', 'slug', 'channel', 'related_channels', 'summary',
    #                'body', 'choice_A', 'choice_B', 'choice_C', 'choice_D', 'published', 'contents',
    #                'show_on_channel', 'available_at', 'available_until',
    #                'tags', 'comments', 'values', 'template_type']

    def view_on_site(self, request, obj, fieldname, *args, **kwargs):
        return html.a(
            href=obj.get_absolute_url('question-detail'),
            target='_blank',
        )(html.i(class_="icon icon-eye-open", style="margin-right: 5px;")(),
          lazy_gettext('View on site'))

    column_formatters = {'view_on_site': view_on_site,
                         'created_at': ModelAdmin.formatters.get('datetime'),
                         'available_at': ModelAdmin.formatters.get('datetime')}

    form_columns = ['title', 'slug', 'channel',
                    'body', 'choice_A', 'choice_B', 'choice_C', 'choice_D',
                    'choice_E', 'correct_answer']

    form_widget_args = {
        'body': {
            'rows': 20,
            'cols': 20,
            'class': 'text_editor',
            'style': "margin: 0px; width: 725px; height: 200px;"
        },
        'choice_A': {
            'rows': 5,
            'cols': 10,
            'class': 'text_editor',
            'style': "margin: 0px; width: 400px; height: 100px;"
        },
        'choice_B': {
            'rows': 5,
            'cols': 10,
            'class': 'text_editor',
            'style': "margin: 0px; width: 400px; height: 100px;"
        },
        'choice_C': {
            'rows': 5,
            'cols': 10,
            'class': 'text_editor',
            'style': "margin: 0px; width: 400px; height: 100px;"
        },
        'choice_D': {
            'rows': 5,
            'cols': 10,
            'class': 'text_editor',
            'style': "margin: 0px; width: 400px; height: 100px;"
        },
        'choice_E': {
            'rows': 5,
            'cols': 10,
            'class': 'text_editor',
            'style': "margin: 0px; width: 400px; height: 100px;"
        },
        'summary': {
            'style': 'width: 400px; height: 100px;'
        },
        'title': {'style': 'width: 400px'},
        'slug': {'style': 'width: 400px'},
    }

admin.register(Question, QuestionAdmin, category=_("Content"), name=_l("Question"))