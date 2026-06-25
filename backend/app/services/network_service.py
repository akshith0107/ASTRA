import logging
from sqlalchemy.orm import Session
from app.database.models import NetworkNode, NetworkEdge

logger = logging.getLogger(__name__)

class NetworkService:
    @staticmethod
    def process_entities(db: Session, entities: list, report_id: int, risk_score: float, campaign_id: int = None):
        """
        Automates creating graph nodes and edges for extracted entities.
        """
        for entity in entities:
            # Check if node already exists
            node_val = entity["value"]
            node_type = entity["type"]
            
            node = db.query(NetworkNode).filter(NetworkNode.node_value == node_val).first()
            if not node:
                node = NetworkNode(
                    node_type=node_type,
                    node_value=node_val,
                    risk_score=risk_score
                )
                db.add(node)
                db.flush() # get node.id
            else:
                # Update risk score if higher
                if risk_score > node.risk_score:
                    node.risk_score = risk_score
                    
            # Create edge from Report/Campaign to Node
            # We use campaign_id as the source if available to cluster them easily
            source_id = campaign_id if campaign_id else report_id
            
            # Check if edge exists
            edge = db.query(NetworkEdge).filter(
                NetworkEdge.source_node_id == source_id,
                NetworkEdge.target_node_id == node.id,
                NetworkEdge.relationship_type == "used_in"
            ).first()
            
            if not edge:
                new_edge = NetworkEdge(
                    source_node_id=source_id,
                    target_node_id=node.id,
                    relationship_type="used_in"
                )
                db.add(new_edge)
                
        db.commit()

network_service = NetworkService()
