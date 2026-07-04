import logging
from sqlalchemy.orm import Session
from app.database.models import NetworkNode, NetworkEdge

logger = logging.getLogger(__name__)

class NetworkService:
    @staticmethod
    def process_entities(db: Session, entities: list, report_id: int, risk_score: float, campaign_id: int = None):
        """
        Creates graph nodes and edges for extracted entities and links them to the campaign or report node.
        """
        # 1. Resolve source node (Campaign or Report)
        source_node = None
        if campaign_id:
            from app.database.models import Campaign
            camp = db.query(Campaign).filter(Campaign.id == campaign_id).first()
            if camp:
                # Find or create Campaign node in graph
                source_node = db.query(NetworkNode).filter(
                    NetworkNode.node_type == "campaign",
                    NetworkNode.node_value == camp.campaign_name
                ).first()
                if not source_node:
                    source_node = NetworkNode(
                        node_type="campaign",
                        node_value=camp.campaign_name,
                        risk_score=risk_score
                    )
                    db.add(source_node)
                    db.flush()
        
        if not source_node:
            # Fallback to Report node
            source_node = db.query(NetworkNode).filter(
                NetworkNode.node_type == "report",
                NetworkNode.node_value == f"RPT-{report_id}"
            ).first()
            if not source_node:
                source_node = NetworkNode(
                    node_type="report",
                    node_value=f"RPT-{report_id}",
                    risk_score=risk_score
                )
                db.add(source_node)
                db.flush()

        # 2. Add entity nodes and edges
        for entity in entities:
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
                db.flush()
            else:
                if risk_score > node.risk_score:
                    node.risk_score = risk_score
                    
            # Create link between source campaign/report node and entity node
            edge = db.query(NetworkEdge).filter(
                NetworkEdge.source_node_id == source_node.id,
                NetworkEdge.target_node_id == node.id
            ).first()
            
            if not edge:
                new_edge = NetworkEdge(
                    source_node_id=source_node.id,
                    target_node_id=node.id,
                    relationship_type="used_in"
                )
                db.add(new_edge)
                
        db.commit()

network_service = NetworkService()
