import random

from django.conf import settings
from django.db import models

import praw


class KittensManager(models.Manager):
    def get_random(self):
        """Get a kitten, either from the db, or a new one.
        """
        num_kittens = self.count()
        if random.random() > (num_kittens / (num_kittens + 100.0)):
            return self._rand_inst()
        else:
            return self.create_new()

    def _rand_inst(self):
        ids = self.values_list('id', flat=True)
        rand_id = random.choice(ids)
        return self.get(id=rand_id)

    def create_new(self):
        """Create a new kitten by querying /r/awww.
        """
        kitten = reddit_kitten()
        if self.filter(url=kitten.url).exists():
            return self.get(url=kitten.url)
        else:
            kitten_obj = self.create(
                url=kitten.url,
                thumbnail=kitten.thumbnail,
                title=kitten.title,
            )
            return kitten_obj


class Kittens(models.Model):
    url = models.CharField(max_length=200, unique=True)
    thumbnail = models.CharField(max_length=200)
    title = models.CharField(max_length=200, unique=True)
    votes_up = models.PositiveIntegerField(default=0)
    votes_down = models.PositiveIntegerField(default=0)
    added = models.DateTimeField(auto_now_add=True)

    objects = KittensManager()


def reddit_kitten():
    reddit_api = praw.Reddit(user_agent=settings.REDDIT_USER_AGENT)
    aww_subreddit = reddit_api.get_subreddit("aww")
    kitten_results = aww_subreddit.search("kitten", sort="new", limit=100)
    kittens = [k for k in kitten_results if k.thumbnail != 'self']
    return random.choice(kittens)