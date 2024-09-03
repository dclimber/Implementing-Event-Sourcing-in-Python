import sqlalchemy as sql
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class AggregateModel(Base):
    __tablename__ = "aggregates"

    uuid = sql.Column(sql.String(36), primary_key=True)
    version = sql.Column(sql.Integer, default=1)


class EventModel(Base):
    __tablename__ = "events"

    uuid = sql.Column(sql.String(36), primary_key=True)
    aggregate_uuid = sql.Column(sql.String(36), sql.ForeignKey("aggregates.uuid"))
    name = sql.Column(sql.String(50))
    data = sql.Column(sql.JSON)

    aggregate = sql.orm.relationship(AggregateModel, backref="events")
