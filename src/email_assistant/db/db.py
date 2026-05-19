# db.py
# Centralized PostgreSQL connection pool module for LangGraph

from psycopg_pool import ConnectionPool
from langgraph.store.postgres import PostgresStore
from langgraph.checkpoint.postgres import PostgresSaver



DATABASE_URL = (
    "postgresql://postgres:cbj123@localhost:5432/langgraph_db"
)

# Shared PostgreSQL connection pool
pool = ConnectionPool(
    conninfo=DATABASE_URL,
    max_size=20,
    kwargs={
        "autocommit": True
    }
)

# LangGraph persistent store (long-term memory)
store = PostgresStore(pool)

# LangGraph checkpoint saver (thread state / resumability)
checkpointer = PostgresSaver(pool)


def init_db():
    """
    Create required LangGraph tables.
    Run once during application startup.
    """

    store.setup()
    checkpointer.setup()

    print("PostgresStore initialized")
    print("PostgresSaver initialized")


def close_db():
    """
    Gracefully close all DB connections.
    """
    pool.close()
    print("Connection pool closed")