# coding: utf-8

import logging
import collections
from datetime import datetime
import random
from flask import request, redirect, url_for, session
from flask.views import MethodView
from flask.ext.mongoengine.wtf import model_form
from wtforms import RadioField, TextField
from quokka.core.models import Channel, Content, Comment
from quokka.core.templates import render_template
from quokka.modules.question.models import Question, Answer

logger = logging.getLogger()


class QuestionList(MethodView):
    object_name = "question"
    template_suffix = "list"
    template_ext = "html"

    def get_template_names(self):

        if self.channel.channel_type:
            type_suffix = self.channel.channel_type.template_suffix
        else:
            type_suffix = 'default'

        self.template_suffix = "{0}_{1}".format(type_suffix,
                                                self.template_suffix)

        common_data = dict(
            object_name=self.object_name,
            suffix=self.template_suffix,
            ext=self.template_ext
        )

        channel_list = self.channel.get_ancestors_slugs()
        names = [
            u"{object_name}/{channel}/{suffix}.{ext}".format(
                channel=channel, **common_data
            )
            for channel in channel_list
        ]

        names.append(u"{object_name}/{suffix}.{ext}".format(**common_data))

        return names

    def get(self, pretty_slug):
        now = datetime.now()
        path = pretty_slug.split('/')
        mpath = ",".join(path)
        mpath = ",{0},".format(mpath)

        channel = Channel.objects.get_or_404(mpath=mpath)

        if channel.render_content:
            return QuestionDetail().get(
                channel.render_content.content.pretty_slug, True)

        self.channel = channel

        base_filters = {}

        filters = {
            'published': True,
            'available_at__lte': now,
            'show_on_channel': True
        }

        if not channel.is_homepage:
            base_filters['__raw__'] = {
                'mpath': {'$regex': "^{0}".format(mpath)}}

        filters.update(channel.get_content_filters())
        contents = Content.objects(**base_filters).filter(**filters)

        themes = channel.get_themes()
        return render_template(self.get_template_names(),
                               theme=themes, contents=contents)


class QuestionDetail(MethodView):
    object_name = "question"
    template_suffix = "detail"
    template_ext = "html"

    Form = model_form(
        Answer,
        exclude=['answer', 'created_at', 'created_by', 'published']
    )

    def get_template_names(self):

        if self.question.template_type:
            type_suffix = self.question.template_type.template_suffix
        else:
            type_suffix = 'default'

        self.template_suffix = "{0}_{1}".format(type_suffix,
                                                self.template_suffix)

        module_name = self.question.module_name
        model_name = self.question.model_name

        common_data = dict(
            object_name=self.object_name,
            module_name=module_name,
            model_name=model_name,
            suffix=self.template_suffix,
            ext=self.template_ext
        )

        names = [
            u"{object_name}/{content_slug}.{ext}".format(
                content_slug=self.question.long_slug, **common_data),
            u"{object_name}/{content_slug}_{suffix}.{ext}".format(
                content_slug=self.question.long_slug, **common_data),
            u"{object_name}/{content_slug}.{ext}".format(
                content_slug=self.question.slug, **common_data),
            u"{object_name}/{content_slug}_{suffix}.{ext}".format(
                content_slug=self.question.slug, **common_data)
        ]

        channel_list = self.question.channel.get_ancestors_slugs()
        for channel in channel_list:
            path = ("{object_name}/_{module_name}/{channel}/"
                    "{model_name}_{suffix}.{ext}")
            names.append(path.format(channel=channel, **common_data))

        for channel in channel_list:
            path = "{object_name}/_{module_name}/{channel}/{suffix}.{ext}"
            names.append(path.format(channel=channel, **common_data))

        names.append(
            "{object_name}/_{module_name}/{model_name}_{suffix}.{ext}".format(
                **common_data
            )
        )

        names.append(
            "{object_name}/_{module_name}/{suffix}.{ext}".format(**common_data)
        )

        for channel in channel_list:
            path = "{object_name}/{channel}/{model_name}_{suffix}.{ext}"
            names.append(path.format(channel=channel, **common_data))

        for channel in channel_list:
            path = "{object_name}/{channel}/{suffix}.{ext}"
            names.append(path.format(channel=channel, **common_data))

        names.append(
            "{object_name}/{model_name}_{suffix}.{ext}".format(**common_data)
        )

        names.append("{object_name}/{suffix}.{ext}".format(**common_data))

        return names

    def get_context_by_pretty_slug(self, pretty_slug, render_content=False):

        now = datetime.now()
        homepage = Channel.objects.get(is_homepage=True)

        if pretty_slug.startswith(homepage.slug) and \
                len(pretty_slug.split('/')) < 3 and \
                not render_content:
            slug = pretty_slug.split('/')[-1]
            return redirect(url_for('detail', long_slug=slug))

        filters = {
            'published': True,
            'available_at__lte': now
        }

        try:
            question = Question.objects.get(
                pretty_slug=pretty_slug,
                **filters
            )
        except Question.DoesNotExist:
            question = Content.objects.get_or_404(
                channel=homepage,
                slug=pretty_slug,
                **filters
            )

        return self.get_context(question)


    def get_context_by_long_slug(self, long_slug, render_content=False):

        now = datetime.now()
        homepage = Channel.objects.get(is_homepage=True)

        if long_slug.startswith(homepage.slug) and \
                len(long_slug.split('/')) < 3 and \
                not render_content:
            slug = long_slug.split('/')[-1]
            return redirect(url_for('detail', long_slug=slug))

        filters = {
            'published': True,
            'available_at__lte': now
        }

        try:
            question = Question.objects.get(
                pretty_slug=long_slug,
                **filters
            )
        except Question.DoesNotExist:
            question = Content.objects.get_or_404(
                channel=homepage,
                slug=long_slug,
                **filters
            )

        return self.get_context(question)

    def get_context(self, question):

        labels = [question.choice_A,
                  question.choice_B,
                  question.choice_C,
                  question.choice_D,
                  question.choice_E]
        choices = [(chr(65+c), v) for c,v in list(enumerate(labels))]

        random.seed(session['user_id'])
        random.shuffle(choices)

        self.Form.answer = RadioField('Choice', choices=choices)

        form = self.Form(request.form)

        self.question = question

        context = {
            "question": question,
            "form": form
        }

        return context


    def get(self, pretty_slug, render_content=False):
        context = self.get_context_by_pretty_slug(pretty_slug, render_content)
        if not render_content and isinstance(context, collections.Callable):
            return context
        return render_template(
            self.get_template_names(),
            theme=self.question.get_themes(),
            **context
        )


    def post(self, long_slug):
        context = self.get_context_by_long_slug(long_slug)
        form = context.get('form')

        #if form.validate():
        #    comment = Comment()
        #    form.populate_obj(comment)
        #
        #    content = context.get('content')
        #    content.comments.append(comment)
        #    content.save()
        #
        #    return redirect(url_for('.detail', long_slug=long_slug))

        if form.validate():
            answer = Answer()
            form.populate_obj(answer)

            question = context.get('question')
            question.tries.append(answer)
            question.save()

            #candidate = context.get('candidate')
            #candidate.answers.append(answer)
            #candidate.save()

            return redirect(url_for('.detail', long_slug=long_slug))

        return render_template(
            self.get_template_names(),
            theme=self.question.get_themes(),
            **context
        )


class ContentFeed(MethodView):
    pass


class ChannelFeed(ContentFeed):
    pass
