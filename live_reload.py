from livereload import Server, shell
from sasehack.__main__ import app

app.debug = True
server = Server(app.wsgi_app)

# run a shell command
server.watch('*.py')
server.serve(host='127.0.0.1', port=8080)
