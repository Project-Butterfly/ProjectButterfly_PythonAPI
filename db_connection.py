import config_handler
import logging
import psycopg2


class DataAccessObject:
    def __init__(self, config=config_handler.get_default()):
        self.config = config.get_db_config()
        self.has_connected = False
        self.tables = {i: f'"projectbutterflyapi$prod"."{i}"' for i in ["User", "Post", "Message"]}

    def _connect(self, function):
        """:param function Function with 1 Cursor parameter.
        :returns result of function"""

        connection = None
        value = None

        # noinspection PyUnresolvedReferences
        try:
            logging.debug('Connecting to the PostgreSQL Database...')

            connection = psycopg2.connect(**self.config)
            cur = connection.cursor()

            if not self.has_connected:
                cur.execute('SELECT version()')
                db_version = cur.fetchone()
                logging.debug(f'Database Version: {db_version}')

            value = function(cur)

            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            logging.error(error)
        finally:
            if connection is not None:
                connection.close()
                logging.debug("Database Connection Closed")
        return value

    def get_phone_numbers(self):

        def _get_phone_number(cursor):
            # noinspection SqlResolve,SqlNoDataSourceInspection
            cursor.execute(f'SELECT "User"."phoneNumber" FROM {self.tables["User"]}')
            users = cursor.fetchall()
            return tuple(map(lambda x: x[0], users))

        return self._connect(_get_phone_number)

    def get_messages(self, limit=-1):

        def _get_messages(cursor):
            # noinspection SqlResolve,SqlNoDataSourceInspection
            cursor.execute(f'SELECT "Message".* FROM {self.tables["Message"]}' +
                           (f' LIMIT {limit}' if limit > 0 else ''))
            msgs = cursor.fetchall()
            return msgs

        return self._connect(_get_messages)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
