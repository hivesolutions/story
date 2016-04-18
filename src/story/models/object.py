#!/usr/bin/python
# -*- coding: utf-8 -*-

import appier

from . import base

class Object(base.StoryBase):

    key = appier.field(
        index = True,
        safe = True,
        immutable = True
    )

    name = appier.field(
        index = True
    )

    engine = appier.field(
        index = True,
        safe = True
    )

    file = appier.field(
        type = appier.File,
        private = True
    )

    bucket = appier.field(
        type = appier.references(
            "Bucket",
            name = "id"
        )
    )

    @classmethod
    def validate(cls):
        return super(Object, cls).validate() + [
            appier.not_null("name"),
            appier.not_empty("name")
        ]

    @classmethod
    def list_names(cls):
        return ["id", "name", "key", "engine", "bucket"]

    @classmethod
    def order_name(self):
        return ["id", -1]

    def pre_create(self):
        base.StoryBase.pre_create(self)
        self.key = self.secret()
        self.description = self.key[:8]
