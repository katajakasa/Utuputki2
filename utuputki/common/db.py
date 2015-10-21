# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text, Boolean, UniqueConstraint
from datetime import datetime

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
    'fetching_metadata': 1,
    'downloading': 2,
    'finished': 3,
    'error': 4
}


class Event(Base):
    __tablename__ = "event"
    id = Column(Integer, primary_key=True)
    name = Column(String(32))
    visible = Column(Boolean)

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'visible': self.visible
        }


class Player(Base):
    __tablename__ = "player"
    id = Column(Integer, primary_key=True)
    token = Column(String(16), unique=True)
    event = Column(ForeignKey('event.id'))
    name = Column(String(32))

    def serialize(self, show_token=False):
        return {
            'id': self.id,
            'token': self.token if show_token else None,
            'name': self.name,
            'event_id': self.event,
        }


class SourceQueue(Base):
    __tablename__ = "sourcequeue"
    id = Column(Integer, primary_key=True)
    user = Column(ForeignKey('user.id'))
    target = Column(ForeignKey('player.id'))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow())

    # Allow only one source queue per user per target player
    __table_args__ = (
        UniqueConstraint('user', 'target', name='_user_target_uc'),
    )

    def serialize(self):
        s = db_session()
        items = [media.serialize() for media in s.query(Media).filter_by(queue=self.id).all()],
        s.close()
        return {
            'id': self.id,
            'user': self.user,
            'target': self.target,
            'items': items
        }


class Source(Base):
    __tablename__ = "source"
    id = Column(Integer, primary_key=True)
    hash = Column(String(64), default='')
    file_path = Column(String(512), default='')
    file_ext = Column(String(4))
    mime_type = Column(String(32))
    size_bytes = Column(Integer, default=0)
    media_type = Column(Integer, default=0)
    youtube_hash = Column(String(32), default='')
    other_url = Column(String(512), default='')
    length_seconds = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow())
    title = Column(String(100), default='')
    description = Column(Text, default='')
    status = Column(Integer, default=0)
    message = Column(String(64), default='')
    video_codec = Column(String(16), default='')
    video_bitrate = Column(Integer, default=0)
    video_w = Column(Integer, default=0)
    video_h = Column(Integer, default=0)
    audio_codec = Column(String(16), default='')
    audio_bitrate = Column(Integer, default=0)

    def serialize(self):
        return {
            'id': self.id,
            'youtube_hash': self.youtube_hash,
            'other_url': self.other_url,
            'status': self.status,
            'title': self.title,
            'description': self.description,
            'file_ext': self.file_ext,
            'mime_type': self.mime_type,
            'size_bytes': self.size_bytes,
            'media_type': self.media_type,
            'length_seconds': self.length_seconds,
            'message': self.message,
            'audio': {
                'codec': self.audio_codec,
                'bitrate': self.audio_bitrate
            },
            'video': {
                'codec': self.video_codec,
                'bitrate': self.video_bitrate,
                'width': self.video_w,
                'height': self.video_h
            }
        }


class Media(Base):
    __tablename__ = "media"
    id = Column(Integer, primary_key=True)
    source = Column(ForeignKey('source.id'), nullable=True, default=None)
    user = Column(ForeignKey('user.id'))
    queue = Column(ForeignKey('sourcequeue.id'))

    def serialize(self):
        s = db_session()
        source_entry = s.query(Source).filter_by(id=self.source).one().serialize() if self.source else None,
        s.close()
        return {
            'id': self.id,
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
        return {
            'id': self.id,
            'username': self.username,
            'nickname': self.nickname,
            'email': self.email,
            'level': self.level
        }


class Session(Base):
    __tablename__ = "session"
    key = Column(String(32), primary_key=True)
    user = Column(ForeignKey('user.id'))
    start = Column(DateTime(timezone=True), default=datetime.utcnow())


def db_init(engine_str):
    _engine = create_engine(engine_str)
    _session.configure(bind=_engine)
    Base.metadata.create_all(_engine)


def db_session():
    return _session()

