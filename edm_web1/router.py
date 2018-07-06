class MyRouter(object):
    def db_for_read(self, model, **hints):
        # if model.__name__ == 'CommonVar':
        if model._meta.model_name == 'commontype':
            return 'pgsql-ms'
        if model._meta.app_label == 'other':
            return 'pgsql-ms'
        # elif model._meta.app_label in ['auth', 'admin', 'contenttypes', 'sesssions', 'django_weixin', 'tagging']:
        #     return 'default'
        return 'mm-ms'

    def db_for_write(self, model, **hints):
        if model._meta.model_name == 'commontype':
            return 'pgsql-ms'
        if model._meta.app_label == 'other':
            return 'pgsql-ms'
        # elif model._meta.app_label in ['auth', 'admin', 'contenttypes', 'sesssions', 'django_weixin', 'tagging']:
        #     return 'default'
        return 'mm-ms'
