import argparse


def create_parser():
    parser = argparse.ArgumentParser(
        prog="move_task",
        description="""
            Приложение для поиска записей разговора
            и последующего переноса их на nfs-server.

            Приложение работает с двумя базами данных:
            MySQL и PostgreSQL. В MySQL хранится информация
            о сохраненных записях разговора, в PostgreSQL
            хранится информация о произошедших звонках.
        """,
        epilog="""
        (с) 2018 Амельченко Дмитрий.\n
            amelchenko.dmitrit@outlook.com
        """,
        add_help=False
    )
    parser.add_argument(
        "-h",
        "-help",
        action="help",
        help="Вывести данное сообщение."
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        help="Текущая версия проложения.",
        version="version - v_0.1"
    )
    parser.add_argument(
        "-i",
        "--interval",
        type=int,
        default=0,
        metavar="<5>",
        help="""Не обязательный параметр, принимает интервал частоты
            запуска переноса.
            По умолчанию 1 час.
            Можно задать в файле конфигурациию
        """
    )
    parser.add_argument(
        "-s",
        "--stop",
        action="store_true",
        help="""Остановить приложение."""
    )
    parser.add_argument(
        "-r",
        "--restart",
        action="store_true",
        help="""Перезапуск приложения с возможными новыми параметрами.
        """
    )
    parser.add_argument(
        "-f",
        "--file",
        default="/usr/local/etc/move_task/settings.cfg",
        metavar="</path/to/file.cfg>",
        help="""Путь к файлу кофигурации, читается при старте программы.
            По умолчанию: "/usr/local/etc/move_task/settings.cfg".
        """
    )
    parser.add_argument(
        "-l",
        "--log",
        default="/var/log/move_task.log",
        metavar="</path/to/file.log>",
        help="""Путь к файлу лога, читается при старте программы.
            По умолчанию: "/var/log/move_task.log".
        """
    )
    parser.add_argument(
        "-m",
        "--mysql",
        default=False,
        metavar="<user:password@host/base.table>",
        help="""Строка подключения к база данных: MySQL.
            По умолчанию: "root:password@localhost/voip.cdr".
            Можно задать в файле конфигурации.
        """
    )
    parser.add_argument(
        "-p",
        "--postgres",
        default=False,
        metavar="<user:password@host/base.table>",
        help="""Строка подключения к база данных: PostgreSQL.
            По умолчанию: "postgres:password@localhost/voip.cdr".
            Можно задать в файле конфигурации."""
    )
    return parser


if __name__ == '__main__':
    import sys
    data = create_parser()
    args = data.parse_args(sys.argv[1:])
    print(args)
