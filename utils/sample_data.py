# utils/sample_data.py
# Sample Data Generator for AAVA System
# Generates realistic test data for demonstration

"""
Sample Data Generator
=====================

Generates realistic sample data including:
- 50-100 addresses across major Indian cities
- 10-15 field agents with varied performance
- 200+ delivery records
- Validation requests and verifications
- Audit log entries
"""

import random
import json
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import get_database, DatabaseManager
from utils.digipin import DIGIPINValidator
from utils.confidence_score import get_grade


# =============================================================================
# SAMPLE DATA CONFIGURATION
# =============================================================================

# Indian cities with coordinates
INDIAN_CITIES = {
    "New Delhi": (28.6139, 77.2090, "Delhi", "110001"),
    "Mumbai": (19.0760, 72.8777, "Maharashtra", "400001"),
    "Bangalore": (12.9716, 77.5946, "Karnataka", "560001"),
    "Chennai": (13.0827, 80.2707, "Tamil Nadu", "600001"),
    "Kolkata": (22.5726, 88.3639, "West Bengal", "700001"),
    "Hyderabad": (17.3850, 78.4867, "Telangana", "500001"),
    "Pune": (18.5204, 73.8567, "Maharashtra", "411001"),
    "Ahmedabad": (23.0225, 72.5714, "Gujarat", "380001"),
    "Jaipur": (26.9124, 75.7873, "Rajasthan", "302001"),
    "Lucknow": (26.8467, 80.9462, "Uttar Pradesh", "226001"),
    "Chandigarh": (30.7333, 76.7794, "Punjab", "160001"),
    "Bhopal": (23.2599, 77.4126, "Madhya Pradesh", "462001"),
    "Kochi": (9.9312, 76.2673, "Kerala", "682001"),
    "Guwahati": (26.1445, 91.7362, "Assam", "781001"),
    "Patna": (25.5941, 85.1376, "Bihar", "800001")
}

# Agent names (Indian names)
AGENT_NAMES = [
    ("Rahul", "Kumar"),
    ("Priya", "Sharma"),
    ("Amit", "Singh"),
    ("Neha", "Patel"),
    ("Vikram", "Reddy"),
    ("Anjali", "Gupta"),
    ("Rajesh", "Verma"),
    ("Sunita", "Devi"),
    ("Mohit", "Agarwal"),
    ("Kavita", "Nair"),
    ("Suresh", "Yadav"),
    ("Pooja", "Mishra"),
    ("Arun", "Krishnan"),
    ("Deepa", "Menon"),
    ("Sanjay", "Chauhan")
]

# Street names
STREET_NAMES = [
    "MG Road", "Gandhi Nagar", "Nehru Street", "Park Avenue",
    "Station Road", "Temple Street", "Market Road", "College Road",
    "Industrial Area", "Civil Lines", "Rajaji Road", "Lake View",
    "Green Park", "Shanti Nagar", "Ashok Marg", "Lal Bahadur Marg"
]

# Locality names
LOCALITIES = [
    "Sector", "Block", "Phase", "Colony", "Extension",
    "Enclave", "Nagar", "Vihar", "Puram", "Layout"
]

# Delivery partners
DELIVERY_PARTNERS = [
    "BlueDart Express",
    "Delhivery",
    "DTDC",
    "Ecom Express",
    "FedEx India",
    "India Post",
    "Amazon Logistics",
    "Flipkart Logistics",
    "XpressBees",
    "Shadowfax"
]


# =============================================================================
# SAMPLE DATA GENERATOR CLASS
# =============================================================================

