# coding=utf-8

"""
replace `werkzeug.formparser.MultiPartParser` so that it will not decode form data
"""

import werkzeug.formparser
from werkzeug.formparser import FileStorage, _begin_file, _begin_form, _cont, _end


class MultiPartParserWithoutDecode(werkzeug.formparser.MultiPartParser):
    def parse_parts(self, file, boundary, content_length):
        """Generate ``('file', (name, val))`` and
        ``('form', (name, val))`` parts.
        """
        in_memory = 0

        for ellt, ell in self.parse_lines(file, boundary, content_length):
            if ellt == _begin_file:
                headers, name, filename = ell
                is_file = True
                guard_memory = False
                filename, container = self.start_file_streaming(
                    filename, headers, content_length)
                _write = container.write

            elif ellt == _begin_form:
                headers, name = ell
                is_file = False
                container = []
                _write = container.append
                guard_memory = self.max_form_memory_size is not None

            elif ellt == _cont:
                _write(ell)
                # if we write into memory and there is a memory size limit we
                # count the number of bytes in memory and raise an exception if
                # there is too much data in memory.
                if guard_memory:
                    in_memory += len(ell)
                    if in_memory > self.max_form_memory_size:
                        self.in_memory_threshold_reached(in_memory)

            elif ellt == _end:
                if is_file:
                    container.seek(0)
                    yield ('file',
                           (name, FileStorage(container, filename, name,
                                              headers=headers)))
                else:
                    yield ('form',
                           (name, b''.join(container)))


werkzeug.formparser.MultiPartParser = MultiPartParserWithoutDecode
