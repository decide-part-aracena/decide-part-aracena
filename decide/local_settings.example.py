ALLOWED_HOSTS = ["*"]

# Modules in use, commented modules that you won't use
MODULES = [
    'authentication',
    'base',
    'booth',
    '',
    'graphic',
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
    'graphic': BASEURL,
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
        'NAME': 'decide',
        'USER': 'decide',
        'PASSWORD': 'complexpassword',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}


# number of bits for the key, all auths should use the same number of bits
KEYBITS = 256
