import db_handler
import datetime
import sqlite3

# update db when the topics are updated
def update_bot_db():
    conn = sqlite3.connect('topics.db')
    c = conn.cursor()

    db_handler.load_topics(c)

    conn.commit()
    c.close()
    db_handler.print_topics('topics.db')


# set up database for use with the bot
def set_up_bot():
    db_name = 'topics.db'
    log_name = 'log.txt'
    # bot comments every day at 8:02 AM
    bot_time_hours = 8
    bot_time_minutes = 2
    already_posted = (
        bot_time_hours < datetime.datetime.now().hour
        or bot_time_hours == datetime.datetime.now().hour
        and bot_time_minutes < datetime.datetime.now().minute
    )

    db_handler.up_db('topics.db')
    migrate_log_to_db('log.txt', 'topics.db', already_posted)

# Para migrar los datos viejos
def migrate_log_to_db(log_path, db_name, already_posted_today):
    with open(log_path) as old_log:
        log = [x.strip('\n') for x in old_log.readlines()]
    log = reversed(log)

    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    
    for i, topic in enumerate(log):
        print(topic)
        c.execute('SELECT id FROM titles WHERE title=?',(topic,))
        title_id = c.fetchone()[0]
        c.execute('SELECT id FROM bodies WHERE title_id=?',(title_id,))
        body_id = c.fetchall()[0][0]

        if already_posted_today:
            topic_date = (datetime.date.today() - datetime.timedelta(days=i))
        else:
            topic_date = (datetime.date.today() - datetime.timedelta(days=i+1))
        topic_weekday = topic_date.weekday()

        c.execute('INSERT INTO submitted VALUES (NULL, ?, ?, ?, ?)',
            (topic_date, topic_weekday, title_id , body_id))
        c.execute('UPDATE titles SET count = count + 1 WHERE id=?',
            (title_id,))
        if body_id:
            c.execute('UPDATE bodies SET count = count + 1 WHERE id=?',
                (body_id,))
    conn.commit()
    c.close()
