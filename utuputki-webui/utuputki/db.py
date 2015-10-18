# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text, Boolean, UniqueConstraint
from utils import utc_now

Base = declarative_base()

_engine = None
_session = sessionmaker()


USERLEVELS = {
    'none': 0,
    'user': 10,
    'admin': 20,
}

MEDIATYPES = {
    'video': 0,
    'audio': 1
}

MEDIASTATUS = {
    'not_started': 0,
    'sourced': 1,
    'cached': 2,
    'finished': 3
}


class Event(Base):
    __tablename__ = "event"
    id = Column(Integer, primary_key=True)
    name = Column(String(32))
    visible = Column(Boolean)


class Player(Base):
    __tablename__ = "player"
    id = Column(Integer, primary_key=True)
    token = Column(String(16), unique=True)
    event = Column(ForeignKey('event.id'))
    name = Column(String(32))

    def serialize(self):
        return {
            'token': self.token,
            'name': self.name
        }


class SourceQueueItem(Base):
    __tablename__ = "sourcequeueitem"
    id = Column(Integer, primary_key=True)
    queue = Column(ForeignKey('sourcequeue.id'))
    media = Column(ForeignKey('media.id'))

    def serialize(self):
        s = db_session()
        media = [media.serialize() for media in s.query(Media).filter_by(id=self.media).all()],
        s.close()
        return {
            'id': self.id,
            'media_id': self.media,
            'media': media
        }


class SourceQueue(Base):
    __tablename__ = "sourcequeue"
    id = Column(Integer, primary_key=True)
    user = Column(ForeignKey('user.id'))
    target = Column(ForeignKey('player.id'))
    created_at = Column(DateTime(timezone=True), default=utc_now())

    # Allow only one source queue per user per target player
    __table_args__ = (
        UniqueConstraint('user', 'target', name='_user_target_uc'),
    )

    def serialize(self):
        s = db_session()
        items = [item.serialize() for item in s.query(SourceQueueItem).filter_by(queue=self.id).all()],
        s.close()
        return {
            'id': self.id,
            'user': self.user,
            'name': self.name,
            'created_at': self.created_at,
            'items': items
        }


class Source(Base):
    __tablename__ = "source"
    id = Column(Integer, primary_key=True)
    hash = Column(String(64))
    youtube_hash = Column(String(32), nullable=True)
    fetch_url = Column(String(512), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now())
    title = Column(String(100), nullable=True)

    def serialize(self):
        return {
            'id': self.id,
            'youtube_hash': self.youtube_hash,
            'fetch_url': self.fetch_url,
            'created_at': self.created_at,
            'title': self.title
        }


class Cache(Base):
    __tablename__ = "cache"
    id = Column(Integer, primary_key=True)
    source = Column(ForeignKey('source.id'))
    file_path = Column(String(512))
    file_ext = Column(String(4))
    mime_type = Column(String(32))
    size_bytes = Column(Integer, default=0)
    media_type = Column(Integer, default=0)
    length_seconds = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=utc_now())

    def serialize(self):
        return {
            'id': self.id,
            'file_ext': self.file_ext,
            'mime_type': self.mime_type,
            'size_bytes': self.size_bytes,
            'media_type': self.media_type,
            'length_seconds': self.length_seconds,
            'created_at': self.created_at,
        }


class Media(Base):
    __tablename__ = "media"
    id = Column(Integer, primary_key=True)
    status = Column(Integer, default=0)
    step_progress = Column(Integer, default=0)
    cache = Column(ForeignKey('cache.id'), nullable=True, default=None)
    source = Column(ForeignKey('source.id'), nullable=True, default=None)
    user = Column(ForeignKey('user.id'))

    def serialize(self):
        s = db_session()
        cache_entry = s.query(Cache).filter_by(id=self.cache).one().serialize() if self.cache else None,
        source_entry = s.query(Source).filter_by(id=self.source).one().serialize() if self.source else None,
        s.close()
        return {
            'id': self.id,
            'type': self.type,
            'status': self.status,
            'cache_id': self.cache,
            'cache': cache_entry,
            'source_id': self.source,
            'source': source_entry,
            'user_id': self.user
        }


class Setting(Base):
    __tablename__ = "setting"
    id = Column(Integer, primary_key=True)
    user = Column(ForeignKey('user.id'))
    key = Column(String(32))
    value = Column(String(32))
    type = Column(Integer)
    max = Column(Integer)
    min = Column(Integer)

    def serialize(self):
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'type': self.type,
            'max': self.max,
            'min': self.min
        }


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    username = Column(String(32), unique=True)
    password = Column(String(255))
    nickname = Column(String(32))
    email = Column(String(128))
    level = Column(Integer, default=USERLEVELS['none'])

    def serialize(self):
        s = db_session()
        settings = [setting.serialize() for setting in s.query(Setting).filter_by(user=self.id).all()],
        queues = [queue.serialize() for queue in s.query(SourceQueue).filter_by(user=self.id).all()],
        s.close()
        return {
            'id': self.id,
            'username': self.username,
            'nickname': self.nickname,
            'email': self.email,
            'level': self.level,
            'settings': settings,
            'queues': queues
        }


class Session(Base):
    __tablename__ = "session"
    key = Column(String(32), primary_key=True)
    user = Column(ForeignKey('user.id'))
    start = Column(DateTime(timezone=True), default=utc_now())


def db_init(engine_str):
    _engine = create_engine(engine_str)
    _session.configure(bind=_engine)
    Base.metadata.create_all(_engine)


def db_session():
    return _session()

