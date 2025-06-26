from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    phone = Column(String)
    password = Column(String, nullable=False)
    contacts = Column(String)

engine = create_engine('sqlite:///users.db', echo=False)
Session = sessionmaker(bind=engine)
session = Session()

Base.metadata.create_all(engine)


def add_user(username, phone, password):
    if session.query(User).filter_by(username=username).first():
        return False  # Username already exists
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


def get_contacts(username):
    user = session.query(User).filter_by(username=username).first()
    if user:
        return user.contacts.split(',') if user.contacts else []
    return []