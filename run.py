import opt
import sys
import config
import log
import os
import daemon


def run():
    parser = opt.create_parser()
    args = parser.parse_args(sys.argv[1:])
    conf = config.Config(args)
    journal = log.Log(path_file=conf.get("log"))
    pid = os.fork()
    if pid == 0:
        daemon.start_daemion(
            config=conf,
            log=journal
        )
    elif pid > 0:
        journal.info("Close parrent process.")
    else:
        journal.emerg("NOT STARTED CHILDREN PROCESS!")


if __name__ == '__main__':
    run()

# file='/usr/master.cfg',
# interval=2,
# mysql='root:password@localhost/voip.cdr',
# postgres='postgres:password@localhost/voip.cdr',
# restart=False,
# stop=False

# dbname="test", user="postgres", password="secret"
