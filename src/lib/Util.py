from datetime import datetime


class Util:
    @staticmethod
    # datetime.strptime and datetime.strftime in one go
    def strpstrf(dt, strp="%Y%m%d", strf="%Y-%m-%d"):
        dt = str(dt)  # Ensure string
        return datetime.strftime(datetime.strptime(dt, strp), strf)
