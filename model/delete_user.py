import sqlite3
from sys import argv


def main(argv):
    # db path
    path: str = "../crowd.db"

    # connect to db
    db = sqlite3.connect(path)

    # delete the user
    db.execute("DELETE FROM users WHERE username = ?", (argv[1],))
    db.commit()
    db.close()


if __name__ == "__main__":
    main(argv)
