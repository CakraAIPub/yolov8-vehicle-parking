from db.database import *
from db.model import *
from sqlalchemy import select
from sqlalchemy.sql import func 
from datetime import datetime

### login functions ###
class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], 
                           render_kw={"placeholder": "Username"})
    
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], 
                             render_kw={"placeholder":"Password"})

    submit = SubmitField('Register')

    def validate_username(self, username):
        session = Session()
        existing_user_username = session.query(User).filter_by(username=username.data).first()
        session.close()
        if existing_user_username:
            raise ValidationError('Already exists')       

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={'placeholder': 'Username'})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={'placeholder': 'Password'})
    submit = SubmitField('Login')
    
def insert_new_user(username,password):
    session = Session()
    new_user = User(username=username, password=password)
    session.add(new_user)
    session.commit()
    session.close()

def get_uuid(username):
    session=Session()
    query = select(User.uuid).where(User.username == username)
    url = session.execute(query).fetchone()
    urls = url[0]
    session.close()
    return urls

### functions for insert data to database ###
def insert_id_database(id, url):
    session = Session()
    polygon = RTSP(id = id,url=url)
    session.add(polygon)
    session.commit()
    session.close()

def insert_url(id_user,name,url,session_id):
    session = Session()
    url = RTSP(id_user=id_user,name=name, url=url, session_id=session_id)
    session.add(url)
    session.commit()
    session.close()

def insert_session_rtsp(id, url):
    session = Session()
    polygon = RTSP(session_id = id, url_rtsp=url)
    session.add(polygon)
    session.commit()
    session.close()

def insert_area(id_uuid,area):
    session = Session()
    session.query(RTSP).filter_by(id=id_uuid).update({'area': area})
    session.commit()
    session.close()

def insert_coordinates(id_uuid,coordinates):
    session = Session()
    session.query(RTSP).filter_by(id=id_uuid).update({'coordinates': coordinates})
    session.commit()
    session.close()

def insert_image(id_uuid,url_imgae):
    session=Session()
    session.query(RTSP).filter_by(id=id_uuid).update({'image': url_imgae})
    session.commit()
    session.close()


### ------------------functions for retrieve database--------------------------- ###
def get_id_user(username):
    session = Session()
    query = select(User.id).where(User.username==username)
    id = session.execute(query).fetchone()
    id = id[0]
    session.close()
    return id

def get_table_rtsp(id_user):
    session = Session()
    results = session.query(RTSP.id, RTSP.name, RTSP.url).filter(RTSP.id_user==id_user).all()
    session.close()
    return results

def get_uuid_user(id_user, id):
    session = Session()
    query = select(RTSP.session_id).where(RTSP.id_user == id_user, RTSP.id == id)
    urls = session.execute(query).fetchone()
    url = urls[0]
    session.close()
    return url

def get_url_rtsp(id_user, id):
    session = Session()
    query = select(RTSP.url).where(RTSP.id_user == id_user, RTSP.id == id)
    urls = session.execute(query).fetchone()
    url = urls[0]
    session.close()
    return url

def get_url(id):
    session = Session()
    query = select(RTSP.url).where(RTSP.id == id)
    urls = session.execute(query).fetchone()
    url = urls[0]
    session.close()
    return url

def get_img(id):
    session=Session()
    query = select(RTSP.image).where(RTSP.id == id)
    url = session.execute(query).fetchone()
    urls = url[0]
    session.close()
    return urls

def get_coords(id):
    session = Session()
    query = select(RTSP.coordinates).where(RTSP.id == id)
    url = session.execute(query).fetchone()
    urls = url[0]

    coordinates_data = {}

    #looping for getting dictionary of coordinates data
    for idx, data in enumerate(urls):
        coordinates_data[idx] = data
    return coordinates_data

### function for updating and deleting
def delete_rtsp(id_user,id):
    session = Session()
    delete_query = session.query(RTSP).filter(RTSP.id == id, RTSP.id_user==id_user).first()
    session.delete(delete_query)
    session.commit()
    session.close()