from website import app, socketio
import os

port = int(os.environ.get('PORT', 5000))

if __name__ == '__main__':
    socketio.run(app, host='127.0.0.1', debug=True, port=port)
    # socketio.run(app)

