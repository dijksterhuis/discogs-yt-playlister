from main import app as application
import os

if __name__ == '__main__':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    application.run(host='0.0.0.0',debug=True)
