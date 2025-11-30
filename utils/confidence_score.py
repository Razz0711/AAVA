# utils/confidence_score.py
# Confidence Score Calculator for AAVA
# Calculates address validation confidence based on 4 weighted components
# 
# AAVA - Authorised Address Validation Agency
# DHRUVA Digital Address Ecosystem

"""
Confidence Score Algorithm
===========================

The confidence score (0-100) measures how reliable an address is based on
historical data and verification status.

Components and Weights:
-----------------------
1. Delivery Success Rate (DSR) - 30%
   - Based on historical delivery outcomes
   - Success=100, Partial=50, Failed=0 points
   - Formula: (sum of points) / (count * 100)

2. Spatial Consistency (SC) - 30%
   - How tightly deliveries cluster around stated coordinates
   - Uses average distance from declared position
   - Formula: exp(-(avg_distance / reference_distance)^2)

3. Temporal Freshness (TF) - 20%
   - Time since last successful verification
   - Exponential decay over time
   - Formula: exp(-lambda * days_since_last)
   - Half-life: 180 days (adjustable)

4. Physical Verification Status (PVS) - 20%
   - Whether address was physically verified by agent
   - Includes verification quality score
   - Formula: verified_flag * quality_score * freshness_decay

Final Score:
   S = 100 * (0.30*DSR + 0.30*SC + 0.20*TF + 0.20*PVS)

Grades:
   A+ : 90-100
   A  : 80-89
   B  : 70-79
   C  : 60-69
   D  : 50-59
   F  : 0-49
"""

import math
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum


# =============================================================================
# ENUMS AND CONSTANTS
# =============================================================================

class DeliveryStatus(Enum):
    """Delivery outcome status."""
    DELIVERED = "DELIVERED"
    DELIVERED_WITH_DIFFICULTY = "DELIVERED_WITH_DIFFICULTY"
    FAILED = "FAILED"
    PENDING = "PENDING"

# Points for each delivery status
DELIVERY_POINTS = {
    DeliveryStatus.DELIVERED: 100,
    DeliveryStatus.DELIVERED_WITH_DIFFICULTY: 50,
    DeliveryStatus.FAILED: 0,
    DeliveryStatus.PENDING: None  # Not counted
}

# Component weights (must sum to 1.0)
WEIGHTS = {
    'delivery_success': 0.30,
    'spatial_consistency': 0.30,
    'temporal_freshness': 0.20,
    'physical_verification': 0.20
}

# Grade thresholds
GRADE_THRESHOLDS = [
    (90, 'A+', 'Excellent - Highly Reliable'),
    (80, 'A', 'Very Good - Reliable'),
    (70, 'B', 'Good - Mostly Reliable'),
    (60, 'C', 'Fair - Moderately Reliable'),
    (50, 'D', 'Poor - Low Reliability'),
    (0, 'F', 'Fail - Unreliable')
]

# Default parameters
DEFAULT_HALF_LIFE_DAYS = 180  # Days for temporal decay half-life
DEFAULT_REFERENCE_DISTANCE = 50  # Meters for spatial consistency reference


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class DeliveryRecord:
    """Single delivery attempt record."""
    id: str
    timestamp: datetime
    status: DeliveryStatus
    actual_lat: Optional[float] = None
    actual_lon: Optional[float] = None
    ease_rating: Optional[int] = None  # 1-5 scale
    notes: Optional[str] = None


@dataclass
class PhysicalVerification:
    """Physical verification record by agent."""
    id: str
    agent_id: str
    timestamp: datetime
    verified: bool
    quality_score: float  # 0.0 to 1.0
    evidence_type: str  # 'photo', 'video', 'signature', etc.
    gps_accuracy: float  # meters
    notes: Optional[str] = None


@dataclass
class AddressData:
    """Complete address data for scoring."""
    address_id: str
    stated_lat: float
    stated_lon: float
    created_at: datetime
    deliveries: List[DeliveryRecord] = field(default_factory=list)
    verifications: List[PhysicalVerification] = field(default_factory=list)
    last_updated: Optional[datetime] = None


