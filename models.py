from sqlalchemy import Boolean, Column, Date, ForeignKeyConstraint, Identity, Integer, PrimaryKeyConstraint, String, \
    Table, Text, text, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()
metadata = Base.metadata


class Genre(Base):
    __tablename__ = 'genre'
    __table_args__ = (
        PrimaryKeyConstraint('genre_id', name='genre_pkey'),
    )

    genre_id = Column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False,
                                        cache=1))
    name = Column(String(50), nullable=False)

    # note = relationship('Note', secondary='note_genre', back_populates='genre')


class Type(Base):
    __tablename__ = 'type'
    __table_args__ = (
        PrimaryKeyConstraint('type_id', name='type_pkey'),
    )

    type_id = Column(Integer,
                     Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1))
    name = Column(String(50), nullable=False)

    # note = relationship('Note', secondary='note_type', back_populates='type')


t_friend_request = Table(
    'friend_request', metadata,
    Column('user_id1', ForeignKey('user.user_id'), nullable=False),
    Column('user_id2', ForeignKey('user.user_id'), nullable=False),
    ForeignKeyConstraint(['user_id1'], ['user.user_id'], name='fk_user_id1'),
    ForeignKeyConstraint(['user_id2'], ['user.user_id'], name='fk_user_id2')
)

t_friends = Table(
    'friends', metadata,
    Column('user_id1', ForeignKey('user.user_id'), nullable=False),
    Column('user_id2', ForeignKey('user.user_id'), nullable=False),
    ForeignKeyConstraint(['user_id1'], ['user.user_id'], name='fk_user_id1'),
    ForeignKeyConstraint(['user_id2'], ['user.user_id'], name='fk_user_id2')
)


class User(Base):
    __tablename__ = 'user'
    __table_args__ = (
        PrimaryKeyConstraint('user_id', name='user_pkey'),
    )

    user_id = Column(Integer,
                     Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1))
    login = Column(String(20), nullable=False)
    password = Column(String(20), nullable=False)
    nickname = Column(String(20), nullable=False)

    friend_requested = relationship('User', secondary='friend_request',
                                    primaryjoin=(t_friend_request.c.user_id1 == user_id),
                                    secondaryjoin=(t_friend_request.c.user_id2 == user_id),
                                    back_populates='friend_requested')
    friends = relationship('User', secondary='friends',
                           primaryjoin=(t_friends.c.user_id1 == user_id),
                           secondaryjoin=(t_friends.c.user_id2 == user_id),
                           back_populates='friends')

    note = relationship('Note', backref='user')
    comment = relationship('Comment', backref='user')

    def befriend(self, friend):
        if friend in self.friend_requested:
            self.friend_requested.remove(friend)
        if self in friend.friend_requested:
            friend.friend_requested.remove(self)
        if friend not in self.friends:
            self.friends.append(friend)
            friend.friends.append(self)

    def unfriend(self, friend):
        if friend in self.friends:
            self.friends.remove(friend)
            friend.friends.remove(self)

    # Flask-Login Support
    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return str(self.user_id)

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False


t_note_genre = Table(
    'note_genre', metadata,
    Column('note_id', ForeignKey('note.note_id'), nullable=False),
    Column('genre_id', ForeignKey('genre.genre_id'), nullable=False),
    ForeignKeyConstraint(['genre_id'], ['genre.genre_id'], name='fk_genre_id'),
    ForeignKeyConstraint(['note_id'], ['note.note_id'], name='fk_note_id')
)

t_note_type = Table(
    'note_type', metadata,
    Column('note_id', ForeignKey('note.note_id'), nullable=False),
    Column('type_id', ForeignKey('type.type_id'), nullable=False),
    ForeignKeyConstraint(['note_id'], ['note.note_id'], name='fk_note_id'),
    ForeignKeyConstraint(['type_id'], ['type.type_id'], name='fk_type_id')
)


class Note(Base):
    __tablename__ = 'note'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['user.user_id'], name='fk_user_id'),
        PrimaryKeyConstraint('note_id', name='note_pkey')
    )

    note_id = Column(Integer,
                     Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1))
    user_id = Column(ForeignKey('user.user_id'), nullable=False)
    name = Column(String(100), nullable=False)
    open = Column(Boolean, nullable=False, server_default=text('true'))
    date = Column(Date, nullable=False)
    score = Column(Integer)
    text = Column(Text)

    genre = relationship('Genre', secondary='note_genre', backref='note')
    # user = relationship('User', backref='note')
    type = relationship('Type', secondary='note_type', backref='note')
    comment = relationship('Comment', backref='note')


class Comment(Base):
    __tablename__ = 'comment'
    __table_args__ = (
        ForeignKeyConstraint(['note_id'], ['note.note_id'], name='fk_note_id'),
        ForeignKeyConstraint(['user_id'], ['user.user_id'], name='fk_user_id'),
        PrimaryKeyConstraint('comment_id', name='comment_pkey')
    )

    comment_id = Column(Integer,
                        Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False,
                                 cache=1))
    note_id = Column(ForeignKey('note.note_id'), nullable=False)
    user_id = Column(ForeignKey('user.user_id'), nullable=False)
    text = Column(Text, nullable=False)
    date = Column(Date, nullable=False)

    # note = relationship('Note', back_populates='comment')
    # user = relationship('User', back_populates='comment')
