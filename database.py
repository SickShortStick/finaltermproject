from datetime import datetime
from sqlalchemy import Column, Integer, String, create_engine, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    phone = Column(String)
    password = Column(String, nullable=False)
    contacts = Column(String)
    

class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)
    sender_id = Column(Integer, ForeignKey('users.id'))
    receiver_id = Column(Integer, ForeignKey('users.id'))
    chat_content = Column(String, nullable=False)
    message_type = Column(String, default='text')
    timestamp = Column(String, default=datetime.utcnow)

    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])


def save_message(sender_username, receiver_username, content, message_type='text'):
    sender = session.query(User).filter_by(username=sender_username).first()
    receiver = session.query(User).filter_by(username=receiver_username).first()
    if sender and receiver:
        msg = Message(sender_id=sender.id, receiver_id=receiver.id, chat_content=content, message_type=message_type)
        session.add(msg)
        session.commit()
        return True
    return False


def save_image(sender_username, receiver_username, image_path, filename):
    content = f"{image_path}|{filename}"
    return save_message(sender_username, receiver_username, content, message_type='image')


def get_chat_history(username1, username2):
    user1 = session.query(User).filter_by(username=username1).first()
    user2 = session.query(User).filter_by(username=username2).first()

    if not user1 or not user2:
        return []

    messages = session.query(Message).filter(
        ((Message.sender_id == user1.id) & (Message.receiver_id == user2.id)) |
        ((Message.sender_id == user2.id) & (Message.receiver_id == user1.id))
    ).order_by(Message.timestamp).all()
    
    return messages


engine = create_engine('sqlite:///users.db', echo=False)
Session = sessionmaker(bind=engine)
session = Session()

Base.metadata.create_all(engine)


def add_user(username, phone, password):
    if session.query(User).filter_by(username=username).first():
        return False
    new_user = User(username=username, phone=phone, password=password)
    session.add(new_user)
    session.commit()
    return True


def check_user(username, password):
    return session.query(User).filter_by(username=username, password=password).first()


def check_user_phone(username, phone):
    user = session.query(User).filter_by(username=username).first()
    if user and user.phone == phone:
        return True
    return False

def add_contact(username, contact, phone):
    user = session.query(User).filter_by(username=username).first()
    if user:
        if user.contacts:
            contacts = user.contacts.split(',')
            if contact not in contacts:
                contacts.append(contact)
                user.contacts = ','.join(contacts)
        else:
            user.contacts = contact
        session.commit()
        return True
    return False


def update_user_info(username, new_password):
    user = session.query(User).filter_by(username=username).first()
    if user:
        user.password = new_password
        session.commit()
        return True
    return False

def update_username(old_username, new_username):
    if session.query(User).filter_by(username=new_username).first():
        return False
    user = session.query(User).filter_by(username=old_username).first()
    if user:
        user.username = new_username
        session.commit()
        update_contacts_username(old_username, new_username)
        return True
    return False

def update_phone(username, new_phone):
    user = session.query(User).filter_by(username=username).first()
    if user:
        user.phone = new_phone
        session.commit()
        return True
    return False

def update_contacts_username(old_username, new_username):
    users = session.query(User).all()
    for user in users:
        if user.contacts:
            contacts = user.contacts.split(',')
            if old_username in contacts:
                contacts = [new_username if contact == old_username else contact for contact in contacts]
                user.contacts = ','.join(contacts)
    session.commit()


def get_contacts(username):
    user = session.query(User).filter_by(username=username).first()
    if user:
        return user.contacts.split(',') if user.contacts else []
    return []

def get_phone(username):
    user = session.query(User).filter_by(username=username).first()
    if user:
        return user.phone
    return None

def get_id(username):
    user = session.query(User).filter_by(username=username).first()
    if user:
        return user.id
    return None
