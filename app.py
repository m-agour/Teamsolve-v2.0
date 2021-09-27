from website import app, socketio
import os

port = int(os.environ.get('PORT', 5000))

if __name__ == '__main__':
    print(port)
    socketio.run(app, host='0.0.0.0', debug=True, port=port)
    # socketio.run(app)

