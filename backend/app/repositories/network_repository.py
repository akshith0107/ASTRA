from sqlalchemy.orm import Session
from typing import List
from app.database.models import NetworkNode, NetworkEdge

class NetworkRepository:
    @staticmethod
    def get_all_nodes(db: Session) -> List[NetworkNode]:
        return db.query(NetworkNode).all()
        
    @staticmethod
    def get_all_edges(db: Session) -> List[NetworkEdge]:
        return db.query(NetworkEdge).all()
