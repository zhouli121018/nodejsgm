class MyRouter(object):
    def db_for_read(self, model, **hints):
        return 'localhost'

    def db_for_write(self, model, **hints):
        return 'localhost'