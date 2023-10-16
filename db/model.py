from sqlalchemy import String,create_engine,ForeignKey,DateTime,LargeBinary,Integer,Column, Text, JSON, UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from sqlalchemy import select
from sqlalchemy.sql import func 

Base = declarative_base()

# Define a model for storing polygon coordinates
class RTSP(Base):
    __tablename__ = 'vehicle_parking'
    id = Column(UUID, primary_key=True, nullable=False)
    url = Column(Text)
    area = Column(Integer)
    image = Column(LargeBinary)
    coordinates = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
