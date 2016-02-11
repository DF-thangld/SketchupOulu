from flipflop import WSGIServer
from run import app

if __name__ == '__main__':
    WSGIServer(app).run()