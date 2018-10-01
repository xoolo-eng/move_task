import re


class Config():
    """docstring for Config"""
    __base_pattern = re.compile(
        "([\w]+):([\S]*)@([\w\.]+)/([\w_-]+).([\w_]+)"
    )

    def __init__(self, args):
        self.data = {}
        if args.interval:
            self.data["interval"] = args.interval
        if args.interval:
            self.data["log"] = args.log
        if args.mysql:
            self.data["mysql"] = args.mysql
        if args.postgres:
            self.data["postgres"] = args.postgres
        file = open(args.file, "r").read()
        if file:
            file_data = file.split("\n")
            for string in file_data:
                string.strip()
                if string[0] != "#":
                    key_value = string.split("=")
                    try:
                        self.data[key_value[0].strip()] = key_value[1].strip()
                    except IndexError:
                        pass
        self.data["mysql"] = list(re.findall(self.__base_pattern, self.data["mysql"])[0])
        self.data["postgres"] = list(re.findall(self.__base_pattern, self.data["postgres"])[0])
        if len(self.data["mysql"]) != 5:
            raise ValueError(
                "Error in config file or passed arguments: MySQL"
            )
        if len(self.data["postgres"]) != 5:
            raise ValueError(
                "Error in config file or passed arguments: PosqtgreSQL"
            )

    def get(self, key):
        return self.data.get(key)

    def set(self, key, value):
        self.data[key] = value

# file='/usr/master.cfg',
# interval=2,
# mysql='root:password@localhost/voip.cdr',
# postgres='postgres:password@localhost/voip.cdr',
# restart=False,
# stop=False
# "([\w]+):([\S]*)@([\w\.]+)/([\w_-]+).([\w_]+)"
# base_pattern = re.compile("([\w]+):([\S]*)@([\w\.]+)/([\w_-]+).([\w_]+)")
