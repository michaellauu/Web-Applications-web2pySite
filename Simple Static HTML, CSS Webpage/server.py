from bottle import get, route, run, template, view, static_file, debug
debug(True)

# Our webpage
@get('/')
def news():
    return template('news_template')

# Let's add some code to serve jpg images from our static images directory.
@route('/images/<filename:re:.*\.jpg>')
def serve_image(filename):
    return static_file(filename, root='images', mimetype='image/jpg')

# Let's add some code to serve png images from our static images directory.
@route('/images/<filename:re:.*\.png>')
def serve_image(filename):
    return static_file(filename, root='images', mimetype='image/png')

# Code for serving css stylesheets from /css directory.
@route('/css/<filename:re:.*.css>')
def serve_css(filename):
    return static_file(filename, root='css', mimetype='text/css')


run(reloader=True, host='localhost', port=8080)

