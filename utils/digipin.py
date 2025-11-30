# utils/digipin.py
# DIGIPIN Validator - Encode, Decode, and Validate DIGIPIN codes
# AAVA - Authorised Address Validation Agency
# 
# DIGIPIN is a 10-character geo-coded grid system for India
# Each code represents a ~4m x 4m area at the finest resolution
# Format: XXX-XXX-XXXX (with hyphens for display)

"""
DIGIPIN Technical Specification
================================

Geographic Bounds (India):
- Latitude:  2.5°N to 38.5°N  (36° span)
- Longitude: 63.5°E to 99.5°E (36° span)

Character Set (16 characters):
- Uses: 2, 3, 4, 5, 6, 7, 8, 9, C, F, J, K, L, M, P, T
- Avoids confusable characters (0, O, 1, I, etc.)

Grid Label Matrix (4x4):
    Col 0   Col 1   Col 2   Col 3
    ─────────────────────────────
Row 0:  F       C       9       8
Row 1:  J       3       2       7
Row 2:  K       4       5       6
Row 3:  L       M       P       T

Encoding Process:
- 10 levels of subdivision (10 characters)
- Each level divides current cell into 4x4 grid
- Cell selected based on lat/lon position
- Resolution doubles with each level (~4m at level 10)
"""

import math
from typing import Tuple, Optional, List, Dict, Any
from dataclasses import dataclass


# =============================================================================
# CONSTANTS
# =============================================================================

# Geographic bounds for India
MIN_LAT = 2.5    # Southern tip (Indira Point)
MAX_LAT = 38.5   # Northern tip (Siachen)
MIN_LON = 63.5   # Western tip (Gujarat)
MAX_LON = 99.5   # Eastern tip (Arunachal Pradesh)

# DIGIPIN character set (16 chars for 4x4 grid)
DIGIPIN_CHARS = "23456789CFJKLMPT"

# Grid label matrix - maps (row, col) to character
# Row 0 is top (higher latitude), Row 3 is bottom (lower latitude)
# Col 0 is left (lower longitude), Col 3 is right (higher longitude)
LABEL_GRID = [
    ['F', 'C', '9', '8'],  # Row 0 (top)
    ['J', '3', '2', '7'],  # Row 1
    ['K', '4', '5', '6'],  # Row 2
    ['L', 'M', 'P', 'T'],  # Row 3 (bottom)
]

# Reverse lookup: character to (row, col)
CHAR_TO_POSITION = {}
for row_idx, row in enumerate(LABEL_GRID):
    for col_idx, char in enumerate(row):
        CHAR_TO_POSITION[char] = (row_idx, col_idx)

# Number of levels in DIGIPIN (10 characters)
NUM_LEVELS = 10

# Grid size at each level (approximate meters)
# Level 1: ~1000km, Level 10: ~4m
GRID_SIZES_KM = [1000, 250, 62.5, 15.6, 3.9, 0.98, 0.24, 0.06, 0.015, 0.004]


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class Coordinates:
    """Geographic coordinates with latitude and longitude."""
    latitude: float
    longitude: float
    
    def __post_init__(self):
        """Validate coordinates are within valid ranges."""
        if not (-90 <= self.latitude <= 90):
            raise ValueError(f"Latitude {self.latitude} out of range [-90, 90]")
        if not (-180 <= self.longitude <= 180):
            raise ValueError(f"Longitude {self.longitude} out of range [-180, 180]")
    
    def to_tuple(self) -> Tuple[float, float]:
        """Return as (lat, lon) tuple."""
        return (self.latitude, self.longitude)
    
    def __str__(self) -> str:
        return f"({self.latitude:.6f}, {self.longitude:.6f})"


@dataclass
class DIGIPINResult:
    """Result of DIGIPIN encoding or decoding operation."""
    digipin: str
    formatted: str  # With hyphens: XXX-XXX-XXXX
    center_lat: float
    center_lon: float
    bounds: Dict[str, float]  # min_lat, max_lat, min_lon, max_lon
    resolution_meters: float
    valid: bool
    error: Optional[str] = None


# =============================================================================
# DIGIPIN VALIDATOR CLASS
# =============================================================================

