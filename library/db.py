import base64
import datetime
from library.app import app, mysql, celery


@celery.task(name='save_festival')
def save_to_database(festivalName, userId, playlistId, playlistURL, catalogId, urlSlug):
    '''
    saves infromation the data base.
    festivalId will be created automatically
    '''
    festivalName = str(festivalName)
    userId = str(userId)
    playlistId = str(playlistId)
    playlistURL = str(playlistURL)
    catalogId = str(catalogId)
    values = (festivalName, userId, playlistId, playlistURL, catalogId, urlSlug)
    with app.app_context():
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO sessions (festivalName, userId, playlistId, playlistURL, catalogId, urlSlug) VALUES (%s, %s, %s, %s, %s, %s)", values)
        connection.commit()
        print 'saved to database'
    return


@celery.task(name='update_festival')
def update_festival(festivalName, playlistId, playlistURL, urlSlug):
    values = (festivalName, playlistId, playlistURL, urlSlug)
    with app.app_context():
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute("UPDATE sessions SET festivalName=%s, playlistId=%s, playlistURL=%s WHERE urlSlug=%s",
                        (festivalName, playlistId, playlistURL, urlSlug))
        connection.commit()
        print 'saved to database'
    return


def update_parameters(festivalId, userId, hotttnesss, danceability,
                    energy, variety, advent):
    festivalId = int(festivalId)
    userId = str(userId)
    hotttnesss = float(hotttnesss)
    danceability = float(danceability)
    energy = float(energy)
    variety = float(variety)
    advent = float(advent)
    with app.app_context():
        connection = mysql.connect()
        cursor = connection.cursor()
        values = (hotttnesss, danceability, energy, variety, advent, festivalId, userId)
        print "THESE ARE VALUES", values
        cursor.execute("UPDATE contributors SET hotness=%s, danceability=%s, energy=%s,\
                        variety=%s, adventurousness=%s, ready=1 WHERE festivalId=%s AND userId=%s", values)
        connection.commit()
        print "updated settings for user."
    return


def save_contributor(festivalId, userId, ready=0, hotness=None,
                    danceability=None, energy=None, variety=None, advent=None,
                    organizer=0):
    '''
    requires festivalId and userId,
    saves whatever else you also put in it in the contributor table
    '''
    festivalId = int(festivalId)
    userId = str(userId)
    values = (festivalId, userId, ready, hotness,
                danceability, energy, variety, advent, organizer)
    print ("Saving contributor {} to festival {}".format(userId, festivalId))
    with app.app_context():
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO contributors VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", values)
        connection.commit()
        print 'saved to database'
    return


def get_contributors(festivalId):
    '''
    return a list with all the contributors id of
    the festival. THE FIRST contributor == organizer
    '''
    print type(festivalId)
    print (festivalId)
    connection = mysql.get_db()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT userId FROM contributors WHERE (festivalId = %s AND organizer = 1)", (festivalId,))
    except:
        print ("Database can't be reached")
        return None
    data1 = cursor.fetchall()
    if data1:
        all_users = [user[0].encode('utf-8') for user in data1]
    else:
        print ("There is no organizer assigned.")
        return None

    try:
        connection = mysql.get_db()
        cursor = connection.cursor()
        cursor.execute("SELECT userId FROM contributors WHERE (festivalId = %s AND organizer = 0)", (festivalId,))
        data2 = cursor.fetchall()
        print ("contributors: {}".format(data2))
    except:
        print ("Database can't be reached..")
        return None
    if data2:
        contributors = [user[0].encode('utf-8') for user in data2]
        all_users += contributors

    print ('contributors retrieved from database: {}'.format(all_users))
    return all_users


def get_info_from_database(urlSlug):
    '''
    return a list with all the information from the
    database for a certain festival id
    '''
    print "URL SLUG IS {}".format(urlSlug)
    with app.app_context():
        connection = mysql.get_db()
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT * FROM sessions WHERE urlSlug = %s", (urlSlug,))
            data = cursor.fetchall()
        except:
            return None
        print 'DATA', data
        festivalId = int(data[0][0])
        festivalName = str(data[0][1])
        userId = str(data[0][2])
        playlistId = str(data[0][3])
        playlistURL = str(data[0][4])
        catalogId = str(data[0][5])
        values = [festivalId, festivalName, userId, playlistId, playlistURL, catalogId]
        return values


def get_average_parameters(festivalId):
    '''
    return list of the average parameters for a festival
    '''
    with app.app_context():
        connection = mysql.get_db()
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT AVG(hotness), AVG(danceability), AVG(energy), AVG(variety),\
                            AVG(adventurousness) from contributors where festivalId = %s", (festivalId,))
            data = cursor.fetchall()
        except:
            print 'error getting average parameters from the DB'
            return None
        average_parameters = [float(data[0][0]), float(data[0][1]), float(data[0][2]),
                              float(data[0][3]), float(data[0][4])]
        print 'Average Parameter : ' + str(average_parameters)
        return average_parameters
