import os

import config.secrets as secrets

MODE = os.environ.get('APP_MODE')
DEBUG = MODE not in ['PROD', 'STAGE']

if DEBUG:
    import config.secrets_local as secrets
else:
    import config.secrets as secrets


# localhost = '127.0.0.1'
localhost = 'mysql_workshop'
# db_name = 'sdg_workshop'
db_name = 'workshop'
DATABASE_URI = 'mysql://ffuser:{}@{}/{}'.format(secrets.DATABASE_PASSWORD, localhost, db_name)
