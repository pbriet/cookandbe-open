import re

from django.db                  import models
from django.db.models.signals   import post_save, post_delete
from django.dispatch            import receiver

from common.string              import unaccent

class NamedModel(object):
    def __str__(self):
        return self.name

class AutoUrlKeyModel(models.Model):
    """
    Adds a url_key field which contains a URL-compatible string,
    optimized for SEO, built from a field of the model (usually : the name)
    """
    class Meta:
        abstract = True

    # Function that returns the string from which the url_key will be built
    URL_KEY_FROM_FCN = lambda x: x.name.strip()

    # Field containing the string to put in the url instead of an id
    url_key             = models.CharField(max_length=500, blank=True, db_index=True)

    @classmethod
    def _build_base_key(cls, text):
        # Removing accents
        res = unaccent(text)
        # Only keeping spaces and alphanumerics
        res = re.sub(r'[^a-z0-9 \'\-]+', '', res)
        # Replacing spaces by dashes
        res = re.sub(r'[ \']+', '-', res.strip())
        res = res[:450] # Limiting the string part to 450 chars
        return res

    def build_key(self, text):
        """
        From a text, returns a URL-compatible string
        """
        res = self._build_base_key(text)
        # Adding unique id (unicity guaranteed)
        res += '-%s' % self.pk
        return res

    def save(self, *args, **kargs):
        assert hasattr(self.__class__, '_AUTO_URL_KEY_ENABLED'), "please apply enable_auto_url_key decorator on class %s" % self.__class__
        super().save(*args, **kargs)

    def _update_url_key(self):
        url_key = self.build_key(self.URL_KEY_FROM_FCN())

        if url_key == self.url_key:
            # No modification
            return
        self.url_key = url_key
        self.save()

    # Storing post_save event binding functions
    _BINDS = []

    @classmethod
    def _enable_auto_url_key(cls):
        cls._AUTO_URL_KEY_ENABLED = True
        @receiver(post_save, sender=cls)
        def post_profile_save(sender, instance, **kwargs):
            instance._update_url_key()

        AutoUrlKeyModel._BINDS.append(post_profile_save)

def enable_auto_url_key(cls):
    """
    Class decorator that calls enable_auto_url_key
    """
    assert issubclass(cls, AutoUrlKeyModel), "please make %s inherit from AutoUrlKeyModel" % cls
    cls._enable_auto_url_key()
    return cls


def auto_delete_file(field_name):
    def decorator(cls):
        """
        Class decorator that deletes a file contained in a field (e.g. models.ImageField), when
        the object is deleted. By default, the file stays in the storage
        """

        @receiver(post_delete, sender=cls)
        def file_cleanup(sender, instance=None, **kargs):
            getattr(instance, field_name).delete(save=False)
        if not hasattr(cls, "__AUTO_DELETE_EVENTS"):
            cls.__AUTO_DELETE_EVENTS = []
        cls.__AUTO_DELETE_EVENTS.append(file_cleanup) # For memory issues
        return cls
    return decorator

def reload_object(obj):
    """
    Reloads an object from the database
    """
    new_obj = obj.__class__.objects.get(pk=obj.pk)
    obj.__dict__ = new_obj.__dict__

def get_field_validators(model_cls, field_name):
    """
    Returns the list of validators from a model class and a field name
    """
    return model_cls._meta.get_field(field_name).validators