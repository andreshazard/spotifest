import base64
import datetime
from library.app import app, mysql, celery


@celery.task(name='save_festival')
def save_to_database(festivalName, userId, playlistId,
                     playlistURL, catalogId, urlSlug):
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
        cursor.execute("INSERT INTO sessions (festivalName, userId, playlistId, playlistURL, catalogId, urlSlug)\
                        VALUES (%s, %s, %s, %s, %s, %s)", values)
        connection.commit()
        print 'saved to database'
    return


@celery.task(name='update_festival')
def update_festival(festivalName, playlistId, playlistURL, urlSlug):
    values = (festivalName, playlistId, playlistURL, urlSlug)
    with app.app_context():
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute("UPDATE sessions SET festivalName=%s, playlistId=%s,\
                        playlistURL=%s WHERE urlSlug=%s",
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
        cursor.execute("INSERT INTO contributors VALUES\
                       (%s, %s, %s, %s, %s, %s, %s, %s, %s)", values)
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
        cursor.execute("SELECT * FROM contributors WHERE\
                       (festivalId = %s AND organizer = 1)", (festivalId,))
        d1 = cursor.fetchall()
    except:
        print ("Database can't be reached")
        return None
    else:
        print (d1)
        if d1:
            print ("going into the if now")
            all_users = {'organizer': {'userId': str(d1[0][1]), 
                                   'ready': int(d1[0][2]), 
                                   'hotness': (d1[0][3]), 
                                   'danceability': (d1[0][4]),
                                   'energy': (d1[0][5]), 
                                   'variety': (d1[0][6]),
                                   'adventurousness': (d1[0][7])}}
            print ("going out of the if now")
        else:
            print ("There is no organizer assigned.")
            return None
        print (all_users)

    try:
        cursor.execute("SELECT * FROM contributors WHERE\
                       (festivalId = %s AND organizer = 0)", (festivalId,))
        d2 = cursor.fetchall()
    except:
        print ("Database can't be reached..")
        return None
    else:
        print (d2)
        if d2:
            contributors = {str(u[1]): {'ready': int(u[2]), 
                                        'hotness': u[3], 
                                        'danceability': u[4],
                                        'energy': u[5], 
                                        'variety': u[6],
                                        'adventurousness': u[7]} for u in d2}
            print (contributors)
            all_ready = 1
            for contributor in contributors:
                if contributors[contributor]['ready'] == 0:
                    all_ready = 0
                    print ("a contributor isn't ready")
                    break
            all_users.update({'contributors': contributors, 'all_ready': all_ready})
            print (all_users)
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
        cursor.execute("SELECT * FROM sessions WHERE urlSlug = %s", (urlSlug,))
        data = cursor.fetchall()
        if not data:
            return None
        print 'DATA', data
        festivalId = int(data[0][0])
        festivalName = str(data[0][1])
        userId = str(data[0][2])
        playlistId = str(data[0][3])
        playlistURL = str(data[0][4])
        catalogId = str(data[0][5])
        values = [festivalId, festivalName, userId,
                  playlistId, playlistURL, catalogId]
        return values

def get_user_festivals(user_id):
    '''
    return the festivals the user is involved in
    '''
    connection = mysql.get_db()
    cursor = connection.cursor()
    query1 = str(("SELECT contributors.festivalId, sessions.festivalName, sessions.userId, "
            "sessions.urlSlug, contributors.organizer FROM contributors "
            "INNER JOIN sessions ON contributors.festivalId=sessions.festivalId"
            "WHERE contributors.userId = %s", (user_id,)))
    query = ("SELECT c.userId, s.festivalId, s.festivalName, s.urlSlug, "
        "c.organizer FROM sessions as s INNER JOIN contributors as c on "
        "s.festivalId = c.festivalId  where s.festivalId = c.festivalId "
        "and c.userId = '{}'".format(user_id))

    print "this is the query {}".format(query)
    
    cursor.execute(query)
    d = cursor.fetchall()
    print (d)
    
    organized_festivals = {u[1]: {'festival_name':u[2], 'url_slug':u[3]} for u in d if u[4] == 1}
    print (" organized festivals", organized_festivals)
    contributed_festivals = {u[1]:{'festival_name':u[2], 'url_slug':u[3], 'user_id':u[0]} for u in d if u[4] == 0}
    print ("  contributed", contributed_festivals)
    user_festivals = {'organizer':organized_festivals}
    user_festivals.update({'contributor':contributed_festivals})
    print ("these are the festivals the user is involved in {}".format(user_festivals))
    return user_festivals


def get_average_parameters(festivalId):
    '''
    return list of the average parameters for a festival
    '''
    with app.app_context():
        connection = mysql.get_db()
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT AVG(hotness), AVG(danceability), \
                            AVG(energy), AVG(variety), AVG(adventurousness) \
                            from contributors where festivalId = %s", (festivalId,))
            data = cursor.fetchall()
        except:
            print 'error getting average parameters from the DB'
            return None
        average_parameters = [float(data[0][0]), float(data[0][1]), 
                              float(data[0][2]), float(data[0][3]), 
                              float(data[0][4])]
        print 'Average Parameter : ' + str(average_parameters)
        return average_parameters