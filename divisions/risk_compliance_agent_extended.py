"""
Risk & Compliance Agent - Extended Functions
Enterprise fraud detection, AML/KYC compliance, and risk management
"""

import os
import json
import sys
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional, Dict, Any
from enum import Enum
import hashlib
import re

# Import existing base
try:
    from .risk_compliance_agent import RiskComplianceAgent
except ImportError:
    sys.path.insert(0, os.path.dirname(__file__))
    from risk_compliance_agent import RiskComplianceAgent


class FraudRiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AMLStatus(Enum):
    CLEAR = "clear"
    PENDING = "pending"
    FLAGGED = "flagged"
    BLOCKED = "blocked"


class RiskComplianceAgentExtended(RiskComplianceAgent):
    """Extended Risk & Compliance with enterprise fraud detection and AML/KYC"""

    def __init__(self, config):
        super().__init__(config)
        self.device_fingerprints = {}
        self.behavioral_profiles = {}
        self.sanctions_cache = {}
        self.pep_database = {}  # In production: external API
        self.merchant_reputation_db = {}
        self.sar_filings = {}  # Suspicious Activity Reports
        self.ctr_filings = {}  # Currency Transaction Reports

    # ============================================================================
    # ADVANCED FRAUD DETECTION
    # ============================================================================

    def behavioral_biometrics_analysis(
        self,
        agent_id: str,
        session_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze typing patterns and mouse movements for fraud detection

        Args:
            agent_id: Agent being analyzed
            session_data: {
                "typing_speed": float,  # words per minute
                "keystroke_dynamics": List[float],  # inter-key delays
                "mouse_movements": List[tuple],  # (x, y, timestamp)
                "scrolling_pattern": dict,
                "session_duration": float
            }

        Returns:
            Risk assessment with behavioral score
        """
        # Get historical behavioral profile
        profile = self.behavioral_profiles.get(agent_id, {})

        if not profile:
            # First time - create baseline
            profile = self._create_behavioral_baseline(session_data)
            self.behavioral_profiles[agent_id] = profile
            return {
                "risk_score": 0,
                "risk_level": FraudRiskLevel.LOW.value,
                "is_baseline": True,
                "message": "Behavioral baseline created"
            }

        # Compare current session to baseline
        typing_deviation = abs(
            session_data["typing_speed"] - profile["avg_typing_speed"]
        ) / profile["avg_typing_speed"]

        # Keystroke dynamics analysis (rhythm)
        keystroke_score = self._analyze_keystroke_dynamics(
            session_data["keystroke_dynamics"],
            profile["keystroke_pattern"]
        )

        # Mouse movement analysis
        mouse_score = self._analyze_mouse_patterns(
            session_data["mouse_movements"],
            profile["mouse_pattern"]
        )

        # Calculate overall behavioral score (0-100)
        behavioral_score = (
            (typing_deviation * 30) +
            ((1 - keystroke_score) * 40) +
            ((1 - mouse_score) * 30)
        ) * 100

        risk_level = self._classify_risk(behavioral_score)

        # Alert if high deviation
        if behavioral_score > 70:
            self._create_fraud_alert(
                agent_id,
                "behavioral_anomaly",
                f"Behavioral score: {behavioral_score:.1f}",
                risk_level
            )

        return {
            "agent_id": agent_id,
            "risk_score": round(behavioral_score, 2),
            "risk_level": risk_level.value,
            "details": {
                "typing_deviation": round(typing_deviation * 100, 2),
                "keystroke_match": round(keystroke_score * 100, 2),
                "mouse_match": round(mouse_score * 100, 2)
            },
            "recommendation": "block" if behavioral_score > 80 else "review" if behavioral_score > 60 else "approve"
        }

    def device_fingerprinting(
        self,
        agent_id: str,
        device_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze device characteristics for fraud detection

        Args:
            device_data: {
                "user_agent": str,
                "browser": str,
                "os": str,
                "screen_resolution": str,
                "timezone": str,
                "language": str,
                "plugins": List[str],
                "canvas_fingerprint": str,
                "webgl_fingerprint": str
            }

        Returns:
            Device risk assessment
        """
        # Generate unique device fingerprint
        device_hash = self._generate_device_fingerprint(device_data)

        # Check if known device
        agent_devices = self.device_fingerprints.get(agent_id, [])

        is_known_device = device_hash in [d["hash"] for d in agent_devices]

        if not is_known_device:
            # New device
            device_record = {
                "hash": device_hash,
                "first_seen": datetime.now().isoformat(),
                "last_seen": datetime.now().isoformat(),
                "data": device_data,
                "trust_score": 50  # Neutral for new devices
            }

            agent_devices.append(device_record)
            self.device_fingerprints[agent_id] = agent_devices

            # Alert on new device
            self._send_notification(
                agent_id,
                f"New device detected: {device_data['browser']} on {device_data['os']}"
            )

            risk_score = 60  # Moderate risk for new device
        else:
            # Known device - update last seen
            for device in agent_devices:
                if device["hash"] == device_hash:
                    device["last_seen"] = datetime.now().isoformat()
                    device["trust_score"] = min(device["trust_score"] + 5, 100)
                    risk_score = 100 - device["trust_score"]
                    break

        # Additional checks
        risk_factors = []

        # Check for VPN/Proxy
        if self._is_vpn_or_proxy(device_data):
            risk_factors.append("vpn_detected")
            risk_score += 20

        # Check for emulation/automation
        if self._is_emulated_device(device_data):
            risk_factors.append("emulation_detected")
            risk_score += 30

        risk_score = min(risk_score, 100)
        risk_level = self._classify_risk(risk_score)

        return {
            "device_hash": device_hash,
            "is_known_device": is_known_device,
            "risk_score": risk_score,
            "risk_level": risk_level.value,
            "risk_factors": risk_factors,
            "recommendation": "block" if risk_score > 80 else "challenge" if risk_score > 50 else "approve"
        }

    def geolocation_risk_analysis(
        self,
        agent_id: str,
        ip_address: str,
        transaction: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze geographic anomalies and impossible travel

        Args:
            ip_address: Current IP
            transaction: Transaction details

        Returns:
            Geographic risk assessment
        """
        # Get IP geolocation (in production: use MaxMind GeoIP2)
        current_location = self._geolocate_ip(ip_address)

        # Get agent's historical locations
        agent_locations = self._get_historical_locations(agent_id)

        if not agent_locations:
            # First transaction - establish baseline
            self._save_location(agent_id, current_location)
            return {
                "risk_score": 0,
                "risk_level": FraudRiskLevel.LOW.value,
                "is_baseline": True
            }

        # Check for impossible travel
        last_location = agent_locations[-1]
        time_diff = (
            datetime.now() -
            datetime.fromisoformat(last_location["timestamp"])
        ).total_seconds() / 3600  # hours

        distance_km = self._calculate_distance(
            last_location["lat"],
            last_location["lon"],
            current_location["lat"],
            current_location["lon"]
        )

        # Maximum possible speed (accounting for flights)
        max_speed_kmh = 900  # ~Mach 0.85
        required_speed = distance_km / time_diff if time_diff > 0 else float('inf')

        impossible_travel = required_speed > max_speed_kmh

        # Risk factors
        risk_score = 0
        risk_factors = []

        if impossible_travel:
            risk_score += 50
            risk_factors.append("impossible_travel")

        # High-risk countries
        if current_location["country_code"] in self._get_high_risk_countries():
            risk_score += 30
            risk_factors.append("high_risk_country")

        # VPN/Proxy from different country
        if current_location.get("is_vpn") and current_location["country_code"] != last_location.get("country_code"):
            risk_score += 20
            risk_factors.append("vpn_country_mismatch")

        # Unusual location (never been there before)
        if current_location["country_code"] not in [loc["country_code"] for loc in agent_locations]:
            risk_score += 15
            risk_factors.append("new_country")

        risk_level = self._classify_risk(risk_score)

        # Save current location
        self._save_location(agent_id, current_location)

        return {
            "current_location": current_location,
            "last_location": last_location,
            "distance_km": round(distance_km, 2),
            "time_diff_hours": round(time_diff, 2),
            "impossible_travel": impossible_travel,
            "risk_score": risk_score,
            "risk_level": risk_level.value,
            "risk_factors": risk_factors,
            "recommendation": "block" if risk_score > 70 else "review" if risk_score > 40 else "approve"
        }

    def merchant_reputation_check(
        self,
        merchant_id: str,
        merchant_category: str
    ) -> Dict[str, Any]:
        """
        Check merchant risk level and reputation

        Args:
            merchant_id: Merchant identifier
            merchant_category: MCC (Merchant Category Code)

        Returns:
            Merchant risk assessment
        """
        # Get merchant from database
        merchant = self.merchant_reputation_db.get(merchant_id, {})

        if not merchant:
            # New merchant - moderate risk
            merchant = {
                "merchant_id": merchant_id,
                "category": merchant_category,
                "first_seen": datetime.now().isoformat(),
                "transaction_count": 0,
                "chargeback_count": 0,
                "fraud_reports": 0,
                "reputation_score": 50
            }
            self.merchant_reputation_db[merchant_id] = merchant

        # High-risk categories (gambling, crypto, adult, etc.)
        high_risk_categories = [
            "7995",  # Gambling
            "6051",  # Crypto
            "5967",  # Direct marketing
            "5122"   # Drugs/pharmaceuticals
        ]

        risk_score = 0

        # Category risk
        if merchant_category in high_risk_categories:
            risk_score += 40

        # Chargeback rate
        if merchant["transaction_count"] > 0:
            chargeback_rate = merchant["chargeback_count"] / merchant["transaction_count"]
            if chargeback_rate > 0.01:  # >1% chargeback rate is high
                risk_score += 30

        # Fraud reports
        if merchant["fraud_reports"] > 5:
            risk_score += 30

        # Reputation score
        risk_score += (100 - merchant["reputation_score"]) * 0.5

        risk_level = self._classify_risk(risk_score)

        return {
            "merchant_id": merchant_id,
            "category": merchant_category,
            "reputation_score": merchant["reputation_score"],
            "transaction_count": merchant["transaction_count"],
            "chargeback_rate": round(
                merchant["chargeback_count"] / max(merchant["transaction_count"], 1) * 100,
                2
            ),
            "fraud_reports": merchant["fraud_reports"],
            "risk_score": round(risk_score, 2),
            "risk_level": risk_level.value,
            "recommendation": "block" if risk_score > 80 else "review" if risk_score > 50 else "approve"
        }

    def account_takeover_detection(
        self,
        agent_id: str,
        login_event: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Detect account takeover attempts

        Args:
            login_event: {
                "ip_address": str,
                "device_fingerprint": str,
                "location": dict,
                "password_changed": bool,
                "email_changed": bool,
                "phone_changed": bool,
                "failed_attempts_before": int
            }

        Returns:
            ATO risk assessment
        """
        risk_score = 0
        indicators = []

        # Multiple failed login attempts
        if login_event["failed_attempts_before"] >= 3:
            risk_score += 30
            indicators.append("multiple_failed_logins")

        # Password changed from new device
        if login_event["password_changed"] and not self._is_known_device(agent_id, login_event["device_fingerprint"]):
            risk_score += 40
            indicators.append("password_change_new_device")

        # Email or phone changed
        if login_event["email_changed"] or login_event["phone_changed"]:
            risk_score += 35
            indicators.append("contact_info_changed")

        # Login from unusual location
        if not self._is_usual_location(agent_id, login_event["location"]):
            risk_score += 25
            indicators.append("unusual_location")

        # Suspicious timing (e.g., 3 AM)
        hour = datetime.now().hour
        if hour < 6 or hour > 23:
            risk_score += 10
            indicators.append("unusual_time")

        risk_level = self._classify_risk(risk_score)

        # If high risk, freeze account immediately
        if risk_score > 70:
            self._freeze_account_for_security(
                agent_id,
                "Possible account takeover detected"
            )

        return {
            "agent_id": agent_id,
            "risk_score": risk_score,
            "risk_level": risk_level.value,
            "indicators": indicators,
            "account_frozen": risk_score > 70,
            "recommendation": "freeze_account" if risk_score > 70 else "challenge_mfa" if risk_score > 40 else "allow"
        }

    # ============================================================================
    # AML/KYC COMPLIANCE
    # ============================================================================

    def screen_sanctions_lists(
        self,
        agent_name: str,
        date_of_birth: str,
        nationality: str
    ) -> Dict[str, Any]:
        """
        Screen against OFAC, UN, EU sanctions lists

        Args:
            agent_name: Full name
            date_of_birth: YYYY-MM-DD
            nationality: Country code

        Returns:
            Sanctions screening result
        """
        # In production: use ComplyAdvantage, Dow Jones, or similar API

        # Check cache first
        cache_key = hashlib.sha256(
            f"{agent_name}{date_of_birth}{nationality}".encode()
        ).hexdigest()

        if cache_key in self.sanctions_cache:
            cached = self.sanctions_cache[cache_key]
            if (datetime.now() - datetime.fromisoformat(cached["screened_at"])).days < 1:
                return cached["result"]

        # Screen against lists (simulated)
        matches = []

        # OFAC SDN List (Specially Designated Nationals)
        ofac_match = self._check_ofac_sdn(agent_name, date_of_birth)
        if ofac_match:
            matches.append({
                "list": "OFAC_SDN",
                "name": ofac_match["name"],
                "match_score": ofac_match["score"],
                "details": ofac_match
            })

        # UN Consolidated List
        un_match = self._check_un_list(agent_name)
        if un_match:
            matches.append({
                "list": "UN_CONSOLIDATED",
                "name": un_match["name"],
                "match_score": un_match["score"]
            })

        # EU Sanctions List
        eu_match = self._check_eu_list(agent_name, nationality)
        if eu_match:
            matches.append({
                "list": "EU_SANCTIONS",
                "name": eu_match["name"],
                "match_score": eu_match["score"]
            })

        status = AMLStatus.CLEAR.value if not matches else AMLStatus.BLOCKED.value

        result = {
            "status": status,
            "matches": matches,
            "screened_at": datetime.now().isoformat(),
            "lists_checked": ["OFAC_SDN", "UN_CONSOLIDATED", "EU_SANCTIONS"],
            "recommendation": "block" if matches else "approve"
        }

        # Cache result
        self.sanctions_cache[cache_key] = {
            "screened_at": datetime.now().isoformat(),
            "result": result
        }

        # If match, create alert
        if matches:
            self._create_compliance_alert(
                agent_name,
                "sanctions_match",
                f"Matched {len(matches)} sanctions list(s)",
                matches
            )

        return result

    def check_pep_status(
        self,
        agent_name: str,
        country: str
    ) -> Dict[str, Any]:
        """
        Check if Politically Exposed Person (PEP)

        PEPs include:
        - Government officials
        - Military leaders
        - Judges, legislators
        - Senior executives of state-owned companies
        - Family members and close associates

        Returns:
            PEP status and details
        """
        # In production: use World-Check, Dow Jones, or ComplyAdvantage

        # Check PEP database
        pep_match = self._search_pep_database(agent_name, country)

        if pep_match:
            # PEP found
            return {
                "is_pep": True,
                "pep_type": pep_match["type"],  # "domestic", "foreign", "international_organization"
                "role": pep_match["role"],
                "country": pep_match["country"],
                "confidence_score": pep_match["confidence"],
                "source": pep_match["source"],
                "requires_edd": True,  # Enhanced Due Diligence required
                "risk_level": FraudRiskLevel.HIGH.value,
                "recommendation": "enhanced_due_diligence"
            }
        else:
            # Not a PEP
            return {
                "is_pep": False,
                "requires_edd": False,
                "risk_level": FraudRiskLevel.LOW.value,
                "recommendation": "standard_due_diligence"
            }

    def adverse_media_screening(
        self,
        agent_name: str
    ) -> Dict[str, Any]:
        """
        Search for negative news and media mentions

        Searches for:
        - Fraud, embezzlement, corruption
        - Money laundering
        - Tax evasion
        - Court cases, lawsuits
        - Bankruptcy

        Returns:
            Adverse media findings
        """
        # In production: use World-Check, LexisNexis, or web scraping

        # Search news sources (simulated)
        articles = self._search_news_sources(agent_name)

        # Categorize articles
        adverse_articles = []
        for article in articles:
            if self._is_adverse_content(article["content"]):
                adverse_articles.append({
                    "title": article["title"],
                    "source": article["source"],
                    "date": article["date"],
                    "category": self._categorize_adverse_content(article["content"]),
                    "severity": self._assess_severity(article["content"]),
                    "url": article["url"]
                })

        risk_score = len(adverse_articles) * 15  # Each article adds 15 points
        risk_level = self._classify_risk(risk_score)

        return {
            "agent_name": agent_name,
            "total_articles_found": len(articles),
            "adverse_articles_count": len(adverse_articles),
            "adverse_articles": adverse_articles,
            "risk_score": min(risk_score, 100),
            "risk_level": risk_level.value,
            "requires_review": len(adverse_articles) > 0,
            "recommendation": "decline" if risk_score > 70 else "manual_review" if risk_score > 30 else "approve"
        }

    def file_suspicious_activity_report(
        self,
        agent_id: str,
        reason: str,
        details: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        File SAR (Suspicious Activity Report) with FinCEN

        Required for:
        - Transactions >= $5,000 with suspicious patterns
        - Structuring (breaking up large transactions)
        - Money laundering indicators
        - Terrorist financing

        Deadline: 30 days from detection

        Args:
            agent_id: Subject of report
            reason: Reason code
            details: Additional details

        Returns:
            SAR filing confirmation
        """
        sar_id = f"SAR-{datetime.now().strftime('%Y%m%d')}-{len(self.sar_filings) + 1:04d}"

        sar = {
            "sar_id": sar_id,
            "agent_id": agent_id,
            "reason": reason,
            "details": details,
            "filed_at": datetime.now().isoformat(),
            "filed_by": "RiskComplianceAgent",
            "status": "filed",
            "fincen_status": "pending"  # Will be updated when acknowledged
        }

        self.sar_filings[sar_id] = sar

        # In production: Submit to FinCEN BSA E-Filing System
        # self._submit_to_fincen(sar)

        # Freeze account if severe
        if reason in ["money_laundering", "terrorist_financing"]:
            self._freeze_account_for_compliance(agent_id, f"SAR filed: {reason}")

        # Notify compliance team
        self._notify_compliance_team(
            f"SAR filed: {sar_id}",
            sar
        )

        return {
            "sar_id": sar_id,
            "status": "filed",
            "deadline": (datetime.now() + timedelta(days=30)).isoformat(),
            "message": "SAR filed with FinCEN. Account may be frozen pending review."
        }

    def file_currency_transaction_report(
        self,
        transaction_id: str,
        amount: Decimal
    ) -> Dict[str, str]:
        """
        File CTR (Currency Transaction Report) for cash transactions > $10K

        Required by law for:
        - Single cash transaction > $10,000
        - Multiple related transactions totaling > $10,000 in one day

        Args:
            transaction_id: Transaction ID
            amount: Transaction amount

        Returns:
            CTR filing confirmation
        """
        if amount < Decimal("10000.00"):
            return {
                "status": "not_required",
                "message": "CTR only required for transactions >= $10,000"
            }

        ctr_id = f"CTR-{datetime.now().strftime('%Y%m%d')}-{len(self.ctr_filings) + 1:04d}"

        ctr = {
            "ctr_id": ctr_id,
            "transaction_id": transaction_id,
            "amount": str(amount),
            "filed_at": datetime.now().isoformat(),
            "status": "filed"
        }

        self.ctr_filings[ctr_id] = ctr

        # In production: Submit to FinCEN
        # self._submit_ctr_to_fincen(ctr)

        return {
            "ctr_id": ctr_id,
            "status": "filed",
            "message": f"CTR filed for ${amount} transaction"
        }

    # ============================================================================
    # RISK SCORING & LIMITS
    # ============================================================================

    def calculate_credit_score(
        self,
        agent_id: str
    ) -> Dict[str, Any]:
        """
        Calculate dynamic credit score (300-850 scale like FICO)

        Factors:
        - Payment history (35%)
        - Account age (15%)
        - Transaction volume (25%)
        - Utilization rate (20%)
        - Account variety (5%)

        Returns:
            Credit score and details
        """
        agent = self._get_agent(agent_id)
        account = self._get_account(agent.get("account_id"))

        # Payment history (35% weight)
        payment_score = self._calculate_payment_history_score(agent_id) * 0.35

        # Account age (15% weight)
        account_age_days = (
            datetime.now() -
            datetime.fromisoformat(account["created_at"])
        ).days
        age_score = min(account_age_days / 365 * 100, 100) * 0.15

        # Transaction volume (25% weight)
        tx_volume = self._get_30day_transaction_volume(agent_id)
        volume_score = min(tx_volume / 50000 * 100, 100) * 0.25

        # Utilization rate (20% weight)
        # Low utilization is good (using < 30% of limits)
        utilization = self._calculate_utilization_rate(agent_id)
        utilization_score = (100 - min(utilization * 100, 100)) * 0.20

        # Account variety (5% weight)
        # Having sub-accounts, cards, etc.
        variety_score = self._calculate_account_variety(agent_id) * 0.05

        # Total score (0-100)
        total_score = (
            payment_score +
            age_score +
            volume_score +
            utilization_score +
            variety_score
        )

        # Convert to 300-850 scale (FICO-like)
        credit_score = int(300 + (total_score / 100) * 550)

        # Classification
        if credit_score >= 800:
            rating = "Excellent"
        elif credit_score >= 740:
            rating = "Very Good"
        elif credit_score >= 670:
            rating = "Good"
        elif credit_score >= 580:
            rating = "Fair"
        else:
            rating = "Poor"

        return {
            "agent_id": agent_id,
            "credit_score": credit_score,
            "rating": rating,
            "factors": {
                "payment_history": round(payment_score / 0.35, 2),
                "account_age": round(age_score / 0.15, 2),
                "transaction_volume": round(volume_score / 0.25, 2),
                "utilization_rate": round(utilization * 100, 2),
                "account_variety": round(variety_score / 0.05, 2)
            },
            "calculated_at": datetime.now().isoformat()
        }

    # ============================================================================
    # HELPER METHODS
    # ============================================================================

    def _create_behavioral_baseline(self, session_data: dict) -> dict:
        """Create initial behavioral baseline"""
        return {
            "avg_typing_speed": session_data["typing_speed"],
            "keystroke_pattern": session_data["keystroke_dynamics"],
            "mouse_pattern": session_data["mouse_movements"],
            "created_at": datetime.now().isoformat()
        }

    def _analyze_keystroke_dynamics(self, current: List[float], baseline: List[float]) -> float:
        """Compare keystroke patterns (0=no match, 1=perfect match)"""
        if not baseline or not current:
            return 0.5

        # Simple correlation
        from statistics import correlation
        try:
            return max(0, correlation(current[:len(baseline)], baseline))
        except:
            return 0.5

    def _classify_risk(self, score: float) -> FraudRiskLevel:
        """Classify risk level based on score"""
        if score >= 70:
            return FraudRiskLevel.CRITICAL
        elif score >= 50:
            return FraudRiskLevel.HIGH
        elif score >= 30:
            return FraudRiskLevel.MEDIUM
        else:
            return FraudRiskLevel.LOW

    def _generate_device_fingerprint(self, device_data: dict) -> str:
        """Generate unique device fingerprint hash"""
        fingerprint_string = (
            f"{device_data['user_agent']}"
            f"{device_data['screen_resolution']}"
            f"{device_data.get('canvas_fingerprint', '')}"
            f"{device_data.get('webgl_fingerprint', '')}"
        )
        return hashlib.sha256(fingerprint_string.encode()).hexdigest()

    def _geolocate_ip(self, ip_address: str) -> dict:
        """Get geolocation from IP (mock - use MaxMind in production)"""
        # Mock data
        return {
            "ip": ip_address,
            "country": "United States",
            "country_code": "US",
            "city": "New York",
            "lat": 40.7128,
            "lon": -74.0060,
            "is_vpn": False
        }

    def _calculate_distance(self, lat1, lon1, lat2, lon2) -> float:
        """Calculate distance between two points (Haversine formula)"""
        from math import radians, sin, cos, sqrt, atan2

        R = 6371  # Earth radius in km

        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))

        return R * c

    def _get_high_risk_countries(self) -> List[str]:
        """Get list of high-risk country codes"""
        # FATF high-risk jurisdictions
        return [
            "KP",  # North Korea
            "IR",  # Iran
            "MM",  # Myanmar
            # Add more based on current FATF list
        ]

    def _send_notification(self, agent_id: str, message: str):
        """Send notification"""
        print(f"[NOTIFICATION to {agent_id}]: {message}")

    def _create_fraud_alert(self, agent_id: str, alert_type: str, details: str, risk_level: FraudRiskLevel):
        """Create fraud alert"""
        print(f"[FRAUD ALERT] {agent_id}: {alert_type} - {details} ({risk_level.value})")

    def _create_compliance_alert(self, agent_name: str, alert_type: str, details: str, data: Any):
        """Create compliance alert"""
        print(f"[COMPLIANCE ALERT] {agent_name}: {alert_type} - {details}")


# Export
def create_extended_risk_agent(config):
    """Factory function"""
    return RiskComplianceAgentExtended(config)
