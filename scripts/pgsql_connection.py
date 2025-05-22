"""
Base class for a script using a connection to the PGSQL database
"""
import psycopg2


PGSQL_DBNAME = "optalim_dev"
USERNAME = "dev"
PASSWORD = "dev"
CSV_DELIMITER = ';'


class PGSQLScript(object):
    def __init__(self):
        self.connection = psycopg2.connect(host="localhost", user=USERNAME,
                                           password=PASSWORD, database=PGSQL_DBNAME)

    def __del__(self):
        self.connection.close()

    def solo_insertion(self, values, sql_table, sql_columns):
        """
        Insert one row and returns the ID
        """
        cur = self.connection.cursor()
        insert_statement = 'INSERT INTO %s (%s) VALUES (%s) RETURNING id' %\
           (sql_table, ','.join(sql_columns), ','.join(['%s'] * len(sql_columns)))
        cur.execute(insert_statement, values)
        id_of_new_row = cur.fetchone()[0]
        self.connection.commit()
        return id_of_new_row

    def multiple_insertion(self, values, sql_table, sql_columns):
        """
        Does a multiple insertion in the PGSQL database
        """
        cur = self.connection.cursor()
        insert_statement = 'INSERT INTO %s (%s) VALUES (%s)' %\
           (sql_table, ','.join(sql_columns), ','.join(['%s'] * len(sql_columns)))
        print(insert_statement)
        cur.executemany(insert_statement, values)
        self.connection.commit()
        print('inserted %i rows in %s' % (cur.rowcount, sql_table))