import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database.database import SessionLocal, engine
from app.database.models.base import Base
from app.database.models import Report, Campaign, NetworkNode, NetworkEdge, Alert

def generate_seed_data():
    print("Creating tables if they don't exist...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    print("Seeding database for Dashboard UI...")

    # 1. Campaigns (20)
    campaigns = []
    scam_types = ["Bank Impersonation", "Job Scam", "Lottery Scam", "Tech Support Fraud", "Romance Scam"]
    for i in range(20):
        c = Campaign(
            campaign_name=f"Operation_Storm_{i}",
            description="Automated generated campaign",
            scam_type=random.choice(scam_types),
            threat_level=random.choice(["MEDIUM", "HIGH_RISK", "CRITICAL"]),
            first_seen=datetime.utcnow() - timedelta(days=random.randint(10, 30)),
            last_seen=datetime.utcnow()
        )
        db.add(c)
        campaigns.append(c)
    db.commit()

    # 2. Reports (100)
    reports = []
    for i in range(100):
        risk = random.uniform(0.1, 0.99)
        r = Report(
            transcript=f"Sample transcribed text for report {i}",
            risk_score=risk,
            risk_level="CRITICAL" if risk > 0.8 else "HIGH_RISK" if risk > 0.6 else "LOW",
            scam_type=random.choice(scam_types),
            confidence=random.uniform(0.5, 0.99)
        )
        db.add(r)
        reports.append(r)
    db.commit()

    # 3. Network Nodes (500)
    nodes = []
    node_types = ["phone", "url", "upi", "bitcoin"]
    for i in range(500):
        n = NetworkNode(
            node_type=random.choice(node_types),
            node_value=f"Entity-{i}-{random.randint(1000, 9999)}",
            risk_score=random.uniform(0.1, 0.99),
            first_seen=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
            last_seen=datetime.utcnow()
        )
        db.add(n)
        nodes.append(n)
    db.commit()

    # 4. Network Edges (1000)
    for i in range(1000):
        source = random.choice(nodes)
        target = random.choice(nodes)
        if source.id != target.id:
            edge = NetworkEdge(
                source_node_id=source.id,
                target_node_id=target.id,
                relationship_type=random.choice(["linked_to", "used_in", "reported_with"])
            )
            db.add(edge)
    
    # 5. Alerts (50)
    for i in range(50):
        report = random.choice(reports)
        a = Alert(
            report_id=report.id,
            title=f"Critical Threat Detected in Report {report.id}",
            description="Automatically flagged by Risk Engine.",
            severity="CRITICAL"
        )
        db.add(a)

    db.commit()
    db.close()
    print("Seed data injected successfully!")

if __name__ == "__main__":
    generate_seed_data()
