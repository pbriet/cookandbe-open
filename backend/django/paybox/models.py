from django.core.validators     import MaxValueValidator, MinValueValidator
from django.db                  import models

from common.date                import today

from paybox                     import Level

from user_mgr.models            import User

class Subscription(models.Model):
    """
    User subscription : premium, gold, from which date to which date
    """
    level               = models.IntegerField(validators=[MinValueValidator(Level.MIN + 1), MaxValueValidator(Level.MAX)])
    user                = models.ForeignKey(User, models.CASCADE, related_name="subscriptions")
    start_date          = models.DateField()
    end_date            = models.DateField()
    nb_months           = models.IntegerField(default=0)
    nb_days             = models.IntegerField(default=0)
    trial_period_end    = models.DateField()  # Trial period AFTER payment. Update 25/05/15 : there is no such period anymore
    total_amount        = models.IntegerField()  # In cents
    enabled             = models.BooleanField(default=False)
    cancelled           = models.BooleanField(default=False)
    discount            = models.IntegerField(null=True, validators=[MinValueValidator(0), MaxValueValidator(75)])  # In percentage

    @property
    def total_days(self):
        return (self.end_date - self.start_date).days

    def can_be_resiliated(self):
        return today() <= self.trial_period_end

    def get_transaction_refs(self):
        return ", ".join([t.ref for t in self.transactions.all()])

class Transaction(models.Model):
    """
    Payment transaction in progress / concluded
    """
    subscription        = models.ForeignKey(Subscription, models.CASCADE, related_name="transactions")
    created_at          = models.DateTimeField(auto_now_add=True)
    ref                 = models.CharField(max_length = 128, unique=True) # Given by us
    transaction_id      = models.IntegerField(null=True) # Provided by the bank
    payment_type        = models.CharField(max_length = 30, null=True) # Provided by the bank
    price               = models.IntegerField() # in cents/euros
    ip                  = models.CharField(max_length = 50)
    authorization_code  = models.CharField(max_length = 100, null=True)
    concluded_at        = models.DateTimeField(null=True, blank=True)  # When the bank calls "payment_validated"
    error_code          = models.IntegerField(null=True)
    status              = models.IntegerField()

    STATUS_STARTED      = 0 # The user has clicked on pay, and will therefore be redirected on the bank
    STATUS_CANCELLED    = 1 # Cancelled by the user
    STATUS_REFUSED      = 2 # Refused by the bank
    STATUS_ERROR        = 3 # Something wrong happened
    STATUS_POST_CANCEL  = 4 # The bank refused the payment in some way, after it was once accepted (should not happen...)
    STATUS_WRONG_AMOUNT = 5 # The amount paid wasn't the one expected !

    STATUS_ACCEPTED     = 10 # The payment was accepted (but the info comes from the user itself, be careful)
    STATUS_CONFIRMED    = 11 # Payment validated by the bank


class GlobalSpecialOffer(models.Model):
    start_date = models.DateTimeField(null=False)
    end_date   = models.DateTimeField(null=False)
    discount   = models.IntegerField() # In percentage
    level      = models.IntegerField(null=True, blank=True) # If None, applied to all levels


class UserSpecialOffer(models.Model):
    """
    Special offer given to a user
    """
    user                = models.ForeignKey(User, models.CASCADE, related_name="special_offers")
    discount            = models.IntegerField() # In percentage
    until               = models.DateTimeField(null=False)