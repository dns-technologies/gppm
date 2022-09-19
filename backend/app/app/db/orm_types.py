from sqlalchemy import orm, engine

class GreenPlumSession(orm.Session):
    pass

class GreenPlumConnection(engine.Connection):
    pass

class GreenPlumEngine(engine.Engine):
    pass