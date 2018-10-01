import pymysql
import psycopg2
from datetime import datetime


# DB_POSTGRES = None
# DB_MYSQL = None
# TABLE_POSTGRES = None
# TABLE_MYSQL = None


def start_daemion(**kwargs):
    log = kwargs["log"]

    # создание соединения к базам
    postgres_connection = psycopg2.connect(
        user=kwargs["config"].get("postgres")[0],
        password=kwargs["config"].get("postgres")[1],
        host=kwargs["config"].get("postgres")[2],
        dbname=kwargs["config"].get("postgres")[3]
    )
    postgres_connection.autocommit = True
    pg_table = kwargs["config"].get("postgres")[4]
    postgres = postgres_connection.cursor()

    mysql_connection = pymysql.connect(
        user=kwargs["config"].get("mysql")[0],
        password=kwargs["config"].get("mysql")[1],
        host=kwargs["config"].get("mysql")[2],
        db=kwargs["config"].get("mysql")[3],
        charset="utf8mb4"
    )
    mysql_connection.autocommit = True
    mysql = mysql_connection.cursor()

    # получения начального значения для запроса по основным данным
    pg_query_start = """
        SELECT start_stamp_in
        FROM cdrs_all ORDER BY id
        DESC LIMIT 1;"""
    start_date = None
    try:
        postgres.execute(pg_query_start)
    except psycopg2.Error as error:
        log.crit(
            "daemon.py:46. Error in 'pg_query_start' to table cdrs_all: {0}".format(
                error
            )
        )
        exit(-1)
    else:
        start_date = postgres.fetchone()
        if not start_date:
            log.info("table 'cdrs_all' is clear.")
            pg_query_start = """
                SELECT start_stamp
                FROM cdrs ORDER BY id
                ASC LIMIT 1;"""

            try:
                postgres.execute(pg_query_start)
            except psycopg2.Error as error:
                log.crit(
                    "daemon.py:64. Error in 'pg_query_start' to table cdrs_all: {0}".format(
                        error
                    )
                )
                exit(-1)
            else:
                start_date = postgres.fetchone()
                # log.err("daemon.py:70. Error in 'pg_query_start' to table cdrs'.")
    if not start_date:
        log.crit(
            "daemon.py:74. Query 'pg_query_start' return NULL. Stop app."
        )
        exit(-1)
    else:
        now_date = datetime.today()
        end_date = "{0}-{1:02}-{2:02} {3}:00:00".format(
            now_date.year,
            now_date.month,
            now_date.day,
            now_date.hour
        )

    # выборка записей за период от "start_date" до "end_date"
    pg_query = """
        SELECT id, uuid, bridge_uuid, sip_call_id,
        caller_id_number, destination_number, sip_from_host,
        sip_req_host, duration, billsec, hangup_cause,
        sip_hangup_disposition, start_stamp, answer_stamp, end_stamp
        FROM {0} WHERE direction = 'inbound'
        AND sip_call_id IS NOT NULL
        AND start_stamp > '{1}'
        AND start_stamp <= '{2}';
    """.format(
        pg_table,
        start_date[0],
        end_date
    )
    try:
        postgres.execute(pg_query)
    except psycopg2.Error as error:
        log.crit(
            "daemon.py:105. Error in 'pg_query' to table {0}: {1}".format(
                pg_table, error
            )
        )
        exit(-1)
    all_record_pg = postgres.fetchall()

    # обработка записей и формирование запроса в "cdrs_all"
    for record in all_record_pg:
        bridge_uuid = record[2]
        outboun_query = """
            SELECT id, uuid, bridge_uuid, sip_call_id,
            caller_id_number, destination_number, sip_from_host,
            sip_req_host, duration, billsec, hangup_cause,
            sip_hangup_disposition, start_stamp
            FROM {0} WHERE direction = 'outbound'
            AND uuid = '{1}';""".format(pg_table, bridge_uuid)
        try:
            postgres.execute(outboun_query)
        except psycopg2.Error as error:
            log.crit(
                "daemon.py:126. Error in 'pg_query' to table {0}: {1}".format(
                    pg_table, error
                )
            )
            exit(-1)

        sip_call_id = record[3]
        cdr_next_query = """
            SELECT cdr_ID, fbasename
            FROM cdr_next
            WHERE fbasename = '{}';""".format(sip_call_id)
        try:
            mysql.execute(cdr_next_query)
        except Exception as error:
            log.crit(
                "daemon.py:141. Error in 'pg_query' to table cdr_next: {0}".format(error)
            )
        cdr_next = mysql.fetchone()
        cdr_next_in = None
        if cdr_next:
            cdr_next_in = cdr_next[1]
        else:
            cdr_next_in = ""
        outbound_cdr = postgres.fetchone()

        if outbound_cdr:

            sip_call_id = outbound_cdr[3]
            cdr_next_query = """
                SELECT cdr_ID, fbasename
                FROM cdr_next
                WHERE fbasename = '{}';""".format(sip_call_id)
            try:
                mysql.execute(cdr_next_query)
            except Exception as error:
                log.crit(
                    "daemon.py:162. Error in 'pg_query' to table cdr_next: {0}".format(error)
                )
            cdr_next = mysql.fetchone()
            cdr_next_out = None
            if cdr_next:
                cdr_next_out = cdr_next[1]
            else:
                cdr_next_out = ""

            cdrs_all_query = """
                INSERT INTO cdrs_all(uuid_in, uuid_out, sip_caller_id_in,
                sip_caller_id_out, caller_id_number_in, caller_id_number_out,
                destination_number_in, destination_number_out,
                sip_from_host_in, sip_from_host_out, sip_req_host_in,
                sip_req_host_out, duration_in, duration_out, billsec_in,
                billsec_out, hangup_cause_in, hangup_cause_out,
                sip_hangup_disposition_in, sip_hangup_disposition_out,
                start_stamp_in, start_stamp_out, answer_stamp, end_stamp,
                filename_in, filename_out) VALUES ('{0}', '{1}', '{2}',
                '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}', '{10}', '{11}',
                {12}, {13}, {14}, {15}, '{16}', '{17}', '{18}', '{19}',
                '{20}', '{21}', '{22}', '{23}', '{24}', '{25}');""".format(
                record[1], record[2], record[3], outbound_cdr[3], record[4],
                outbound_cdr[4], record[5], outbound_cdr[5], record[6],
                outbound_cdr[6], record[7], outbound_cdr[7], record[8],
                outbound_cdr[8], record[9], outbound_cdr[9], record[10],
                outbound_cdr[10], record[11], outbound_cdr[11], record[12],
                outbound_cdr[12], record[13], record[14], cdr_next_in,
                cdr_next_out
            )
            postgres.execute(cdrs_all_query)
    postgres_connection.close()
    mysql_connection.close()
