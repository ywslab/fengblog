# -*- coding: utf-8 -*-
import os

from newblog import create_app
import datetime

# Create an application instance that web servers can use. We store it as
# "application" (the wsgi default) and also the much shorter and convenient
# "app".
application = app = create_app('production')


@app.context_processor
def template_extras():
    """
    上下文处理装饰器，返回的字典的键可以在上下文中使用
    :return:
    """
    return {'enumerate': enumerate, 'len': len, 'datetime': datetime}
