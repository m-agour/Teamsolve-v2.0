from website import app, socketio
import os

port = int(os.environ.get('PORT', 5000))

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True, port=5000)
    # socketio.run(app)

