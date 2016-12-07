#-*- coding: utf-8 -*-

from flask_sqlalchemy import SQLAlchemy

import app

db = SQLAlchemy(app)

class PlanningPokerResult(db.Model):
    id = db.Column(db.Integer, Sequence('planning_poker_id_seq'), primary_key=True)
    sourceId = db.Column(db.String(64))
    times = db.Column(db.String(16))


