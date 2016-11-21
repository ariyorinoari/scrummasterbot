from app import db

class Poker(db.Model):
    id = db.Column(db.Integer, db.Sequence('seq_poker_id', start=1, increment=1), primary_key=True)
    userId = db.Column(db.String(32), primary_key=True)
    vote = db.Column(db.String(32))

    def __repr__(self):
        return '<User %r>' % (self.userId)

