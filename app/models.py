# -*- coding: utf-8 -*-

from app import db

class Poker(db.Model):
    id = db.Column(db.Integer, db.Sequence('seq_poker_id', start=1, increment=1), primary_key=True)
    teamId = db.Column(db.String(64), primary_key=True)
    isComplete = db.Column(db.Boolean(), default=False)

    def __repr__(self):
        return '<Poker %r>' % (self.groupId)

