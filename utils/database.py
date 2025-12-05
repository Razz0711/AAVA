# utils/database.py
# SQLite Database Management for AAVA System
# AAVA - Authorised Address Validation Agency
# 
# Provides all database operations: schema creation, CRUD, and queries

"""
Database Schema Overview
========================

Tables:
-------
1. addresses
   - Core address records with DIGIPIN and coordinates
   
2. validations
   - Validation request records and status tracking
   
3. agents
   - Field agent profiles and performance metrics
   
4. deliveries
   - Delivery attempt records for confidence scoring
   
5. verifications
   - Physical verification records by agents
   
6. consents
   - User consent artifacts and management
   
7. audit_logs
   - Immutable audit trail for all operations
"""

import sqlite3
import json
import uuid
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from contextlib import contextmanager
from dataclasses import dataclass, asdict
from enum import Enum
import threading


# =============================================================================
# ENUMS
# =============================================================================

class ValidationStatus(Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class ValidationType(Enum):
    PHYSICAL = "PHYSICAL"
    DIGITAL = "DIGITAL"
    HYBRID = "HYBRID"

class Priority(Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    URGENT = "URGENT"

class DeliveryStatus(Enum):
    DELIVERED = "DELIVERED"
    DELIVERED_WITH_DIFFICULTY = "DELIVERED_WITH_DIFFICULTY"
    FAILED = "FAILED"
    PENDING = "PENDING"


# =============================================================================
# DATABASE MANAGER
# =============================================================================

class DatabaseManager:
    """
    SQLite Database Manager for AAVA System.
    
    Thread-safe database operations with connection pooling.
    
    Usage:
        db = DatabaseManager("aava.db")
        db.initialize()
        
        # Insert validation
        validation_id = db.create_validation({
            'digital_address': 'user@provider.in',
            'digipin': '3PJK4M5L2T',
            ...
        })
        
        # Query
        validation = db.get_validation(validation_id)
    """
    
    # Thread-local storage for connections
    _local = threading.local()
    
    def __init__(self, db_path: str = "data/aava.db"):
        """
        Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._ensure_directory()
    
    def _ensure_directory(self):
        """Create directory if it doesn't exist."""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
    
    @contextmanager
    def get_connection(self):
        """Get a database connection (thread-safe)."""
        if not hasattr(self._local, 'connection') or self._local.connection is None:
            self._local.connection = sqlite3.connect(self.db_path)
            self._local.connection.row_factory = sqlite3.Row
            # Enable foreign keys
            self._local.connection.execute("PRAGMA foreign_keys = ON")
        
        try:
            yield self._local.connection
        except Exception as e:
            self._local.connection.rollback()
            raise e
    
    def close(self):
        """Close the database connection."""
        if hasattr(self._local, 'connection') and self._local.connection:
            self._local.connection.close()
            self._local.connection = None
    
    # -------------------------------------------------------------------------
    # SCHEMA CREATION
    # -------------------------------------------------------------------------
    
    def initialize(self):
        """Create all database tables if they don't exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Addresses table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS addresses (
                    id TEXT PRIMARY KEY,
                    digital_address TEXT UNIQUE,
                    digipin TEXT,
                    descriptive_address TEXT,
                    latitude REAL,
                    longitude REAL,
                    city TEXT,
                    state TEXT,
                    pincode TEXT,
                    confidence_score REAL DEFAULT 0,
                    confidence_grade TEXT DEFAULT 'F',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Validations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS validations (
                    id TEXT PRIMARY KEY,
                    address_id TEXT,
                    digital_address TEXT,
                    digipin TEXT,
                    descriptive_address TEXT,
                    validation_type TEXT DEFAULT 'DIGITAL',
                    status TEXT DEFAULT 'PENDING',
                    priority TEXT DEFAULT 'NORMAL',
                    requester_id TEXT,
                    assigned_agent_id TEXT,
                    consent_id TEXT,
                    confidence_score_before REAL,
                    confidence_score_after REAL,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    FOREIGN KEY (address_id) REFERENCES addresses(id),
                    FOREIGN KEY (assigned_agent_id) REFERENCES agents(id)
                )
            """)
            
            # Agents table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agents (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE,
                    phone TEXT UNIQUE,
                    password TEXT,
                    photo_url TEXT,
                    certification_date DATE,
                    certification_expiry DATE,
                    active INTEGER DEFAULT 1,
                    performance_score REAL DEFAULT 0.8,
                    total_verifications INTEGER DEFAULT 0,
                    successful_verifications INTEGER DEFAULT 0,
                    current_location_lat REAL,
                    current_location_lon REAL,
                    last_active TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Add password column if not exists (for existing databases)
            try:
                cursor.execute("ALTER TABLE agents ADD COLUMN password TEXT")
            except:
                pass  # Column already exists
            
            # Deliveries table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS deliveries (
                    id TEXT PRIMARY KEY,
                    address_id TEXT,
                    status TEXT DEFAULT 'PENDING',
                    actual_latitude REAL,
                    actual_longitude REAL,
                    distance_from_stated REAL,
                    ease_rating INTEGER,
                    delivery_partner TEXT,
                    notes TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (address_id) REFERENCES addresses(id)
                )
            """)
            
            # Verifications table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS verifications (
                    id TEXT PRIMARY KEY,
                    validation_id TEXT,
                    agent_id TEXT,
                    verified INTEGER DEFAULT 0,
                    quality_score REAL,
                    evidence_type TEXT,
                    photos TEXT,
                    gps_latitude REAL,
                    gps_longitude REAL,
                    gps_accuracy REAL,
                    signature_data TEXT,
                    notes TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (validation_id) REFERENCES validations(id),
                    FOREIGN KEY (agent_id) REFERENCES agents(id)
                )
            """)
            
            # Users table (for AIA - Address Issuance Authority)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    phone TEXT UNIQUE,
                    password TEXT NOT NULL,
                    aadhaar_hash TEXT,
                    verified INTEGER DEFAULT 0,
                    active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                )
            """)
            
            # User addresses - linking users to their addresses
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_addresses (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    address_id TEXT NOT NULL,
                    label TEXT DEFAULT 'Home',
                    is_primary INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (address_id) REFERENCES addresses(id),
                    UNIQUE(user_id, address_id)
                )
            """)
            
            # Consents table (enhanced for AIA authorization framework)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS consents (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    address_id TEXT NOT NULL,
                    grantee_name TEXT NOT NULL,
                    grantee_type TEXT DEFAULT 'AIU',
                    purpose TEXT,
                    scope TEXT DEFAULT 'view',
                    access_token TEXT UNIQUE,
                    consent_artifact TEXT,
                    issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    access_count INTEGER DEFAULT 0,
                    last_accessed TIMESTAMP,
                    revoked INTEGER DEFAULT 0,
                    revoked_at TIMESTAMP,
                    revocation_reason TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (address_id) REFERENCES addresses(id)
                )
            """)
            
            # Audit logs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id TEXT PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    actor TEXT,
                    action TEXT,
                    resource_type TEXT,
                    resource_id TEXT,
                    details TEXT,
                    ip_address TEXT,
                    prev_hash TEXT,
                    entry_hash TEXT
                )
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_addresses_digipin ON addresses(digipin)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_validations_status ON validations(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_validations_agent ON validations(assigned_agent_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_deliveries_address ON deliveries(address_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_verifications_validation ON verifications(validation_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_addresses_user ON user_addresses(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_consents_user ON consents(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_consents_token ON consents(access_token)")
            
            conn.commit()
            print(f"✓ Database initialized at {self.db_path}")
    
    # -------------------------------------------------------------------------
    # UTILITY METHODS
    # -------------------------------------------------------------------------
    
    def _generate_id(self, prefix: str = "") -> str:
        """Generate a unique ID with optional prefix."""
        uid = str(uuid.uuid4())[:8].upper()
        return f"{prefix}-{uid}" if prefix else uid
    
    def _row_to_dict(self, row: sqlite3.Row) -> Dict:
        """Convert sqlite3.Row to dictionary."""
        if row is None:
            return None
        return dict(row)
    
    # -------------------------------------------------------------------------
    # ADDRESS OPERATIONS
    # -------------------------------------------------------------------------
    
    def create_address(self, data: Dict) -> str:
        """Create a new address record."""
        address_id = data.get('id') or self._generate_id("ADDR")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO addresses (
                    id, digital_address, digipin, descriptive_address,
                    latitude, longitude, city, state, pincode,
                    confidence_score, confidence_grade
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                address_id,
                data.get('digital_address'),
                data.get('digipin'),
                data.get('descriptive_address'),
                data.get('latitude'),
                data.get('longitude'),
                data.get('city'),
                data.get('state'),
                data.get('pincode'),
                data.get('confidence_score', 0),
                data.get('confidence_grade', 'F')
            ))
            conn.commit()
        
        return address_id
    
    def get_address(self, address_id: str) -> Optional[Dict]:
        """Get address by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM addresses WHERE id = ?", (address_id,))
            return self._row_to_dict(cursor.fetchone())
    
    def get_address_by_digipin(self, digipin: str) -> Optional[Dict]:
        """Get address by DIGIPIN."""
        clean_digipin = digipin.replace('-', '').upper()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM addresses WHERE REPLACE(digipin, '-', '') = ?", 
                (clean_digipin,)
            )
            return self._row_to_dict(cursor.fetchone())
    
    def get_address_by_digital_address(self, digital_address: str) -> Optional[Dict]:
        """Get address by digital address."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM addresses WHERE digital_address = ?", 
                (digital_address,)
            )
            return self._row_to_dict(cursor.fetchone())
    
    def update_address(self, address_id: str, data: Dict) -> bool:
        """Update an address record."""
        data['updated_at'] = datetime.now().isoformat()
        
        set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
        values = list(data.values()) + [address_id]
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE addresses SET {set_clause} WHERE id = ?",
                values
            )
            conn.commit()
            return cursor.rowcount > 0
    
    def get_all_addresses(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Get all addresses with pagination."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM addresses ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (limit, offset)
            )
            return [self._row_to_dict(row) for row in cursor.fetchall()]
    
    def search_addresses(self, query: str) -> List[Dict]:
        """Search addresses by digital address, digipin, or descriptive address."""
        search_term = f"%{query}%"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM addresses 
                WHERE digital_address LIKE ?
                   OR digipin LIKE ?
                   OR descriptive_address LIKE ?
                ORDER BY confidence_score DESC
                LIMIT 50
            """, (search_term, search_term, search_term))
            return [self._row_to_dict(row) for row in cursor.fetchall()]
    
    # -------------------------------------------------------------------------
    # VALIDATION OPERATIONS
    # -------------------------------------------------------------------------
    
    def create_validation(self, data: Dict) -> str:
        """Create a new validation request."""
        validation_id = data.get('id') or self._generate_id("VAL")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO validations (
                    id, address_id, digital_address, digipin, descriptive_address,
                    validation_type, status, priority, requester_id,
                    assigned_agent_id, consent_id, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                validation_id,
                data.get('address_id'),
                data.get('digital_address'),
                data.get('digipin'),
                data.get('descriptive_address'),
                data.get('validation_type', 'DIGITAL'),
                data.get('status', 'PENDING'),
                data.get('priority', 'NORMAL'),
                data.get('requester_id'),
                data.get('assigned_agent_id'),
                data.get('consent_id'),
                data.get('notes')
            ))
            conn.commit()
        
        return validation_id
    
    def get_validation(self, validation_id: str) -> Optional[Dict]:
        """Get validation by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM validations WHERE id = ?", (validation_id,))
            return self._row_to_dict(cursor.fetchone())
    
    def update_validation(self, validation_id: str, data: Dict) -> bool:
        """Update a validation record."""
        data['updated_at'] = datetime.now().isoformat()
        
        set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
        values = list(data.values()) + [validation_id]
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE validations SET {set_clause} WHERE id = ?",
                values
            )
            conn.commit()
            return cursor.rowcount > 0
    
    def get_validations_by_status(self, status: str) -> List[Dict]:
        """Get all validations with a specific status."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM validations WHERE status = ? ORDER BY created_at DESC",
                (status,)
            )
            return [self._row_to_dict(row) for row in cursor.fetchall()]
    
    def get_pending_validation_for_address(self, address_id: str) -> Optional[Dict]:
        """Get pending validation for an address if exists."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT * FROM validations 
                   WHERE address_id = ? AND status IN ('PENDING', 'IN_PROGRESS')
                   ORDER BY created_at DESC LIMIT 1""",
                (address_id,)
            )
            return self._row_to_dict(cursor.fetchone())
    
    def get_validations_by_agent(self, agent_id: str) -> List[Dict]:
        """Get all validations assigned to an agent."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT * FROM validations 
                   WHERE assigned_agent_id = ? 
                   ORDER BY 
                       CASE priority 
                           WHEN 'URGENT' THEN 1 
                           WHEN 'HIGH' THEN 2 
                           WHEN 'NORMAL' THEN 3 
                           ELSE 4 
                       END,
                       created_at DESC""",
                (agent_id,)
            )
            return [self._row_to_dict(row) for row in cursor.fetchall()]
    
    def get_all_validations(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Get all validations with pagination."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM validations ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (limit, offset)
            )
            return [self._row_to_dict(row) for row in cursor.fetchall()]
    
    def get_validation_stats(self) -> Dict:
        """Get validation statistics."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Count by status
            cursor.execute("""
                SELECT status, COUNT(*) as count 
                FROM validations 
                GROUP BY status
            """)
            status_counts = {row['status']: row['count'] for row in cursor.fetchall()}
            
            # Count by type
            cursor.execute("""
                SELECT validation_type, COUNT(*) as count 
                FROM validations 
                GROUP BY validation_type
            """)
            type_counts = {row['validation_type']: row['count'] for row in cursor.fetchall()}
            
            # Total
            cursor.execute("SELECT COUNT(*) as total FROM validations")
            total = cursor.fetchone()['total']
            
            # Today's validations
            cursor.execute("""
                SELECT COUNT(*) as today 
                FROM validations 
                WHERE DATE(created_at) = DATE('now')
            """)
            today = cursor.fetchone()['today']
            
            return {
                'total': total,
                'today': today,
                'by_status': status_counts,
                'by_type': type_counts
            }
    
    # -------------------------------------------------------------------------
    # AGENT OPERATIONS
    # -------------------------------------------------------------------------
    
    def create_agent(self, data: Dict) -> str:
        """Create a new agent."""
        agent_id = data.get('id') or self._generate_id("AGT")
        email = data.get('email')
        phone = data.get('phone')
        
        # Check for duplicate email or phone
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check duplicate email
            if email:
                cursor.execute("SELECT id FROM agents WHERE email = ?", (email,))
                if cursor.fetchone():
                    raise ValueError(f"Email '{email}' already exists")
            
            # Check duplicate phone
            if phone:
                cursor.execute("SELECT id FROM agents WHERE phone = ?", (phone,))
                if cursor.fetchone():
                    raise ValueError(f"Phone '{phone}' already exists")
            
            # Check duplicate agent_id
            cursor.execute("SELECT id FROM agents WHERE id = ?", (agent_id,))
            if cursor.fetchone():
                raise ValueError(f"Agent ID '{agent_id}' already exists")
            
            cursor.execute("""
                INSERT INTO agents (
                    id, name, email, phone, password, photo_url,
                    certification_date, certification_expiry, active,
                    performance_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                agent_id,
                data.get('name'),
                email,
                phone,
                data.get('password'),
                data.get('photo_url'),
                data.get('certification_date'),
                data.get('certification_expiry'),
                data.get('active', 1),
                data.get('performance_score', 0.8)
            ))
            conn.commit()
        
        return agent_id
    
    def get_agent(self, agent_id: str) -> Optional[Dict]:
        """Get agent by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM agents WHERE id = ?", (agent_id,))
            return self._row_to_dict(cursor.fetchone())
    
    def get_agent_by_email(self, email: str) -> Optional[Dict]:
        """Get agent by email."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM agents WHERE email = ?", (email,))
            return self._row_to_dict(cursor.fetchone())
    
    def delete_agent(self, agent_id: str) -> bool:
        """Delete an agent."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                # Update validations to remove agent reference
                try:
                    cursor.execute("UPDATE validations SET assigned_agent_id = NULL WHERE assigned_agent_id = ?", (agent_id,))
                except:
                    pass
                # Update verifications to remove agent reference
                try:
                    cursor.execute("UPDATE verifications SET agent_id = NULL WHERE agent_id = ?", (agent_id,))
                except:
                    pass
                # Delete the agent
                cursor.execute("DELETE FROM agents WHERE id = ?", (agent_id,))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error deleting agent: {e}")
            return False
    
    def update_agent(self, agent_id: str, data: Dict) -> bool:
        """Update an agent record."""
        set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
        values = list(data.values()) + [agent_id]
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE agents SET {set_clause} WHERE id = ?",
                values
            )
            conn.commit()
            return cursor.rowcount > 0
    
    def get_all_agents(self, active_only: bool = False) -> List[Dict]:
        """Get all agents."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if active_only:
                cursor.execute(
                    "SELECT * FROM agents WHERE active = 1 ORDER BY performance_score DESC"
                )
            else:
                cursor.execute("SELECT * FROM agents ORDER BY name")
            return [self._row_to_dict(row) for row in cursor.fetchall()]
    
    def get_agent_stats(self, agent_id: str) -> Dict:
        """Get agent performance statistics."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get agent
            agent = self.get_agent(agent_id)
            if not agent:
                return {}
            
            # Count verifications
            cursor.execute("""
                SELECT COUNT(*) as total,
                       SUM(CASE WHEN verified = 1 THEN 1 ELSE 0 END) as successful
                FROM verifications
                WHERE agent_id = ?
            """, (agent_id,))
            ver_stats = cursor.fetchone()
            
            # Count validations
            cursor.execute("""
                SELECT COUNT(*) as assigned,
                       SUM(CASE WHEN status = 'COMPLETED' THEN 1 ELSE 0 END) as completed
                FROM validations
                WHERE assigned_agent_id = ?
            """, (agent_id,))
            val_stats = cursor.fetchone()
            
            return {
                'agent': agent,
                'total_verifications': ver_stats['total'] or 0,
                'successful_verifications': ver_stats['successful'] or 0,
                'assigned_validations': val_stats['assigned'] or 0,
                'completed_validations': val_stats['completed'] or 0,
                'success_rate': (ver_stats['successful'] or 0) / max(ver_stats['total'] or 1, 1)
            }
    
    # -------------------------------------------------------------------------
    # USER OPERATIONS (AIA - Address Issuance Authority)
    # -------------------------------------------------------------------------
    
    def create_user(self, data: Dict) -> str:
        """Create a new user account."""
        import hashlib
        user_id = data.get('id') or self._generate_id("USR")
        email = data.get('email')
        phone = data.get('phone')
        
        # Hash password
        password = data.get('password', '')
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check duplicate email
            if email:
                cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
                if cursor.fetchone():
                    raise ValueError(f"Email '{email}' already registered")
            
            # Check duplicate phone
            if phone:
                cursor.execute("SELECT id FROM users WHERE phone = ?", (phone,))
                if cursor.fetchone():
                    raise ValueError(f"Phone '{phone}' already registered")
            
            cursor.execute("""
                INSERT INTO users (
                    id, name, email, phone, password, aadhaar_hash, verified, active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                data.get('name'),
                email,
                phone,
                password_hash,
                data.get('aadhaar_hash'),
                data.get('verified', 0),
                data.get('active', 1)
            ))
            conn.commit()
        
        return user_id
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            return self._row_to_dict(cursor.fetchone())
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            return self._row_to_dict(cursor.fetchone())
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
        """Authenticate user by email and password."""
        import hashlib
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE email = ? AND password = ? AND active = 1",
                (email, password_hash)
            )
            user = self._row_to_dict(cursor.fetchone())
            
            if user:
                # Update last login
                cursor.execute(
                    "UPDATE users SET last_login = ? WHERE id = ?",
                    (datetime.now().isoformat(), user['id'])
                )
                conn.commit()
            
            return user
    
    def update_user(self, user_id: str, data: Dict) -> bool:
        """Update a user record."""
        # If password is being updated, hash it
        if 'password' in data:
            import hashlib
            data['password'] = hashlib.sha256(data['password'].encode()).hexdigest()
        
        set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
        values = list(data.values()) + [user_id]
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE users SET {set_clause} WHERE id = ?",
                values
            )
            conn.commit()
            return cursor.rowcount > 0
    
    # -------------------------------------------------------------------------
    # USER ADDRESS OPERATIONS
    # -------------------------------------------------------------------------
    
    def link_address_to_user(self, user_id: str, address_id: str, label: str = "Home", is_primary: bool = False) -> str:
        """Link an address to a user."""
        link_id = self._generate_id("UAL")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # If primary, unset other primaries for this user
            if is_primary:
                cursor.execute(
                    "UPDATE user_addresses SET is_primary = 0 WHERE user_id = ?",
                    (user_id,)
                )
            
            cursor.execute("""
                INSERT INTO user_addresses (id, user_id, address_id, label, is_primary)
                VALUES (?, ?, ?, ?, ?)
            """, (link_id, user_id, address_id, label, 1 if is_primary else 0))
            conn.commit()
        
        return link_id
    
    def get_user_addresses(self, user_id: str) -> List[Dict]:
        """Get all addresses linked to a user."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT ua.*, a.digital_address, a.digipin, a.descriptive_address,
                       a.latitude, a.longitude, a.city, a.state, a.pincode,
                       a.confidence_score, a.confidence_grade
                FROM user_addresses ua
                JOIN addresses a ON ua.address_id = a.id
                WHERE ua.user_id = ?
                ORDER BY ua.is_primary DESC, ua.created_at DESC
            """, (user_id,))
            return [self._row_to_dict(row) for row in cursor.fetchall()]
    
    def unlink_address_from_user(self, user_id: str, address_id: str) -> bool:
        """Remove address link from user."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM user_addresses WHERE user_id = ? AND address_id = ?",
                (user_id, address_id)
            )
            conn.commit()
            return cursor.rowcount > 0
    
    def update_user_address(self, user_id: str, address_id: str, data: Dict) -> bool:
        """Update user address link (label, primary status)."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # If setting as primary, unset others first
            if data.get('is_primary'):
                cursor.execute(
                    "UPDATE user_addresses SET is_primary = 0 WHERE user_id = ?",
                    (user_id,)
                )
            
            set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
            values = list(data.values()) + [user_id, address_id]
            
            cursor.execute(
                f"UPDATE user_addresses SET {set_clause} WHERE user_id = ? AND address_id = ?",
                values
            )
            conn.commit()
            return cursor.rowcount > 0
    
    # -------------------------------------------------------------------------
    # CONSENT OPERATIONS (Authorization Framework)
    # -------------------------------------------------------------------------
    
    def create_consent(self, data: Dict) -> str:
        """Create a new consent grant for address sharing."""
        import secrets
        consent_id = data.get('id') or self._generate_id("CON")
        access_token = secrets.token_urlsafe(32)
        
        # Default expiry: 30 days
        expires_at = data.get('expires_at')
        if not expires_at:
            expires_at = (datetime.now() + timedelta(days=30)).isoformat()
        
        consent_artifact = json.dumps({
            'consent_id': consent_id,
            'user_id': data.get('user_id'),
            'address_id': data.get('address_id'),
            'grantee_name': data.get('grantee_name'),
            'grantee_type': data.get('grantee_type', 'AIU'),
            'purpose': data.get('purpose'),
            'scope': data.get('scope', 'view'),
            'issued_at': datetime.now().isoformat(),
            'expires_at': expires_at
        })
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO consents (
                    id, user_id, address_id, grantee_name, grantee_type,
                    purpose, scope, access_token, consent_artifact, expires_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                consent_id,
                data.get('user_id'),
                data.get('address_id'),
                data.get('grantee_name'),
                data.get('grantee_type', 'AIU'),
                data.get('purpose'),
                data.get('scope', 'view'),
                access_token,
                consent_artifact,
                expires_at
            ))
            conn.commit()
        
        return consent_id, access_token
    
    def get_consent(self, consent_id: str) -> Optional[Dict]:
        """Get consent by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM consents WHERE id = ?", (consent_id,))
            return self._row_to_dict(cursor.fetchone())
    
    def get_consent_by_token(self, access_token: str) -> Optional[Dict]:
        """Get consent by access token (for AIU access)."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.*, a.digital_address, a.digipin, a.descriptive_address,
                       a.latitude, a.longitude, a.city, a.state, a.pincode,
                       a.confidence_score, a.confidence_grade
                FROM consents c
                JOIN addresses a ON c.address_id = a.id
                WHERE c.access_token = ? AND c.revoked = 0
                  AND (c.expires_at IS NULL OR c.expires_at > datetime('now'))
            """, (access_token,))
            consent = self._row_to_dict(cursor.fetchone())
            
            if consent:
                # Increment access count and update last accessed
                cursor.execute("""
                    UPDATE consents 
                    SET access_count = access_count + 1, last_accessed = ?
                    WHERE id = ?
                """, (datetime.now().isoformat(), consent['id']))
                conn.commit()
            
            return consent
    
    def get_user_consents(self, user_id: str, include_revoked: bool = False) -> List[Dict]:
        """Get all consents granted by a user."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if include_revoked:
                cursor.execute("""
                    SELECT c.*, a.digital_address, a.digipin
                    FROM consents c
                    JOIN addresses a ON c.address_id = a.id
                    WHERE c.user_id = ?
                    ORDER BY c.issued_at DESC
                """, (user_id,))
            else:
                cursor.execute("""
                    SELECT c.*, a.digital_address, a.digipin
                    FROM consents c
                    JOIN addresses a ON c.address_id = a.id
                    WHERE c.user_id = ? AND c.revoked = 0
                    ORDER BY c.issued_at DESC
                """, (user_id,))
            return [self._row_to_dict(row) for row in cursor.fetchall()]
    
    def revoke_consent(self, consent_id: str, reason: str = None) -> bool:
        """Revoke a consent."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE consents 
                SET revoked = 1, revoked_at = ?, revocation_reason = ?
                WHERE id = ?
            """, (datetime.now().isoformat(), reason, consent_id))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_address_consents(self, address_id: str) -> List[Dict]:
        """Get all active consents for an address."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM consents 
                WHERE address_id = ? AND revoked = 0
                  AND (expires_at IS NULL OR expires_at > datetime('now'))
                ORDER BY issued_at DESC
            """, (address_id,))
            return [self._row_to_dict(row) for row in cursor.fetchall()]

    # -------------------------------------------------------------------------
    # DELIVERY OPERATIONS
    # -------------------------------------------------------------------------
    
    def create_delivery(self, data: Dict) -> str:
        """Create a new delivery record."""
        delivery_id = data.get('id') or self._generate_id("DEL")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO deliveries (
                    id, address_id, status, actual_latitude, actual_longitude,
                    distance_from_stated, ease_rating, delivery_partner, notes, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                delivery_id,
                data.get('address_id'),
                data.get('status', 'PENDING'),
                data.get('actual_latitude'),
                data.get('actual_longitude'),
                data.get('distance_from_stated'),
                data.get('ease_rating'),
                data.get('delivery_partner'),
                data.get('notes'),
                data.get('timestamp', datetime.now().isoformat())
            ))
            conn.commit()
        
        return delivery_id
    
    def get_deliveries_by_address(self, address_id: str) -> List[Dict]:
        """Get all deliveries for an address."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM deliveries WHERE address_id = ? ORDER BY timestamp DESC",
                (address_id,)
            )
            return [self._row_to_dict(row) for row in cursor.fetchall()]
    
    def get_delivery_stats(self, address_id: str) -> Dict:
        """Get delivery statistics for an address."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'DELIVERED' THEN 1 ELSE 0 END) as delivered,
                    SUM(CASE WHEN status = 'DELIVERED_WITH_DIFFICULTY' THEN 1 ELSE 0 END) as partial,
                    SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END) as failed,
                    AVG(distance_from_stated) as avg_distance,
                    AVG(ease_rating) as avg_ease
                FROM deliveries
                WHERE address_id = ?
            """, (address_id,))
            row = cursor.fetchone()
            
            return {
                'total': row['total'] or 0,
                'delivered': row['delivered'] or 0,
                'partial': row['partial'] or 0,
                'failed': row['failed'] or 0,
                'avg_distance': row['avg_distance'] or 0,
                'avg_ease_rating': row['avg_ease'] or 0,
                'success_rate': (
                    ((row['delivered'] or 0) + 0.5 * (row['partial'] or 0)) / 
                    max(row['total'] or 1, 1)
                )
            }
    
    # -------------------------------------------------------------------------
    # VERIFICATION OPERATIONS
    # -------------------------------------------------------------------------
    
    def create_verification(self, data: Dict) -> str:
        """Create a new verification record."""
        verification_id = data.get('id') or self._generate_id("VER")
        
        # Convert photos list to JSON if needed
        photos = data.get('photos')
        if isinstance(photos, list):
            photos = json.dumps(photos)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO verifications (
                    id, validation_id, agent_id, verified, quality_score,
                    evidence_type, photos, gps_latitude, gps_longitude,
                    gps_accuracy, signature_data, notes, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                verification_id,
                data.get('validation_id'),
                data.get('agent_id'),
                data.get('verified', 0),
                data.get('quality_score'),
                data.get('evidence_type'),
                photos,
                data.get('gps_latitude'),
                data.get('gps_longitude'),
                data.get('gps_accuracy'),
                data.get('signature_data'),
                data.get('notes'),
                data.get('timestamp', datetime.now().isoformat())
            ))
            conn.commit()
        
        return verification_id
    
    def get_verifications_by_validation(self, validation_id: str) -> List[Dict]:
        """Get all verifications for a validation."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM verifications WHERE validation_id = ? ORDER BY timestamp DESC",
                (validation_id,)
            )
            results = []
            for row in cursor.fetchall():
                d = self._row_to_dict(row)
                # Parse photos JSON
                if d.get('photos'):
                    try:
                        d['photos'] = json.loads(d['photos'])
                    except:
                        pass
                results.append(d)
            return results
    
    def get_verifications_by_agent(self, agent_id: str, limit: int = 50) -> List[Dict]:
        """Get verifications by agent."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT * FROM verifications 
                   WHERE agent_id = ? 
                   ORDER BY timestamp DESC 
                   LIMIT ?""",
                (agent_id, limit)
            )
            return [self._row_to_dict(row) for row in cursor.fetchall()]
    
    def get_verifications_for_address(self, address_id: str) -> List[Dict]:
        """Get all verifications for an address (via validations)."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT v.* FROM verifications v
                JOIN validations val ON v.validation_id = val.id
                WHERE val.address_id = ?
                ORDER BY v.timestamp DESC
            """, (address_id,))
            results = []
            for row in cursor.fetchall():
                d = self._row_to_dict(row)
                if d.get('photos'):
                    try:
                        d['photos'] = json.loads(d['photos'])
                    except:
                        pass
                results.append(d)
            return results
    
    # -------------------------------------------------------------------------
    # CONSENT OPERATIONS
    # -------------------------------------------------------------------------
    
    def create_consent(self, data: Dict) -> str:
        """Create a new consent record."""
        consent_id = data.get('id') or self._generate_id("CON")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO consents (
                    id, subject_id, granter, grantee, scope,
                    consent_artifact, issued_at, expires_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                consent_id,
                data.get('subject_id'),
                data.get('granter'),
                data.get('grantee'),
                json.dumps(data.get('scope', [])),
                data.get('consent_artifact'),
                data.get('issued_at', datetime.now().isoformat()),
                data.get('expires_at')
            ))
            conn.commit()
        
        return consent_id
    
    def get_consent(self, consent_id: str) -> Optional[Dict]:
        """Get consent by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM consents WHERE id = ?", (consent_id,))
            row = cursor.fetchone()
            if row:
                d = self._row_to_dict(row)
                if d.get('scope'):
                    try:
                        d['scope'] = json.loads(d['scope'])
                    except:
                        pass
                return d
            return None
    
    def revoke_consent(self, consent_id: str, reason: str = None) -> bool:
        """Revoke a consent."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE consents 
                SET revoked = 1, 
                    revoked_at = ?,
                    revocation_reason = ?
                WHERE id = ?
            """, (datetime.now().isoformat(), reason, consent_id))
            conn.commit()
            return cursor.rowcount > 0
    
    # -------------------------------------------------------------------------
    # AUDIT LOG OPERATIONS
    # -------------------------------------------------------------------------
    
    def log_audit(self, data: Dict) -> str:
        """Create an audit log entry."""
        import hashlib
        
        log_id = self._generate_id("LOG")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get previous hash for chain
            cursor.execute(
                "SELECT entry_hash FROM audit_logs ORDER BY timestamp DESC LIMIT 1"
            )
            row = cursor.fetchone()
            prev_hash = row['entry_hash'] if row else "GENESIS"
            
            # Create entry hash
            entry_data = json.dumps({
                'id': log_id,
                'timestamp': datetime.now().isoformat(),
                'prev_hash': prev_hash,
                **data
            }, sort_keys=True)
            entry_hash = hashlib.sha256(entry_data.encode()).hexdigest()
            
            cursor.execute("""
                INSERT INTO audit_logs (
                    id, actor, action, resource_type, resource_id,
                    details, ip_address, prev_hash, entry_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                log_id,
                data.get('actor'),
                data.get('action'),
                data.get('resource_type'),
                data.get('resource_id'),
                json.dumps(data.get('details', {})),
                data.get('ip_address'),
                prev_hash,
                entry_hash
            ))
            conn.commit()
        
        return log_id
    
    def get_audit_logs(
        self, 
        resource_type: str = None,
        resource_id: str = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get audit logs with optional filtering."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM audit_logs WHERE 1=1"
            params = []
            
            if resource_type:
                query += " AND resource_type = ?"
                params.append(resource_type)
            
            if resource_id:
                query += " AND resource_id = ?"
                params.append(resource_id)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            
            results = []
            for row in cursor.fetchall():
                d = self._row_to_dict(row)
                if d.get('details'):
                    try:
                        d['details'] = json.loads(d['details'])
                    except:
                        pass
                results.append(d)
            
            return results
    
    # -------------------------------------------------------------------------
    # DASHBOARD STATISTICS
    # -------------------------------------------------------------------------
    
    def get_dashboard_stats(self) -> Dict:
        """Get overall dashboard statistics."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # Address stats
            cursor.execute("SELECT COUNT(*) as count FROM addresses")
            stats['total_addresses'] = cursor.fetchone()['count']
            
            cursor.execute(
                "SELECT AVG(confidence_score) as avg FROM addresses WHERE confidence_score > 0"
            )
            stats['avg_confidence'] = cursor.fetchone()['avg'] or 0
            
            # Validation stats
            cursor.execute("SELECT COUNT(*) as count FROM validations")
            stats['total_validations'] = cursor.fetchone()['count']
            
            cursor.execute(
                "SELECT COUNT(*) as count FROM validations WHERE status = 'PENDING'"
            )
            stats['pending_validations'] = cursor.fetchone()['count']
            
            cursor.execute(
                "SELECT COUNT(*) as count FROM validations WHERE status = 'COMPLETED'"
            )
            stats['completed_validations'] = cursor.fetchone()['count']
            
            # Agent stats
            cursor.execute("SELECT COUNT(*) as count FROM agents WHERE active = 1")
            stats['active_agents'] = cursor.fetchone()['count']
            
            # Recent activity
            cursor.execute("""
                SELECT COUNT(*) as count 
                FROM validations 
                WHERE DATE(created_at) = DATE('now')
            """)
            stats['validations_today'] = cursor.fetchone()['count']
            
            # Delivery stats
            cursor.execute("SELECT COUNT(*) as count FROM deliveries")
            stats['total_deliveries'] = cursor.fetchone()['count']
            
            cursor.execute("""
                SELECT 
                    SUM(CASE WHEN status = 'DELIVERED' THEN 1 ELSE 0 END) * 100.0 / 
                    NULLIF(COUNT(*), 0) as rate
                FROM deliveries
            """)
            stats['delivery_success_rate'] = cursor.fetchone()['rate'] or 0
            
            return stats


# =============================================================================
# GLOBAL DATABASE INSTANCE
# =============================================================================

_db_instance = None

def get_database(db_path: str = "data/aava.db") -> DatabaseManager:
    """Get or create the global database instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseManager(db_path)
        _db_instance.initialize()
    return _db_instance


# =============================================================================
# TEST CODE
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("DATABASE MANAGER - TEST SUITE")
    print("=" * 70)
    
    # Use test database
    db = DatabaseManager("data/test_aava.db")
    db.initialize()
    
    print("\n✓ Database initialized")
    
    # Test address creation
    print("\n📍 Testing Address Operations...")
    address_id = db.create_address({
        'digital_address': 'test.user@aava.in',
        'digipin': '3PJK4M5L2T',
        'descriptive_address': '123 Test Street, New Delhi',
        'latitude': 28.6139,
        'longitude': 77.2090,
        'city': 'New Delhi',
        'state': 'Delhi',
        'pincode': '110001'
    })
    print(f"  Created address: {address_id}")
    
    address = db.get_address(address_id)
    print(f"  Retrieved: {address['digital_address']}")
    
    # Test agent creation
    print("\n👤 Testing Agent Operations...")
    agent_id = db.create_agent({
        'name': 'Test Agent',
        'email': 'agent@test.com',
        'phone': '+91-9876543210',
        'certification_date': '2024-01-01',
        'certification_expiry': '2025-01-01'
    })
    print(f"  Created agent: {agent_id}")
    
    # Test validation creation
    print("\n📋 Testing Validation Operations...")
    validation_id = db.create_validation({
        'address_id': address_id,
        'digital_address': 'test.user@aava.in',
        'digipin': '3PJK4M5L2T',
        'validation_type': 'HYBRID',
        'priority': 'NORMAL',
        'assigned_agent_id': agent_id
    })
    print(f"  Created validation: {validation_id}")
    
    # Test delivery creation
    print("\n📦 Testing Delivery Operations...")
    for i in range(5):
        db.create_delivery({
            'address_id': address_id,
            'status': 'DELIVERED' if i < 4 else 'FAILED',
            'actual_latitude': 28.6139 + 0.0001 * i,
            'actual_longitude': 77.2090 + 0.0001 * i,
            'ease_rating': 4
        })
    print(f"  Created 5 delivery records")
    
    delivery_stats = db.get_delivery_stats(address_id)
    print(f"  Delivery stats: {delivery_stats['success_rate']:.0%} success rate")
    
    # Test verification creation
    print("\n✅ Testing Verification Operations...")
    verification_id = db.create_verification({
        'validation_id': validation_id,
        'agent_id': agent_id,
        'verified': 1,
        'quality_score': 0.95,
        'evidence_type': 'photo',
        'photos': ['photo1.jpg', 'photo2.jpg'],
        'gps_latitude': 28.6139,
        'gps_longitude': 77.2090,
        'gps_accuracy': 5.0
    })
    print(f"  Created verification: {verification_id}")
    
    # Test audit log
    print("\n📝 Testing Audit Log...")
    log_id = db.log_audit({
        'actor': 'test_user',
        'action': 'validation.created',
        'resource_type': 'validation',
        'resource_id': validation_id,
        'details': {'test': True}
    })
    print(f"  Created audit log: {log_id}")
    
    # Test dashboard stats
    print("\n📊 Dashboard Statistics:")
    stats = db.get_dashboard_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 70)
    print("ALL TESTS COMPLETED")
    print("=" * 70)
    
    # Cleanup test database
    db.close()
    import os
    if os.path.exists("data/test_aava.db"):
        os.remove("data/test_aava.db")
        print("\n✓ Test database cleaned up")
