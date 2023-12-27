import os
from django.conf import settings
from django.core.management.base import BaseCommand
from base.methods import (
    dicts_to_models,
    get_account_model,
    get_feed_model,
    get_json_dicts,
)

class Command(BaseCommand):
    help = "Sync essential models with data from JSON files."

    def handle(self, *args, **options):
        data_directory = os.path.join(settings.BASE_DIR, "data")
        # process accounts
        accounts_json = os.path.join(data_directory, "accounts.json")
        # check if file exists
        if os.path.isfile(accounts_json):
            # get account model
            AccountModel = get_account_model()
            # get json dicts
            account_dicts = get_json_dicts(accounts_json, key="accounts")
            # update model objects
            dicts_to_models(account_dicts, AccountModel, object_id="uid")
            self.stdout.write(self.style.SUCCESS('Successfully updated accounts to "%s" model based on data from "%s".' % (AccountModel.__name__, accounts_json)))
        # process feeds
        feeds_json = os.path.join(data_directory, "feeds.json")
        # check if file exists
        if os.path.isfile(feeds_json):
            # get feed model
            FeedModel = get_feed_model()
            # get json dicts
            feed_dicts = get_json_dicts(feeds_json, key="feeds")
            # update model objects
            dicts_to_models(feed_dicts, FeedModel, object_id="uid")
            self.stdout.write(self.style.SUCCESS('Successfully updated feeds to "%s" model based on data from "%s".' % (FeedModel.__name__, feeds_json)))
