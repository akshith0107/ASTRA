from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey
from app.database.models.base import Base, BaseMixin

class NetworkNode(Base, BaseMixin):
    __tablename__ = "network_nodes"

    node_type = Column(String, index=True) # phone, upi, url, campaign, script
    node_value = Column(String, unique=True, index=True)
    risk_score = Column(Float)
    
    first_seen = Column(DateTime)
    last_seen = Column(DateTime)

class NetworkEdge(Base, BaseMixin):
    __tablename__ = "network_edges"

    source_node_id = Column(Integer, ForeignKey("network_nodes.id", ondelete="CASCADE"), index=True)
    target_node_id = Column(Integer, ForeignKey("network_nodes.id", ondelete="CASCADE"), index=True)
    relationship_type = Column(String) # linked_to, used_in, part_of, reported_with
