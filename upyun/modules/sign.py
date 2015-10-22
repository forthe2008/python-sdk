# -*- coding: utf-8 -*-

import hashlib
import base64
import json

from .compat import b, PY3, builtin_str, bytes, str
from .exception import UpYunClientException

DEFAULT_CHUNKSIZE = 8192

def make_rest_signature(bucket, username, password,
                                method, uri, date, length):
    if method:
        signstr = '&'.join([method, uri, date, str(length), password])
        signature = hashlib.md5(b(signstr)).hexdigest()
        return "UpYun %s:%s" % (username, signature)

    else:
        signstr = '&'.join([uri, bucket, date, password])
        signature = hashlib.md5(b(signstr)).hexdigest()
        return "UpYun %s:%s:%s" % (bucket, username, signature)

def make_content_md5(value, chunksize=DEFAULT_CHUNKSIZE):
    if hasattr(value, 'fileno'):
        md5 = hashlib.md5()
        for chunk in iter(lambda: value.read(chunksize), b''):
            md5.update(chunk)
        value.seek(0)
        return md5.hexdigest()
    elif isinstance(value, bytes) or (not PY3 and
                                isinstance(value, builtin_str)):
        return hashlib.md5(value).hexdigest()
    else:
        raise UpYunClientException('object type error')

def decode_msg(msg):
    if isinstance(msg, bytes):
        msg = msg.decode('utf-8')
    return msg

def encode_msg(msg):
    if isinstance(msg, str):
        msg = msg.encode('utf-8')
    return msg

def make_policy(data):
    if type(data) == dict:
        policy = json.dumps(data)
        policy = base64.b64encode(b(policy))
        return decode_msg(policy)
    else:
        return None

def make_signature(data, secret):
    if type(data) == dict:
        signature = ''
        list_meta = sorted(data.items(), key=lambda d:d[0])
        for k, v in list_meta:
            signature = signature + k + str(v)
        signature += secret
        return make_content_md5(signature)
    else:
        return None
