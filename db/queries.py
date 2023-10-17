from db.database import *
from db.model import *
from sqlalchemy import select

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

def get_table_rtsp(id_user):
    session = Session()
    results = session.query(RTSP.id, RTSP.name, RTSP.url).filter(RTSP.id_user==id_user).all()
    session.close()
    return results

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
