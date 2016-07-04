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
        type = appier.reference(
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

    def pre_save(self):
        base.StoryBase.pre_save(self)
        if not hasattr(self, "engine") or not self.engine:
            self.engine = appier.conf("ENGINE", None)
        if hasattr(self, "key") and self.key:
            self.file.guid = self.key
        if hasattr(self, "engine") and self.engine:
            self.file.engine = self.engine

    def pre_create(self):
        base.StoryBase.pre_create(self)
        self.key = self.secret()
        self.description = self.key[:8]
        self.file.guid = self.key

    @appier.link(name = "View")
    def view_url(self, absolute = False):
        return self.owner.url_for(
            "object_api.data",
            absolute = absolute,
            key = self.key
        )

    @appier.link(name = "Info")
    def info_url(self):
        return self.owner.url_for(
            "object_api.info",
            key = self.key
        )
