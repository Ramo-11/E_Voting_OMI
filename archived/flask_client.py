from routes import routes as routes_

from flask import Flask

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'mysecretkey'
app.register_blueprint(routes_)

if __name__ == '__main__':
    app.run(port=3000, debug=True)
