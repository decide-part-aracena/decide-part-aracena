from dotenv import dotenv_values

secrets = dotenv_values(".secrets")

ALLOWED_HOSTS = ["*"]

# Modules in use, commented modules that you won't use
MODULES = [
    'authentication',
    'base',
    'booth',
    'census',
    'mixnet',
    'postproc',
    'store',
    'visualizer',
    'voting',
    'users',
]
BASEURL = 'http://localhost:8000'
APIS = {
    'authentication': BASEURL,
    'base': BASEURL,
    'booth': BASEURL,
    'census': BASEURL,
    'mixnet': BASEURL,
    'postproc': BASEURL,
    'store': BASEURL,
    'visualizer': BASEURL,
    'voting': BASEURL,
    'users': BASEURL,
}



DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'decidedb',
        'USER': 'decideusr',
        'PASSWORD':'complexpassword',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# number of bits for the key, all auths should use the same number of bits
KEYBITS = 256


#Email SMTP
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp-mail.outlook.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'decide.part.aracena@outlook.com'
EMAIL_HOST_PASSWORD = secrets['EMAIL_HOST_PASSWORD']