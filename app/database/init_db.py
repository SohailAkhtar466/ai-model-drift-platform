from app.database.database import (
    Base,
    engine,
)

from app.database import models


def init_database():

    Base.metadata.create_all(
        bind=engine
    )

    print(
        "Database tables created successfully."
    )


if __name__ == "__main__":

    init_database()