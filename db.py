from azure.cosmos import CosmosClient
from flask import g
import os

def get_client():
  if not hasattr(g, 'client'):
    URL = os.environ["COSMOS_URI"]
    KEY = os.environ["COSMOS_KEY"]
    g.client = CosmosClient(URL, credential=KEY)
  return g.client


def get_db():
  if not hasattr(g, 'database'):
    g.database = get_client().get_database_client('db')
  return g.database


def get_container_rent_users():
  if not hasattr(g, 'container'):
    g.container_rent_users = get_db().get_container_client('rent_users')
  return g.container_rent_users
