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
        return self._handle_file(file)

    def _handle_file(self, file):
        # in case there's no file value found raises an exception
        # indicating such problem (should be properly handled)
        if not file: raise appier.NotFoundError(
            message = "File not found",
            code = 404
        )

        # verifies if the file object is "seekable" (depends on engine)
        # and if it is sets the accept ranges header indicating so
        if file.is_seekable(): self.request.set_header(
            "Accept-Ranges",
            "bytes"
        )

        # handles the range request from the client so that if a chunk
        # was requested that simple range is retrieved
        is_partial, range = self._handle_range(file)

        # runs the send file operation taking into account that the a
        # generator is going to be used for the sending operation
        return self.send_file(
            self._file_generator(file, range = range),
            content_type = file.mime,
            etag = None if is_partial else file.etag
        )

    def _handle_range(self, file):
        # retrieves the value of the range header and uses
        # such value to try to determine if the current request
        # is a partial one and if the current file is seekable
        # if that's not the case returns immediately as not partial
        range_s = self.request.get_header("Range", None)
        is_partial = True if range_s else False
        is_partial = is_partial and file.is_seekable()
        if not is_partial: return is_partial, None

        # retrieves the size/length of the current file and then
        # construct the proper range tuple using the range header
        file_size = len(file)
        range_s = range_s[6:]
        start_s, end_s = range_s.split("-", 1)
        start = int(start_s) if start_s else 0
        end = int(end_s) if end_s else file_size - 1
        range = (start, end)

        # updates the values of the current request with the new code
        # for partial data and the content range associated
        self.request.set_code(206)
        self.request.set_header(
            "Content-Range",
            "bytes %d-%d/%d" % (range[0], range[1], file_size)
        )

        # returns the final is partial (flag) and range tuple to the
        # caller method to be used as the base values for generator
        return is_partial, range

    def _file_generator(self, file, range = None, size = 40960):
        try:
            file_size = len(file)
            if range: data_size = range[1] - range[0] + 1
            else: data_size = file_size
            yield data_size
            if range: file.seek(range[0])
            while True:
                read_size = data_size if size > data_size else size
                data = file.read(read_size)
                if not data: break
                yield data
                data_size -= len(data)
                if data_size > 0: continue
                break
        finally:
            file.cleanup()
