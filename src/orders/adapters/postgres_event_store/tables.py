import sqlalchemy as sql


class AggregateModel(sql.Base):
    __tablename__ = "aggregates"

    uuid = sql.Column(sql.VARCHAR(36), primary_key=True)
    version = sql.Column(sql.Integer, default=1)


class EventModel(sql.Base):
    __tablename__ = "events"

    uuid = sql.Column(sql.VARCHAR(36), primary_key=True)
    aggregate_uuid = sql.Column(sql.VARCHAR(36), sql.ForeignKey("aggregates.uuid"))
    name = sql.Column(sql.VARCHAR(50))
    data = sql.Column(sql.JSON)

    aggregate = sql.relationship(AggregateModel, uselist=False, backref="events")