class SampleDataGenerator:
    """Generates realistic sample data for AAVA system."""
    
    def __init__(self, db: DatabaseManager = None):
        """Initialize with database connection."""
        self.db = db or get_database()
        self.validator = DIGIPINValidator()
        
        # Generated IDs for reference
        self.address_ids = []
        self.agent_ids = []
        self.validation_ids = []
        
    def generate_phone(self) -> str:
        """Generate a random Indian phone number."""
        prefixes = ["98", "97", "96", "95", "94", "93", "91", "90", "89", "88", "87", "86"]
        return f"+91-{random.choice(prefixes)}{random.randint(10000000, 99999999)}"
    
    def generate_street_address(self, city: str) -> str:
        """Generate a realistic Indian street address."""
        house_num = random.randint(1, 999)
        street = random.choice(STREET_NAMES)
        locality = f"{random.choice(LOCALITIES)} {random.randint(1, 50)}" if random.random() > 0.5 else ""
        
        if locality:
            return f"{house_num}, {street}, {locality}, {city}"
        return f"{house_num}, {street}, {city}"
    
    def generate_digital_address(self, city: str, index: int) -> str:
        """Generate a digital address in email format."""
        prefixes = ["home", "office", "shop", "flat", "house", "bungalow"]
        city_code = city.lower().replace(" ", "")[:6]
        return f"{random.choice(prefixes)}{index}@{city_code}.address.in"
    
    # -------------------------------------------------------------------------
    # AGENT GENERATION
    # -------------------------------------------------------------------------
    
    def generate_agents(self, count: int = 12) -> List[str]:
        """Generate sample agents."""
        print(f"\n👤 Generating {count} agents...")
        
        agent_ids = []
        
        for i in range(min(count, len(AGENT_NAMES))):
            first, last = AGENT_NAMES[i]
            name = f"{first} {last}"
            email = f"{first.lower()}.{last.lower()}@aava.in"
            
            # Check if already exists
            existing = self.db.get_agent_by_email(email)
            if existing:
                print(f"  ⚠ Agent {name} already exists, skipping...")
                agent_ids.append(existing['id'])
                continue
            
            # Random certification dates
            cert_date = datetime.now() - timedelta(days=random.randint(60, 400))
            cert_expiry = cert_date + timedelta(days=365)
            
            # Performance based on experience
            days_active = (datetime.now() - cert_date).days
            base_perf = 0.7 + (days_active / 1000) * 0.2
            performance = min(0.98, base_perf + random.gauss(0, 0.05))
            
            agent_id = self.db.create_agent({
                'name': name,
                'email': email,
                'phone': self.generate_phone(),
                'certification_date': cert_date.strftime('%Y-%m-%d'),
                'certification_expiry': cert_expiry.strftime('%Y-%m-%d'),
                'active': 1 if random.random() > 0.1 else 0,
                'performance_score': round(performance, 3)
            })
            
            agent_ids.append(agent_id)
            print(f"  ✓ Created agent: {name} ({agent_id})")
        
        self.agent_ids = agent_ids
        return agent_ids
    
    # -------------------------------------------------------------------------
    # ADDRESS GENERATION
    # -------------------------------------------------------------------------
    
    def generate_addresses(self, count: int = 75) -> List[str]:
        """Generate sample addresses across cities."""
        print(f"\n📍 Generating {count} addresses...")
        
        address_ids = []
        cities = list(INDIAN_CITIES.keys())
        
        for i in range(count):
            # Distribute across cities
            city = cities[i % len(cities)]
            base_lat, base_lon, state, base_pincode = INDIAN_CITIES[city]
            
            # Add random offset (within ~5km)
            lat = base_lat + random.gauss(0, 0.02)
            lon = base_lon + random.gauss(0, 0.02)
            
            # Generate DIGIPIN
            result = self.validator.encode(lat, lon)
            digipin = result.digipin
            
            # Generate address details
            digital_addr = self.generate_digital_address(city, i + 1)
            street_addr = self.generate_street_address(city)
            
            # Vary pincode slightly
            pincode_num = int(base_pincode) + random.randint(0, 99)
            pincode = str(pincode_num).zfill(6)
            
            # Generate confidence score (normal distribution around 70)
            confidence = max(0, min(100, random.gauss(70, 15)))
            grade = get_grade(confidence)
            
            address_id = self.db.create_address({
                'digital_address': digital_addr,
                'digipin': digipin,
                'descriptive_address': street_addr,
                'latitude': round(lat, 6),
                'longitude': round(lon, 6),
                'city': city,
                'state': state,
                'pincode': pincode,
                'confidence_score': round(confidence, 2),
                'confidence_grade': grade
            })
            
            address_ids.append(address_id)
            
            if (i + 1) % 10 == 0:
                print(f"  ✓ Created {i + 1} addresses...")
        
        self.address_ids = address_ids
        print(f"  ✓ Total: {len(address_ids)} addresses created")
        return address_ids
    
    # -------------------------------------------------------------------------
    # DELIVERY GENERATION
    # -------------------------------------------------------------------------
    
    def generate_deliveries(self, per_address: int = 12) -> int:
        """Generate delivery records for each address."""
        print(f"\n📦 Generating ~{per_address} deliveries per address...")
        
        if not self.address_ids:
            print("  ⚠ No addresses found. Generate addresses first.")
            return 0
        
        total = 0
        
        for addr_id in self.address_ids:
            # Get address for reference
            addr = self.db.get_address(addr_id)
            if not addr:
                continue
            
            # Variable number of deliveries
            num_deliveries = per_address + random.randint(-5, 5)
            num_deliveries = max(3, num_deliveries)
            
            for j in range(num_deliveries):
                # Determine delivery outcome
                roll = random.random()
                if roll < 0.75:
                    status = "DELIVERED"
                    ease_rating = random.randint(3, 5)
                    offset = random.gauss(0, 0.0003)
                elif roll < 0.90:
                    status = "DELIVERED_WITH_DIFFICULTY"
                    ease_rating = random.randint(1, 3)
                    offset = random.gauss(0, 0.001)
                else:
                    status = "FAILED"
                    ease_rating = None
                    offset = random.gauss(0, 0.002)
                
                # Random timestamp in past 180 days
                days_ago = random.randint(1, 180)
                timestamp = datetime.now() - timedelta(
                    days=days_ago,
                    hours=random.randint(8, 20),
                    minutes=random.randint(0, 59)
                )
                
                self.db.create_delivery({
                    'address_id': addr_id,
                    'status': status,
                    'actual_latitude': addr['latitude'] + offset,
                    'actual_longitude': addr['longitude'] + offset,
                    'distance_from_stated': abs(offset) * 111000,  # Approx meters
                    'ease_rating': ease_rating,
                    'delivery_partner': random.choice(DELIVERY_PARTNERS),
                    'timestamp': timestamp.isoformat()
                })
                
                total += 1
        
        print(f"  ✓ Total: {total} delivery records created")
        return total
    
    # -------------------------------------------------------------------------
    # VALIDATION GENERATION
    # -------------------------------------------------------------------------
    
    def generate_validations(self, percentage: float = 0.6) -> List[str]:
        """Generate validation requests for a percentage of addresses."""
        num_validations = int(len(self.address_ids) * percentage)
        print(f"\n📋 Generating {num_validations} validations...")
        
        if not self.address_ids:
            print("  ⚠ No addresses found. Generate addresses first.")
            return []
        
        validation_ids = []
        selected_addresses = random.sample(self.address_ids, num_validations)
        
        for addr_id in selected_addresses:
            addr = self.db.get_address(addr_id)
            if not addr:
                continue
            
            # Random validation type weighted toward HYBRID
            val_type = random.choices(
                ["PHYSICAL", "DIGITAL", "HYBRID"],
                weights=[0.2, 0.3, 0.5]
            )[0]
            
            # Random status weighted toward completed
            status = random.choices(
                ["PENDING", "IN_PROGRESS", "COMPLETED", "FAILED"],
                weights=[0.15, 0.1, 0.65, 0.1]
            )[0]
            
            # Priority distribution
            priority = random.choices(
                ["LOW", "NORMAL", "HIGH", "URGENT"],
                weights=[0.1, 0.5, 0.3, 0.1]
            )[0]
            
            # Assign agent for non-pending
            agent_id = None
            if status != "PENDING" and self.agent_ids:
                agent_id = random.choice(self.agent_ids)
            
            validation_id = self.db.create_validation({
                'address_id': addr_id,
                'digital_address': addr.get('digital_address'),
                'digipin': addr.get('digipin'),
                'descriptive_address': addr.get('descriptive_address'),
                'validation_type': val_type,
                'status': status,
                'priority': priority,
                'assigned_agent_id': agent_id,
                'notes': f"Auto-generated validation request for {addr.get('city', 'unknown city')}"
            })
            
            validation_ids.append(validation_id)
        
        self.validation_ids = validation_ids
        print(f"  ✓ Total: {len(validation_ids)} validations created")
        return validation_ids
    
    # -------------------------------------------------------------------------
    # VERIFICATION GENERATION
    # -------------------------------------------------------------------------
    
    def generate_verifications(self) -> int:
        """Generate verifications for completed validations."""
        print(f"\n✅ Generating verifications for completed validations...")
        
        if not self.validation_ids:
            print("  ⚠ No validations found. Generate validations first.")
            return 0
        
        total = 0
        
        for val_id in self.validation_ids:
            val = self.db.get_validation(val_id)
            if not val or val.get('status') != 'COMPLETED':
                continue
            
            if not val.get('assigned_agent_id'):
                continue
            
            # Get address for GPS data
            addr = self.db.get_address(val.get('address_id'))
            if not addr:
                continue
            
            # Verification details
            verified = 1 if random.random() > 0.1 else 0
            quality = random.uniform(0.75, 0.98) if verified else random.uniform(0.3, 0.6)
            
            evidence_types = ['photo', 'photo+signature', 'video', 'photo+video']
            
            self.db.create_verification({
                'validation_id': val_id,
                'agent_id': val.get('assigned_agent_id'),
                'verified': verified,
                'quality_score': round(quality, 3),
                'evidence_type': random.choice(evidence_types),
                'photos': json.dumps(['evidence_1.jpg', 'evidence_2.jpg']),
                'gps_latitude': addr['latitude'] + random.gauss(0, 0.0001),
                'gps_longitude': addr['longitude'] + random.gauss(0, 0.0001),
                'gps_accuracy': random.uniform(3, 15),
                'notes': 'Physical verification completed successfully.' if verified else 'Address not found at location.'
            })
            
            total += 1
        
        print(f"  ✓ Total: {total} verifications created")
        return total
    
    # -------------------------------------------------------------------------
    # CONSENT GENERATION
    # -------------------------------------------------------------------------
    
    def generate_consents(self) -> int:
        """Generate consent records for validations."""
        print(f"\n📜 Generating consent records...")
        
        if not self.validation_ids:
            return 0
        
        total = 0
        
        for val_id in self.validation_ids:
            val = self.db.get_validation(val_id)
            if not val:
                continue
            
            # Random consent expiry
            expires = datetime.now() + timedelta(days=random.randint(30, 365))
            
            consent_id = self.db.create_consent({
                'subject_id': val.get('address_id'),
                'granter': val.get('digital_address', 'unknown'),
                'grantee': 'AAVA System',
                'scope': ['validation', 'verification', 'delivery_history'],
                'consent_artifact': f"CONSENT-{val_id[:8]}",
                'expires_at': expires.isoformat()
            })
            
            # Update validation with consent
            self.db.update_validation(val_id, {'consent_id': consent_id})
            
            total += 1
        
        print(f"  ✓ Total: {total} consent records created")
        return total
    
    # -------------------------------------------------------------------------
    # AUDIT LOG GENERATION
    # -------------------------------------------------------------------------
    
    def generate_audit_logs(self) -> int:
        """Generate audit log entries."""
        print(f"\n📝 Generating audit logs...")
        
        actors = ['system', 'admin', 'api'] + [f'agent:{aid}' for aid in self.agent_ids[:5]]
        actions = [
            'validation.created', 'validation.updated', 'validation.completed',
            'verification.submitted', 'verification.approved',
            'consent.granted', 'consent.revoked',
            'agent.login', 'agent.logout',
            'report.generated', 'data.exported'
        ]
        
        total = 50  # Generate 50 audit entries
        
        for i in range(total):
            days_ago = random.randint(0, 60)
            timestamp = datetime.now() - timedelta(days=days_ago)
            
            action = random.choice(actions)
            resource_type = action.split('.')[0]
            
            # Get a random resource ID
            if resource_type == 'validation' and self.validation_ids:
                resource_id = random.choice(self.validation_ids)
            elif resource_type == 'agent' and self.agent_ids:
                resource_id = random.choice(self.agent_ids)
            else:
                resource_id = f"RESOURCE-{i:04d}"
            
            self.db.log_audit({
                'actor': random.choice(actors),
                'action': action,
                'resource_type': resource_type,
                'resource_id': resource_id,
                'details': {'sample': True, 'generated': True}
            })
        
        print(f"  ✓ Total: {total} audit log entries created")
        return total
    
    # -------------------------------------------------------------------------
    # MAIN GENERATION
    # -------------------------------------------------------------------------
    
    def generate_all(
        self,
        num_agents: int = 12,
        num_addresses: int = 75,
        deliveries_per_address: int = 12,
        validation_percentage: float = 0.6
    ) -> Dict:
        """Generate all sample data."""
        print("=" * 70)
        print("AAVA SAMPLE DATA GENERATOR")
        print("=" * 70)
        
        start_time = datetime.now()
        
        # Generate in order
        agents = self.generate_agents(num_agents)
        addresses = self.generate_addresses(num_addresses)
        deliveries = self.generate_deliveries(deliveries_per_address)
        validations = self.generate_validations(validation_percentage)
        verifications = self.generate_verifications()
        consents = self.generate_consents()
        audit_logs = self.generate_audit_logs()
        
        duration = (datetime.now() - start_time).total_seconds()
        
        summary = {
            'agents': len(agents),
            'addresses': len(addresses),
            'deliveries': deliveries,
            'validations': len(validations),
            'verifications': verifications,
            'consents': consents,
            'audit_logs': audit_logs,
            'duration_seconds': round(duration, 2)
        }
        
        print("\n" + "=" * 70)
        print("GENERATION COMPLETE")
        print("=" * 70)
        print(f"\nSummary:")
        for key, value in summary.items():
            print(f"  • {key}: {value}")
        print(f"\nDuration: {duration:.2f} seconds")
        print("=" * 70)
        
        return summary


# =============================================================================
# CLI ENTRY POINT
# =============================================================================

def main():
    """Run sample data generation from command line."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate sample data for AAVA system"
    )
    parser.add_argument(
        '--agents', type=int, default=12,
        help='Number of agents to create (default: 12)'
    )
    parser.add_argument(
        '--addresses', type=int, default=75,
        help='Number of addresses to create (default: 75)'
    )
    parser.add_argument(
        '--deliveries', type=int, default=12,
        help='Deliveries per address (default: 12)'
    )
    parser.add_argument(
        '--validation-pct', type=float, default=0.6,
        help='Percentage of addresses to validate (default: 0.6)'
    )
    parser.add_argument(
        '--db-path', type=str, default='data/aava.db',
        help='Database file path (default: data/aava.db)'
    )
    
    args = parser.parse_args()
    
    # Initialize database
    db = DatabaseManager(args.db_path)
    db.initialize()
    
    # Generate data
    generator = SampleDataGenerator(db)
    summary = generator.generate_all(
        num_agents=args.agents,
        num_addresses=args.addresses,
        deliveries_per_address=args.deliveries,
        validation_percentage=args.validation_pct
    )
    
    return summary


if __name__ == "__main__":
    main()
