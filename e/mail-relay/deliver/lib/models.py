#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .model import model

deliver_model = model(['object',
                       ['mail_ident', 'string'],
                       ['sender', 'email'],
                       ['receiver', 'email'],
                       ['deliver_ip', 'ipv4']])

_log_model = ['object',
              ['mail_ident', 'string'],
              ['sender', 'string'],
              ['receiver', 'string'],
              ['deliver_ip', 'string'],
              ['result', ['array',
                          ['object',
                           ['deliver_time', 'datetime'],
                           ['mx_record', 'string'],
                           ['receive_ip', 'string'],
                           ['return_code', 'integer'],
                           ['return_message', 'string']]]]]

log_model = model(_log_model)

log_list_model = model(['array', _log_model])

bounce_model = model(['object',
                      ['mail_ident', 'string'],
                      ['sender', 'string'],
                      ['receiver', 'string'],
                      ['deliver_ip', 'string'],
                      ['bounce_time', 'datetime'],
                      ['bounce_result', 'boolean'],
                      ['bounce_message', 'string']])
