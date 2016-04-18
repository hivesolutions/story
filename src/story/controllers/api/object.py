#!/usr/bin/python
# -*- coding: utf-8 -*-

import appier

import story

class ObjectApiController(appier.Controller):

    @appier.route("/api/objects", "GET", json = True)
    @appier.ensure(token = "admin")
    def list(self):
        object = appier.get_object(alias = True, find = True)
        objects = story.Object.find(map = True, **object)
        return objects

    @appier.route("/api/objects", "POST", json = True)
    @appier.ensure(token = "admin")
    def create(self):
        object = story.Object.new()
        object.save()
        object = object.reload(map = True)
        return object

    @appier.route("/api/objects/<str:key>/info", "GET", json = True)
    def info(self, key):
        object = story.Object.get(key = key, map = True)
        return object

    @appier.route("/api/objects/<str:key>", "GET", json = True)
    @appier.route("/api/objects/<str:key>/data", "GET", json = True)
    def data(self, key):
        object = story.Object.get(
            key = key,
            fields = ("file",),
            rules = False
        )
        file = object.file
        if not file: raise appier.NotFoundError(
            message = "File not found for object '%key'" % key,
            code = 404
        )
        return self.send_file(
            file.data,
            content_type = file.mime,
            etag = file.etag
        )
