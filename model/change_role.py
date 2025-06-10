import sqlite3
from sys import argv


def main(argv):
    # db path
    path: str = "../crowd.db"

    # connect to db
    db = sqlite3.connect(path)

    username: str = argv[1]
    role: str = argv[2]

    # delete the user
    db.execute("UPDATE users SET role = ? WHERE username = ?", (role, username))
    db.commit()
    db.close()


if __name__ == "__main__":
    main(argv)