class DIGIPINValidator:
    """
    DIGIPIN Validator and Converter
    
    Provides methods to:
    - Validate DIGIPIN format and characters
    - Encode coordinates to DIGIPIN
    - Decode DIGIPIN to coordinates
    - Calculate distance between two DIGIPINs
    - Get cell bounds for a DIGIPIN
    
    Example Usage:
        validator = DIGIPINValidator()
        
        # Encode coordinates to DIGIPIN
        result = validator.encode(28.6139, 77.2090)  # New Delhi
        print(result.formatted)  # e.g., "3PJ-K4M-5L2T"
        
        # Decode DIGIPIN to coordinates
        result = validator.decode("3PJK4M5L2T")
        print(result.center_lat, result.center_lon)
        
        # Validate DIGIPIN
        is_valid = validator.validate("3PJ-K4M-5L2T")
    """
    
    def __init__(self):
        """Initialize the DIGIPIN validator."""
        self.min_lat = MIN_LAT
        self.max_lat = MAX_LAT
        self.min_lon = MIN_LON
        self.max_lon = MAX_LON
        self.chars = DIGIPIN_CHARS
        self.label_grid = LABEL_GRID
        self.char_to_pos = CHAR_TO_POSITION
    
    # -------------------------------------------------------------------------
    # VALIDATION METHODS
    # -------------------------------------------------------------------------
    
    def validate(self, digipin: str) -> bool:
        """
        Validate if a string is a valid DIGIPIN.
        
        Args:
            digipin: DIGIPIN string (with or without hyphens)
            
        Returns:
            True if valid, False otherwise
            
        Valid formats:
            - "3PJK4M5L2T" (10 chars, no hyphens)
            - "3PJ-K4M-5L2T" (with hyphens)
        """
        # Remove hyphens and whitespace
        clean = self._clean_digipin(digipin)
        
        # Check length
        if len(clean) != NUM_LEVELS:
            return False
        
        # Check all characters are valid
        for char in clean.upper():
            if char not in self.chars:
                return False
        
        return True
    
    def validate_with_details(self, digipin: str) -> Tuple[bool, str]:
        """
        Validate DIGIPIN and return detailed error message if invalid.
        
        Args:
            digipin: DIGIPIN string to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not digipin:
            return False, "DIGIPIN cannot be empty"
        
        clean = self._clean_digipin(digipin)
        
        if len(clean) != NUM_LEVELS:
            return False, f"DIGIPIN must be {NUM_LEVELS} characters (got {len(clean)})"
        
        invalid_chars = [c for c in clean.upper() if c not in self.chars]
        if invalid_chars:
            return False, f"Invalid characters: {', '.join(invalid_chars)}. Valid: {self.chars}"
        
        return True, "Valid DIGIPIN"
    
    # -------------------------------------------------------------------------
    # ENCODING METHODS
    # -------------------------------------------------------------------------
    
    def encode(self, latitude: float, longitude: float) -> DIGIPINResult:
        """
        Encode geographic coordinates to a DIGIPIN code.
        
        The encoding process:
        1. Start with full India bounding box
        2. For each of 10 levels:
           a. Divide current box into 4x4 grid (16 cells)
           b. Find which cell contains the point
           c. Record the character for that cell
           d. Use that cell as the new bounding box
        
        Args:
            latitude: Latitude in decimal degrees (2.5 to 38.5 for India)
            longitude: Longitude in decimal degrees (63.5 to 99.5 for India)
            
        Returns:
            DIGIPINResult with code, formatted string, center coordinates, bounds
            
        Example:
            result = validator.encode(28.6139, 77.2090)
            # Returns DIGIPIN for New Delhi
        """
        # Validate coordinates are within India bounds
        if not self._is_within_bounds(latitude, longitude):
            return DIGIPINResult(
                digipin="",
                formatted="",
                center_lat=latitude,
                center_lon=longitude,
                bounds={},
                resolution_meters=0,
                valid=False,
                error=f"Coordinates ({latitude}, {longitude}) outside India bounds"
            )
        
        # Initialize bounds
        min_lat, max_lat = self.min_lat, self.max_lat
        min_lon, max_lon = self.min_lon, self.max_lon
        
        # Build DIGIPIN character by character
        digipin_chars = []
        
        for level in range(NUM_LEVELS):
            # Calculate cell dimensions
            lat_step = (max_lat - min_lat) / 4
            lon_step = (max_lon - min_lon) / 4
            
            # Determine which row and column the point falls into
            # Row 0 is top (highest lat), Row 3 is bottom (lowest lat)
            # Col 0 is left (lowest lon), Col 3 is right (highest lon)
            
            # Calculate row (from top, so invert)
            row = int((max_lat - latitude) / lat_step)
            row = min(row, 3)  # Clamp to valid range
            
            # Calculate column (from left)
            col = int((longitude - min_lon) / lon_step)
            col = min(col, 3)  # Clamp to valid range
            
            # Get character for this cell
            char = self.label_grid[row][col]
            digipin_chars.append(char)
            
            # Update bounds to the selected cell
            new_min_lat = max_lat - (row + 1) * lat_step
            new_max_lat = max_lat - row * lat_step
            new_min_lon = min_lon + col * lon_step
            new_max_lon = min_lon + (col + 1) * lon_step
            
            min_lat, max_lat = new_min_lat, new_max_lat
            min_lon, max_lon = new_min_lon, new_max_lon
        
        # Build result
        digipin = ''.join(digipin_chars)
        formatted = self._format_digipin(digipin)
        center_lat = (min_lat + max_lat) / 2
        center_lon = (min_lon + max_lon) / 2
        
        # Calculate resolution in meters (approximate)
        resolution_m = self._calculate_resolution(min_lat, max_lat, min_lon, max_lon)
        
        return DIGIPINResult(
            digipin=digipin,
            formatted=formatted,
            center_lat=center_lat,
            center_lon=center_lon,
            bounds={
                'min_lat': min_lat,
                'max_lat': max_lat,
                'min_lon': min_lon,
                'max_lon': max_lon
            },
            resolution_meters=resolution_m,
            valid=True
        )
    
    # -------------------------------------------------------------------------
    # DECODING METHODS
    # -------------------------------------------------------------------------
    
    def decode(self, digipin: str) -> DIGIPINResult:
        """
        Decode a DIGIPIN code to geographic coordinates.
        
        The decoding process:
        1. Start with full India bounding box
        2. For each character in DIGIPIN:
           a. Find the (row, col) position for that character
           b. Calculate the corresponding cell bounds
           c. Use that cell as the new bounding box
        3. Return the center of the final cell
        
        Args:
            digipin: DIGIPIN string (with or without hyphens)
            
        Returns:
            DIGIPINResult with center coordinates and cell bounds
            
        Example:
            result = validator.decode("3PJK4M5L2T")
            print(f"Center: ({result.center_lat}, {result.center_lon})")
        """
        # Validate first
        is_valid, error_msg = self.validate_with_details(digipin)
        if not is_valid:
            return DIGIPINResult(
                digipin=digipin,
                formatted="",
                center_lat=0,
                center_lon=0,
                bounds={},
                resolution_meters=0,
                valid=False,
                error=error_msg
            )
        
        # Clean and uppercase
        clean = self._clean_digipin(digipin).upper()
        
        # Initialize bounds
        min_lat, max_lat = self.min_lat, self.max_lat
        min_lon, max_lon = self.min_lon, self.max_lon
        
        # Process each character
        for char in clean:
            # Get row and column for this character
            row, col = self.char_to_pos[char]
            
            # Calculate cell dimensions
            lat_step = (max_lat - min_lat) / 4
            lon_step = (max_lon - min_lon) / 4
            
            # Update bounds to the selected cell
            new_min_lat = max_lat - (row + 1) * lat_step
            new_max_lat = max_lat - row * lat_step
            new_min_lon = min_lon + col * lon_step
            new_max_lon = min_lon + (col + 1) * lon_step
            
            min_lat, max_lat = new_min_lat, new_max_lat
            min_lon, max_lon = new_min_lon, new_max_lon
        
        # Calculate center and resolution
        center_lat = (min_lat + max_lat) / 2
        center_lon = (min_lon + max_lon) / 2
        resolution_m = self._calculate_resolution(min_lat, max_lat, min_lon, max_lon)
        
        return DIGIPINResult(
            digipin=clean,
            formatted=self._format_digipin(clean),
            center_lat=center_lat,
            center_lon=center_lon,
            bounds={
                'min_lat': min_lat,
                'max_lat': max_lat,
                'min_lon': min_lon,
                'max_lon': max_lon
            },
            resolution_meters=resolution_m,
            valid=True
        )
    
    # -------------------------------------------------------------------------
    # DISTANCE CALCULATION
    # -------------------------------------------------------------------------
    
    def distance_between(self, digipin1: str, digipin2: str) -> Optional[float]:
        """
        Calculate the distance in meters between two DIGIPINs.
        
        Uses the Haversine formula for great-circle distance.
        
        Args:
            digipin1: First DIGIPIN code
            digipin2: Second DIGIPIN code
            
        Returns:
            Distance in meters, or None if either DIGIPIN is invalid
            
        Example:
            distance = validator.distance_between("3PJK4M5L2T", "3PJK4M5L2F")
            print(f"Distance: {distance:.2f} meters")
        """
        result1 = self.decode(digipin1)
        result2 = self.decode(digipin2)
        
        if not result1.valid or not result2.valid:
            return None
        
        return self._haversine_distance(
            result1.center_lat, result1.center_lon,
            result2.center_lat, result2.center_lon
        )
    
    def distance_from_coords(
        self, 
        digipin: str, 
        latitude: float, 
        longitude: float
    ) -> Optional[float]:
        """
        Calculate distance from a DIGIPIN to a coordinate point.
        
        Args:
            digipin: DIGIPIN code
            latitude: Target latitude
            longitude: Target longitude
            
        Returns:
            Distance in meters, or None if DIGIPIN is invalid
        """
        result = self.decode(digipin)
        if not result.valid:
            return None
        
        return self._haversine_distance(
            result.center_lat, result.center_lon,
            latitude, longitude
        )
    
    # -------------------------------------------------------------------------
    # UTILITY METHODS
    # -------------------------------------------------------------------------
    
    def get_neighbors(self, digipin: str) -> List[str]:
        """
        Get the 8 neighboring DIGIPIN cells (if they exist).
        
        Args:
            digipin: Center DIGIPIN code
            
        Returns:
            List of valid neighboring DIGIPIN codes
        """
        result = self.decode(digipin)
        if not result.valid:
            return []
        
        # Get cell dimensions
        lat_step = result.bounds['max_lat'] - result.bounds['min_lat']
        lon_step = result.bounds['max_lon'] - result.bounds['min_lon']
        center_lat = result.center_lat
        center_lon = result.center_lon
        
        # Calculate 8 neighbor centers
        offsets = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
        
        neighbors = []
        for lat_off, lon_off in offsets:
            new_lat = center_lat + lat_off * lat_step
            new_lon = center_lon + lon_off * lon_step
            
            if self._is_within_bounds(new_lat, new_lon):
                neighbor_result = self.encode(new_lat, new_lon)
                if neighbor_result.valid:
                    neighbors.append(neighbor_result.digipin)
        
        return neighbors
    
    def get_grid_info(self) -> Dict[str, Any]:
        """
        Get information about the DIGIPIN grid system.
        
        Returns:
            Dictionary with grid specifications
        """
        return {
            'bounds': {
                'min_lat': self.min_lat,
                'max_lat': self.max_lat,
                'min_lon': self.min_lon,
                'max_lon': self.max_lon
            },
            'characters': self.chars,
            'num_levels': NUM_LEVELS,
            'grid_size_per_level': GRID_SIZES_KM,
            'label_grid': self.label_grid,
            'total_cells': 16 ** NUM_LEVELS  # ~1 trillion cells
        }
    
    # -------------------------------------------------------------------------
    # PRIVATE HELPER METHODS
    # -------------------------------------------------------------------------
    
    def _clean_digipin(self, digipin: str) -> str:
        """Remove hyphens, whitespace, and normalize to uppercase."""
        return digipin.replace('-', '').replace(' ', '').strip().upper()
    
    def _format_digipin(self, digipin: str) -> str:
        """Format DIGIPIN with hyphens: XXX-XXX-XXXX."""
        clean = self._clean_digipin(digipin)
        if len(clean) != 10:
            return clean
        return f"{clean[0:3]}-{clean[3:6]}-{clean[6:10]}"
    
    def _is_within_bounds(self, latitude: float, longitude: float) -> bool:
        """Check if coordinates are within India bounds."""
        return (
            self.min_lat <= latitude <= self.max_lat and
            self.min_lon <= longitude <= self.max_lon
        )
    
    def _calculate_resolution(
        self, 
        min_lat: float, 
        max_lat: float, 
        min_lon: float, 
        max_lon: float
    ) -> float:
        """Calculate approximate cell resolution in meters."""
        # Use center latitude for more accurate calculation
        center_lat = (min_lat + max_lat) / 2
        
        # Approximate meters per degree at this latitude
        meters_per_deg_lat = 111320  # Approximately constant
        meters_per_deg_lon = 111320 * math.cos(math.radians(center_lat))
        
        # Calculate cell dimensions in meters
        lat_meters = (max_lat - min_lat) * meters_per_deg_lat
        lon_meters = (max_lon - min_lon) * meters_per_deg_lon
        
        # Return average
        return (lat_meters + lon_meters) / 2
    
    def _haversine_distance(
        self, 
        lat1: float, 
        lon1: float, 
        lat2: float, 
        lon2: float
    ) -> float:
        """
        Calculate great-circle distance using Haversine formula.
        
        Args:
            lat1, lon1: First point coordinates
            lat2, lon2: Second point coordinates
            
        Returns:
            Distance in meters
        """
        R = 6371000  # Earth radius in meters
        
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        # Haversine formula
        a = (
            math.sin(delta_lat / 2) ** 2 +
            math.cos(lat1_rad) * math.cos(lat2_rad) *
            math.sin(delta_lon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

# Global validator instance for convenience
_validator = DIGIPINValidator()

def encode_digipin(latitude: float, longitude: float) -> str:
    """
    Encode coordinates to DIGIPIN (convenience function).
    
    Args:
        latitude: Latitude in decimal degrees
        longitude: Longitude in decimal degrees
        
    Returns:
        Formatted DIGIPIN string or empty string if invalid
    """
    result = _validator.encode(latitude, longitude)
    return result.formatted if result.valid else ""

def decode_digipin(digipin: str) -> Tuple[float, float]:
    """
    Decode DIGIPIN to coordinates (convenience function).
    
    Args:
        digipin: DIGIPIN string
        
    Returns:
        Tuple of (latitude, longitude) or (0, 0) if invalid
    """
    result = _validator.decode(digipin)
    return (result.center_lat, result.center_lon) if result.valid else (0, 0)

def validate_digipin(digipin: str) -> bool:
    """
    Validate DIGIPIN (convenience function).
    
    Args:
        digipin: DIGIPIN string to validate
        
    Returns:
        True if valid, False otherwise
    """
    return _validator.validate(digipin)

def digipin_distance(digipin1: str, digipin2: str) -> float:
    """
    Calculate distance between two DIGIPINs (convenience function).
    
    Args:
        digipin1: First DIGIPIN
        digipin2: Second DIGIPIN
        
    Returns:
        Distance in meters or -1 if invalid
    """
    result = _validator.distance_between(digipin1, digipin2)
    return result if result is not None else -1


# =============================================================================
# TEST CODE
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("DIGIPIN VALIDATOR - TEST SUITE")
    print("=" * 70)
    
    validator = DIGIPINValidator()
    
    # Test cases with known locations
    test_locations = [
        ("New Delhi (India Gate)", 28.6129, 77.2295),
        ("Mumbai (Gateway of India)", 18.9220, 72.8347),
        ("Bangalore (Vidhana Soudha)", 12.9716, 77.5946),
        ("Chennai (Marina Beach)", 13.0500, 80.2824),
        ("Kolkata (Victoria Memorial)", 22.5448, 88.3426),
        ("Hyderabad (Charminar)", 17.3616, 78.4747),
        ("Pune (Shaniwar Wada)", 18.5195, 73.8553),
        ("Ahmedabad (Sabarmati Ashram)", 23.0607, 72.5809),
    ]
    
    print("\n📍 ENCODING TEST (Coordinates → DIGIPIN)")
    print("-" * 70)
    
    encoded_digipins = []
    for name, lat, lon in test_locations:
        result = validator.encode(lat, lon)
        encoded_digipins.append(result.digipin)
        print(f"\n{name}")
        print(f"  Coordinates: ({lat:.4f}, {lon:.4f})")
        print(f"  DIGIPIN: {result.formatted}")
        print(f"  Resolution: {result.resolution_meters:.2f} meters")
        print(f"  Cell bounds: {result.bounds['min_lat']:.6f} to {result.bounds['max_lat']:.6f} lat")
    
    print("\n\n🔍 DECODING TEST (DIGIPIN → Coordinates)")
    print("-" * 70)
    
    for i, (name, orig_lat, orig_lon) in enumerate(test_locations):
        digipin = encoded_digipins[i]
        result = validator.decode(digipin)
        error_lat = abs(result.center_lat - orig_lat) * 111320
        error_lon = abs(result.center_lon - orig_lon) * 111320 * math.cos(math.radians(orig_lat))
        
        print(f"\n{name} - {result.formatted}")
        print(f"  Decoded: ({result.center_lat:.6f}, {result.center_lon:.6f})")
        print(f"  Original: ({orig_lat:.6f}, {orig_lon:.6f})")
        print(f"  Error: {error_lat:.2f}m lat, {error_lon:.2f}m lon")
    
    print("\n\n✅ VALIDATION TEST")
    print("-" * 70)
    
    test_digipins = [
        ("3PJK4M5L2T", True),      # Valid
        ("3PJ-K4M-5L2T", True),    # Valid with hyphens
        ("ABCDEFGHIJ", False),     # Invalid characters (A, B, D, E, G, H, I)
        ("3PJK4M5L2", False),      # Too short (9 chars)
        ("3PJK4M5L2TT", False),    # Too long (11 chars)
        ("", False),               # Empty
    ]
    
    for digipin, expected in test_digipins:
        is_valid, message = validator.validate_with_details(digipin)
        status = "✓" if is_valid == expected else "✗"
        print(f"  {status} '{digipin}' → {message}")
    
    print("\n\n📏 DISTANCE TEST")
    print("-" * 70)
    
    # Calculate distance between Delhi and Mumbai
    delhi_digipin = validator.encode(28.6129, 77.2295).digipin
    mumbai_digipin = validator.encode(18.9220, 72.8347).digipin
    distance = validator.distance_between(delhi_digipin, mumbai_digipin)
    
    print(f"\n  Delhi DIGIPIN: {validator._format_digipin(delhi_digipin)}")
    print(f"  Mumbai DIGIPIN: {validator._format_digipin(mumbai_digipin)}")
    print(f"  Distance: {distance/1000:.2f} km")
    
    # Distance between adjacent cells
    result1 = validator.encode(28.6129, 77.2295)
    neighbors = validator.get_neighbors(result1.digipin)
    if neighbors:
        neighbor_dist = validator.distance_between(result1.digipin, neighbors[0])
        print(f"\n  Distance to adjacent cell: {neighbor_dist:.2f} meters")
    
    print("\n\n📊 GRID INFORMATION")
    print("-" * 70)
    
    grid_info = validator.get_grid_info()
    print(f"\n  Bounds: Lat {grid_info['bounds']['min_lat']}° to {grid_info['bounds']['max_lat']}°")
    print(f"          Lon {grid_info['bounds']['min_lon']}° to {grid_info['bounds']['max_lon']}°")
    print(f"  Characters: {grid_info['characters']}")
    print(f"  Levels: {grid_info['num_levels']}")
    print(f"  Total possible cells: {grid_info['total_cells']:,}")
    
    print("\n" + "=" * 70)
    print("ALL TESTS COMPLETED")
    print("=" * 70)
