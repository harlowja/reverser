# vim: tabstop=4 shiftwidth=4 softtabstop=4

#    Copyright (C) 2014 Yahoo! Inc. All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import os


class ReverseFile(object):
    """Reads a file in reverse."""

    BUFFER_SIZE = 512

    def __init__(self, filename):
        self._handle = open(filename, 'rb')
        self._filename = filename
        self._size = os.path.getsize(filename)
        self._left = self._size
        self._closed = False

    def _buffer(self):
        if self._closed:
            raise ValueError('I/O operation on closed file')
        if self._left <= 0:
            return ""
        end_pos = self._left
        start_pos = max(0, end_pos - self.BUFFER_SIZE)
        self._handle.seek(start_pos, 0)
        buf = self._handle.read(end_pos - start_pos)
        self._left -= self.BUFFER_SIZE
        return buf

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    @property
    def size(self):
        return self._size

    @property
    def name(self):
        return self._filename

    def close(self):
        self._handle.close()
        self._closed = True

    def read(self, size=None):
        """Yields back segments of the given size."""
        if size is None:
            size = self._size
        content = self._buffer()
        if not content:
            yield ''
        else:
            running = True
            while running:
                finished = False
                while len(content) < size and not finished:
                    tmp_content = self._buffer()
                    if not tmp_content:
                        finished = True
                    else:
                        content = tmp_content + content
                if finished:
                    yield content
                    running = False
                else:
                    rest = content[0:-size]
                    content = content[-size:]
                    yield content
                    content = rest

    def readlines(self,
                  include_newline=False, include_last_newline=True,
                  linesep=os.linesep):
        """Yields back lines."""
        content = self._buffer()
        count = 0
        while True:
            idx = content.rfind(linesep)
            while idx == -1:
                tmp_content = self._buffer()
                if not tmp_content:
                    break
                content = tmp_content + content
                idx = content.rfind(linesep)
            if idx == -1:
                yield content
                break
            else:
                rest = content[0:idx]
                if not include_newline:
                    line = content[idx + 1:]
                else:
                    line = content[idx:]
                skip = False
                if not include_last_newline and count == 0:
                    if include_newline and line == linesep:
                        skip = True
                    if not include_newline and line == "":
                        skip = True
                if not skip:
                    yield line
                count += 1
                content = rest
