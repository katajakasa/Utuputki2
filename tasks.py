from invoke import Collection, ctask as task
import os
from rjsmin import jsmin
from glob import glob


def find_js_files(directory):
    return glob('{}/*/*.js'.format(directory)) + glob('{}/*.js'.format(directory))


@task
def clean(ctx):
    try:
        os.remove(ctx.output)
    except OSError:
        pass


@task
def build(ctx):
    with open(ctx.output, 'wb') as out_fp:
        for f in find_js_files(ctx.source):
            with open(f, 'rb') as in_fp:
                out_fp.write(jsmin(in_fp.read()))


ns = Collection(clean, build)
ns.configure({
    'source': "utuputki/webui/public/static/custom",
    'output': "utuputki/webui/public/static/custom/app.min.js",
})
