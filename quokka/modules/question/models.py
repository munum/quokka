#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import random
from flask import url_for

from quokka.core.db import db
from quokka.core.models import Content, LongSlugged
from quokka.modules.accounts.models import User

class Answer(db.EmbeddedDocument):
    answer = db.StringField(verbose_name="Answer", required=True)
    explanation = db.StringField(verbose_name="Explanation", required=False)
    #author = db.StringField(verbose_name="Name", max_length=255, required=True)
    published = db.BooleanField(default=False)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    created_by = db.ReferenceField(User)

    def __unicode__(self):
        return "{0}-{1}...".format(self.author, self.body[:10])

    meta = {
        'indexes': ['-created_at', '-available_at'],
        'ordering': ['-created_at']
    }



class Answerable(object):
    tries = db.ListField(db.EmbeddedDocumentField(Answer), default=[])



class QuestionLongSlugged(LongSlugged):
    pretty_slug = db.StringField(required=True)

    def _create_mpath_long_slug(self):
        if isinstance(self, Content):
            self.long_slug = "/".join(
                [self.channel.long_slug, self.slug]
            )
            self.mpath = "".join([self.channel.mpath, self.slug, ','])

            self.pretty_slug = 'q-' + str(random.randint(10000, 99999))


class Question(Content, QuestionLongSlugged, Answerable):
    # URL_NAMESPACE = 'posts.detail'
    body = db.StringField(required=True)
    choice_A = db.StringField(required=True)
    choice_B = db.StringField(required=True)
    choice_C = db.StringField(required=True)
    choice_D = db.StringField(required=True)
    choice_E = db.StringField(required=True)
    correct_answer = db.StringField(choices=[chr(65+k) for k in range(0, 5)], required=True)

    published = db.BooleanField(default=True)

    def get_absolute_url(self, endpoint='question-detail'):
        if self.channel.is_homepage:
            #long_slug = self.slug
            pretty_slug = self.slug
        else:
            #long_slug = self.long_slug
            pretty_slug = self.pretty_slug

        try:
            return url_for(self.URL_NAMESPACE, pretty_slug=pretty_slug)
        except:
            return url_for(endpoint, pretty_slug=pretty_slug)

    def save(self, *args, **kwargs):

        def strip_outer_p(s):
            if s.startswith("<p>") and s.endswith("</p>"):
                res = s[3:len(s)-4]
            else:
                res = s
            return res

        self.body = strip_outer_p(self.body)
        self.choice_A = strip_outer_p(self.choice_A)
        self.choice_B = strip_outer_p(self.choice_B)
        self.choice_C = strip_outer_p(self.choice_C)
        self.choice_D = strip_outer_p(self.choice_D)
        self.choice_E = strip_outer_p(self.choice_E)

        super(Question, self).save(*args, **kwargs)


class Candidate(User):
    answers = db.ListField(
        db.EmbeddedDocumentField(Answer), default=[]
    )