@dataclass
class ScoreComponent:
    """Individual score component result."""
    name: str
    raw_value: float  # 0.0 to 1.0
    weighted_value: float
    weight: float
    description: str
    data_points: int  # Number of records used


@dataclass
class ConfidenceResult:
    """Complete confidence score result."""
    score: float  # 0-100
    grade: str
    grade_description: str
    components: Dict[str, ScoreComponent]
    computed_at: datetime
    coverage: Dict[str, bool]  # Which components had data
    recommendations: List[str]


# =============================================================================
# CONFIDENCE SCORE CALCULATOR CLASS
# =============================================================================

class ConfidenceScoreCalculator:
    """
    Calculate confidence scores for addresses based on historical data.
    
    Usage:
        calculator = ConfidenceScoreCalculator()
        
        # Create address data
        address = AddressData(
            address_id="addr-001",
            stated_lat=28.6139,
            stated_lon=77.2090,
            created_at=datetime.now() - timedelta(days=90),
            deliveries=[...],
            verifications=[...]
        )
        
        # Calculate score
        result = calculator.calculate(address)
        print(f"Score: {result.score}, Grade: {result.grade}")
    """
    
    def __init__(
        self,
        weights: Dict[str, float] = None,
        half_life_days: float = DEFAULT_HALF_LIFE_DAYS,
        reference_distance: float = DEFAULT_REFERENCE_DISTANCE
    ):
        """
        Initialize the calculator.
        
        Args:
            weights: Custom component weights (must sum to 1.0)
            half_life_days: Half-life for temporal decay
            reference_distance: Reference distance for spatial scoring (meters)
        """
        self.weights = weights or WEIGHTS.copy()
        self.half_life_days = half_life_days
        self.reference_distance = reference_distance
        self.lambda_decay = math.log(2) / half_life_days
        
        # Validate weights
        weight_sum = sum(self.weights.values())
        if abs(weight_sum - 1.0) > 0.001:
            raise ValueError(f"Weights must sum to 1.0, got {weight_sum}")
    
    # -------------------------------------------------------------------------
    # MAIN CALCULATION METHOD
    # -------------------------------------------------------------------------
    
    def calculate(
        self, 
        address: AddressData,
        as_of_date: datetime = None
    ) -> ConfidenceResult:
        """
        Calculate the complete confidence score for an address.
        
        Args:
            address: Address data with history
            as_of_date: Calculate as of this date (default: now)
            
        Returns:
            ConfidenceResult with score, grade, and component details
        """
        as_of_date = as_of_date or datetime.now()
        
        # Calculate each component
        dsr = self._calculate_delivery_success(address.deliveries)
        sc = self._calculate_spatial_consistency(
            address.deliveries, 
            address.stated_lat, 
            address.stated_lon
        )
        tf = self._calculate_temporal_freshness(
            address.deliveries,
            address.verifications,
            as_of_date
        )
        pvs = self._calculate_physical_verification(
            address.verifications,
            as_of_date
        )
        
        # Build components dictionary
        components = {
            'delivery_success': ScoreComponent(
                name='Delivery Success Rate',
                raw_value=dsr['value'],
                weighted_value=dsr['value'] * self.weights['delivery_success'],
                weight=self.weights['delivery_success'],
                description=dsr['description'],
                data_points=dsr['data_points']
            ),
            'spatial_consistency': ScoreComponent(
                name='Spatial Consistency',
                raw_value=sc['value'],
                weighted_value=sc['value'] * self.weights['spatial_consistency'],
                weight=self.weights['spatial_consistency'],
                description=sc['description'],
                data_points=sc['data_points']
            ),
            'temporal_freshness': ScoreComponent(
                name='Temporal Freshness',
                raw_value=tf['value'],
                weighted_value=tf['value'] * self.weights['temporal_freshness'],
                weight=self.weights['temporal_freshness'],
                description=tf['description'],
                data_points=tf['data_points']
            ),
            'physical_verification': ScoreComponent(
                name='Physical Verification',
                raw_value=pvs['value'],
                weighted_value=pvs['value'] * self.weights['physical_verification'],
                weight=self.weights['physical_verification'],
                description=pvs['description'],
                data_points=pvs['data_points']
            )
        }
        
        # Calculate final score
        total_weighted = sum(c.weighted_value for c in components.values())
        score = round(total_weighted * 100, 2)
        score = max(0, min(100, score))  # Clamp to 0-100
        
        # Get grade
        grade, grade_description = self._get_grade(score)
        
        # Determine coverage
        coverage = {
            'has_deliveries': len(address.deliveries) > 0,
            'has_coordinates': any(
                d.actual_lat is not None and d.actual_lon is not None 
                for d in address.deliveries
            ),
            'has_verifications': len(address.verifications) > 0,
            'is_recent': tf['value'] > 0.5
        }
        
        # Generate recommendations
        recommendations = self._generate_recommendations(components, coverage)
        
        return ConfidenceResult(
            score=score,
            grade=grade,
            grade_description=grade_description,
            components=components,
            computed_at=as_of_date,
            coverage=coverage,
            recommendations=recommendations
        )
    
    # -------------------------------------------------------------------------
    # COMPONENT CALCULATIONS
    # -------------------------------------------------------------------------
    
    def _calculate_delivery_success(
        self, 
        deliveries: List[DeliveryRecord]
    ) -> Dict[str, Any]:
        """
        Calculate Delivery Success Rate (DSR).
        
        Formula:
            DSR = Σ(points for each delivery) / (N × 100)
            
        Where points:
            - DELIVERED: 100
            - DELIVERED_WITH_DIFFICULTY: 50
            - FAILED: 0
        """
        # Filter out pending deliveries
        completed = [
            d for d in deliveries 
            if d.status != DeliveryStatus.PENDING
        ]
        
        if not completed:
            return {
                'value': 0.0,
                'description': 'No delivery history',
                'data_points': 0
            }
        
        # Calculate total points
        total_points = 0
        for delivery in completed:
            points = DELIVERY_POINTS.get(delivery.status, 0)
            if points is not None:
                total_points += points
        
        # Normalize
        max_possible = len(completed) * 100
        dsr = total_points / max_possible if max_possible > 0 else 0
        
        # Count by status
        status_counts = {}
        for d in completed:
            status_counts[d.status.value] = status_counts.get(d.status.value, 0) + 1
        
        description = f"{len(completed)} deliveries: " + ", ".join(
            f"{count} {status.lower()}" 
            for status, count in status_counts.items()
        )
        
        return {
            'value': dsr,
            'description': description,
            'data_points': len(completed)
        }
    
    def _calculate_spatial_consistency(
        self,
        deliveries: List[DeliveryRecord],
        stated_lat: float,
        stated_lon: float
    ) -> Dict[str, Any]:
        """
        Calculate Spatial Consistency (SC).
        
        Measures how tightly delivery coordinates cluster around the stated address.
        
        Formula:
            avg_distance = mean(distance(delivery_coords, stated_coords))
            SC = exp(-(avg_distance / reference_distance)²)
        """
        # Get deliveries with coordinates
        with_coords = [
            d for d in deliveries
            if d.actual_lat is not None and d.actual_lon is not None
        ]
        
        if not with_coords:
            return {
                'value': 0.0,
                'description': 'No coordinate data from deliveries',
                'data_points': 0
            }
        
        # Calculate distances
        distances = []
        for d in with_coords:
            dist = self._haversine_distance(
                stated_lat, stated_lon,
                d.actual_lat, d.actual_lon
            )
            distances.append(dist)
        
        # Calculate average distance
        avg_distance = sum(distances) / len(distances)
        
        # Apply Gaussian-like scoring
        # Score decreases as average distance increases
        sc = math.exp(-((avg_distance / self.reference_distance) ** 2))
        
        description = f"Avg distance: {avg_distance:.1f}m from {len(with_coords)} points"
        
        return {
            'value': sc,
            'description': description,
            'data_points': len(with_coords),
            'avg_distance': avg_distance
        }
    
    def _calculate_temporal_freshness(
        self,
        deliveries: List[DeliveryRecord],
        verifications: List[PhysicalVerification],
        as_of_date: datetime
    ) -> Dict[str, Any]:
        """
        Calculate Temporal Freshness (TF).
        
        Based on time since last successful event (delivery or verification).
        
        Formula:
            TF = exp(-λ × days_since_last)
            where λ = ln(2) / half_life_days
        """
        # Find most recent successful event
        last_event_date = None
        
        # Check deliveries
        for d in deliveries:
            if d.status in [DeliveryStatus.DELIVERED, DeliveryStatus.DELIVERED_WITH_DIFFICULTY]:
                if last_event_date is None or d.timestamp > last_event_date:
                    last_event_date = d.timestamp
        
        # Check verifications
        for v in verifications:
            if v.verified:
                if last_event_date is None or v.timestamp > last_event_date:
                    last_event_date = v.timestamp
        
        if last_event_date is None:
            return {
                'value': 0.0,
                'description': 'No successful events recorded',
                'data_points': 0
            }
        
        # Calculate days since last event
        days_since = (as_of_date - last_event_date).days
        days_since = max(0, days_since)  # Handle future dates
        
        # Apply exponential decay
        tf = math.exp(-self.lambda_decay * days_since)
        
        description = f"Last event: {days_since} days ago (half-life: {self.half_life_days} days)"
        
        return {
            'value': tf,
            'description': description,
            'data_points': 1,
            'days_since': days_since
        }
    
    def _calculate_physical_verification(
        self,
        verifications: List[PhysicalVerification],
        as_of_date: datetime
    ) -> Dict[str, Any]:
        """
        Calculate Physical Verification Status (PVS).
        
        Based on whether address was physically verified and quality of verification.
        
        Formula:
            PVS = verified × quality_score × freshness_factor
        """
        if not verifications:
            return {
                'value': 0.1,  # Small baseline for unverified
                'description': 'Not physically verified',
                'data_points': 0
            }
        
        # Find the best and most recent verification
        verified_list = [v for v in verifications if v.verified]
        
        if not verified_list:
            return {
                'value': 0.1,
                'description': 'Physical verification failed/incomplete',
                'data_points': len(verifications)
            }
        
        # Get most recent successful verification
        latest = max(verified_list, key=lambda v: v.timestamp)
        
        # Calculate freshness factor for this verification
        days_since = (as_of_date - latest.timestamp).days
        freshness_factor = math.exp(-self.lambda_decay * days_since)
        
        # Combine quality and freshness
        pvs = latest.quality_score * freshness_factor
        
        description = (
            f"Verified by agent {latest.agent_id}, "
            f"quality: {latest.quality_score:.0%}, "
            f"{days_since} days ago"
        )
        
        return {
            'value': pvs,
            'description': description,
            'data_points': len(verified_list)
        }
    
    # -------------------------------------------------------------------------
    # HELPER METHODS
    # -------------------------------------------------------------------------
    
    def _get_grade(self, score: float) -> Tuple[str, str]:
        """Get letter grade and description for a score."""
        for threshold, grade, description in GRADE_THRESHOLDS:
            if score >= threshold:
                return grade, description
        return 'F', 'Fail - Unreliable'
    
    def _generate_recommendations(
        self,
        components: Dict[str, ScoreComponent],
        coverage: Dict[str, bool]
    ) -> List[str]:
        """Generate improvement recommendations based on scores."""
        recommendations = []
        
        # Check each component
        if components['delivery_success'].raw_value < 0.7:
            recommendations.append(
                "Improve delivery success by validating address details"
            )
        
        if components['spatial_consistency'].raw_value < 0.7:
            recommendations.append(
                "Address location may need correction - high delivery variance"
            )
        
        if components['temporal_freshness'].raw_value < 0.5:
            recommendations.append(
                "Address data is stale - schedule re-verification"
            )
        
        if components['physical_verification'].raw_value < 0.5:
            recommendations.append(
                "Request physical verification by field agent"
            )
        
        if not coverage['has_deliveries']:
            recommendations.append(
                "No delivery history - confidence score based on limited data"
            )
        
        if not coverage['has_verifications']:
            recommendations.append(
                "No physical verification - consider agent verification"
            )
        
        return recommendations
    
    def _haversine_distance(
        self,
        lat1: float, lon1: float,
        lat2: float, lon2: float
    ) -> float:
        """Calculate distance between two points in meters."""
        R = 6371000  # Earth radius in meters
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (
            math.sin(delta_lat / 2) ** 2 +
            math.cos(lat1_rad) * math.cos(lat2_rad) *
            math.sin(delta_lon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c


# =============================================================================
# SAMPLE DATA GENERATOR
# =============================================================================

class SampleDataGenerator:
    """Generate sample data for testing and demonstrations."""
    
    # Major Indian cities with coordinates
    CITIES = [
        ("New Delhi", 28.6139, 77.2090),
        ("Mumbai", 19.0760, 72.8777),
        ("Bangalore", 12.9716, 77.5946),
        ("Chennai", 13.0827, 80.2707),
        ("Kolkata", 22.5726, 88.3639),
        ("Hyderabad", 17.3850, 78.4867),
        ("Pune", 18.5204, 73.8567),
        ("Ahmedabad", 23.0225, 72.5714),
        ("Jaipur", 26.9124, 75.7873),
        ("Lucknow", 26.8467, 80.9462),
    ]
    
    AGENT_NAMES = [
        "Rahul Kumar", "Priya Sharma", "Amit Singh", "Neha Patel",
        "Vikram Reddy", "Anjali Gupta", "Rajesh Verma", "Sunita Devi",
        "Mohit Agarwal", "Kavita Nair"
    ]
    
    @classmethod
    def generate_address(
        cls,
        address_id: str = None,
        city_index: int = None,
        num_deliveries: int = None,
        num_verifications: int = None,
        success_rate: float = None
    ) -> AddressData:
        """
        Generate a sample address with history.
        
        Args:
            address_id: Custom address ID (or generated)
            city_index: Which city to use (random if None)
            num_deliveries: Number of delivery records (random 5-20 if None)
            num_verifications: Number of verifications (random 0-2 if None)
            success_rate: Delivery success rate (random if None)
            
        Returns:
            AddressData with generated history
        """
        # Select city
        if city_index is None:
            city_index = random.randint(0, len(cls.CITIES) - 1)
        city_name, base_lat, base_lon = cls.CITIES[city_index]
        
        # Add small random offset to create unique address
        lat = base_lat + random.uniform(-0.02, 0.02)
        lon = base_lon + random.uniform(-0.02, 0.02)
        
        # Generate ID
        if address_id is None:
            address_id = f"ADDR-{random.randint(100000, 999999)}"
        
        # Generate creation date (1-365 days ago)
        days_ago = random.randint(30, 365)
        created_at = datetime.now() - timedelta(days=days_ago)
        
        # Generate deliveries
        if num_deliveries is None:
            num_deliveries = random.randint(5, 20)
        
        if success_rate is None:
            success_rate = random.uniform(0.5, 0.95)
        
        deliveries = cls._generate_deliveries(
            num_deliveries, success_rate, lat, lon, created_at
        )
        
        # Generate verifications
        if num_verifications is None:
            num_verifications = random.randint(0, 2)
        
        verifications = cls._generate_verifications(
            num_verifications, created_at
        )
        
        return AddressData(
            address_id=address_id,
            stated_lat=lat,
            stated_lon=lon,
            created_at=created_at,
            deliveries=deliveries,
            verifications=verifications,
            last_updated=datetime.now()
        )
    
    @classmethod
    def _generate_deliveries(
        cls,
        count: int,
        success_rate: float,
        stated_lat: float,
        stated_lon: float,
        start_date: datetime
    ) -> List[DeliveryRecord]:
        """Generate delivery records."""
        deliveries = []
        
        for i in range(count):
            # Random date between start and now
            days_offset = random.randint(0, (datetime.now() - start_date).days)
            timestamp = start_date + timedelta(
                days=days_offset,
                hours=random.randint(8, 20),
                minutes=random.randint(0, 59)
            )
            
            # Determine status based on success rate
            rand = random.random()
            if rand < success_rate * 0.8:
                status = DeliveryStatus.DELIVERED
            elif rand < success_rate:
                status = DeliveryStatus.DELIVERED_WITH_DIFFICULTY
            else:
                status = DeliveryStatus.FAILED
            
            # Generate coordinates with some variance
            # Good addresses have low variance, bad ones have high variance
            variance = 0.0001 if success_rate > 0.7 else 0.0005
            actual_lat = stated_lat + random.gauss(0, variance)
            actual_lon = stated_lon + random.gauss(0, variance)
            
            deliveries.append(DeliveryRecord(
                id=f"DEL-{random.randint(100000, 999999)}",
                timestamp=timestamp,
                status=status,
                actual_lat=actual_lat if status != DeliveryStatus.FAILED else None,
                actual_lon=actual_lon if status != DeliveryStatus.FAILED else None,
                ease_rating=random.randint(1, 5) if status == DeliveryStatus.DELIVERED else None,
                notes=None
            ))
        
        return sorted(deliveries, key=lambda d: d.timestamp)
    
    @classmethod
    def _generate_verifications(
        cls,
        count: int,
        start_date: datetime
    ) -> List[PhysicalVerification]:
        """Generate physical verification records."""
        verifications = []
        
        for i in range(count):
            days_offset = random.randint(0, (datetime.now() - start_date).days)
            timestamp = start_date + timedelta(days=days_offset)
            
            verifications.append(PhysicalVerification(
                id=f"VER-{random.randint(100000, 999999)}",
                agent_id=f"AGT-{random.randint(1, 100):03d}",
                timestamp=timestamp,
                verified=random.random() > 0.1,  # 90% success rate
                quality_score=random.uniform(0.7, 1.0),
                evidence_type=random.choice(['photo', 'photo+signature', 'video']),
                gps_accuracy=random.uniform(3, 15),
                notes=None
            ))
        
        return sorted(verifications, key=lambda v: v.timestamp)
    
    @classmethod
    def generate_dataset(cls, num_addresses: int = 50) -> List[AddressData]:
        """Generate a complete dataset of sample addresses."""
        addresses = []
        
        # Generate addresses with varying quality
        for i in range(num_addresses):
            # Create different quality profiles
            if i < num_addresses * 0.2:
                # Excellent addresses (top 20%)
                success_rate = random.uniform(0.9, 1.0)
                num_deliveries = random.randint(15, 25)
                num_verifications = random.randint(1, 3)
            elif i < num_addresses * 0.5:
                # Good addresses (next 30%)
                success_rate = random.uniform(0.75, 0.9)
                num_deliveries = random.randint(10, 20)
                num_verifications = random.randint(0, 2)
            elif i < num_addresses * 0.8:
                # Average addresses (next 30%)
                success_rate = random.uniform(0.6, 0.75)
                num_deliveries = random.randint(5, 15)
                num_verifications = random.randint(0, 1)
            else:
                # Poor addresses (bottom 20%)
                success_rate = random.uniform(0.3, 0.6)
                num_deliveries = random.randint(3, 10)
                num_verifications = 0
            
            address = cls.generate_address(
                address_id=f"ADDR-{i+1:06d}",
                city_index=i % len(cls.CITIES),
                num_deliveries=num_deliveries,
                num_verifications=num_verifications,
                success_rate=success_rate
            )
            addresses.append(address)
        
        return addresses


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def calculate_score(address: AddressData) -> float:
    """Quick function to calculate just the score value."""
    calculator = ConfidenceScoreCalculator()
    result = calculator.calculate(address)
    return result.score

def get_grade(score: float) -> str:
    """Get letter grade for a score."""
    for threshold, grade, _ in GRADE_THRESHOLDS:
        if score >= threshold:
            return grade
    return 'F'

def get_grade_color(grade: str) -> str:
    """Get color for a grade (for UI display)."""
    colors = {
        'A+': '#00C853',  # Green
        'A': '#00E676',
        'B': '#FFEB3B',   # Yellow
        'C': '#FFC107',   # Amber
        'D': '#FF9800',   # Orange
        'F': '#F44336',   # Red
    }
    return colors.get(grade, '#9E9E9E')


# =============================================================================
# TEST CODE
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("CONFIDENCE SCORE CALCULATOR - TEST SUITE")
    print("=" * 70)
    
    # Initialize calculator
    calculator = ConfidenceScoreCalculator()
    
    print("\n📊 ALGORITHM OVERVIEW")
    print("-" * 70)
    print("""
    Score = 100 × (0.30×DSR + 0.30×SC + 0.20×TF + 0.20×PVS)
    
    Components:
    • DSR (Delivery Success Rate): Based on delivery outcomes
    • SC (Spatial Consistency): How tightly deliveries cluster
    • TF (Temporal Freshness): Time since last event
    • PVS (Physical Verification): Agent verification status
    """)
    
    print("\n📦 GENERATING SAMPLE DATA")
    print("-" * 70)
    
    # Generate sample addresses with different profiles
    test_cases = [
        ("Excellent Address (90+ expected)", 0.95, 20, 2),
        ("Good Address (75-85 expected)", 0.80, 15, 1),
        ("Average Address (60-70 expected)", 0.65, 10, 0),
        ("Poor Address (<50 expected)", 0.40, 5, 0),
    ]
    
    for name, success_rate, num_del, num_ver in test_cases:
        print(f"\n{name}")
        print("-" * 50)
        
        address = SampleDataGenerator.generate_address(
            success_rate=success_rate,
            num_deliveries=num_del,
            num_verifications=num_ver
        )
        
        result = calculator.calculate(address)
        
        print(f"  Score: {result.score:.1f} | Grade: {result.grade} ({result.grade_description})")
        print(f"  Components:")
        for key, comp in result.components.items():
            bar = "█" * int(comp.raw_value * 20) + "░" * (20 - int(comp.raw_value * 20))
            print(f"    {comp.name:25} [{bar}] {comp.raw_value:.2%} × {comp.weight:.0%} = {comp.weighted_value:.3f}")
        
        if result.recommendations:
            print(f"  Recommendations:")
            for rec in result.recommendations[:2]:
                print(f"    • {rec}")
    
    print("\n\n📈 SCORE DISTRIBUTION TEST")
    print("-" * 70)
    
    # Generate larger dataset
    dataset = SampleDataGenerator.generate_dataset(100)
    scores = [calculator.calculate(addr).score for addr in dataset]
    
    # Show distribution
    grade_counts = {'A+': 0, 'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
    for score in scores:
        grade = get_grade(score)
        grade_counts[grade] += 1
    
    print("\n  Grade Distribution (100 sample addresses):")
    for grade in ['A+', 'A', 'B', 'C', 'D', 'F']:
        count = grade_counts[grade]
        bar = "█" * count
        print(f"    {grade:3} | {bar} {count}")
    
    print(f"\n  Statistics:")
    print(f"    Min: {min(scores):.1f}")
    print(f"    Max: {max(scores):.1f}")
    print(f"    Avg: {sum(scores)/len(scores):.1f}")
    
    print("\n" + "=" * 70)
    print("ALL TESTS COMPLETED")
    print("=" * 70)
