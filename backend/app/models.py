from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String) # Admin, Senior Officer, Investigator
    full_name = Column(String)

class Case(Base):
    __tablename__ = "cases"
    case_id = Column(String, primary_key=True, index=True) # e.g. CASE-2026-001
    title = Column(String)
    description = Column(Text)
    classification = Column(String)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    documents = relationship("Document", back_populates="case")

class Document(Base):
    __tablename__ = "documents"
    document_id = Column(String, primary_key=True, index=True) # e.g. FIR-001
    case_id = Column(String, ForeignKey("cases.case_id"))
    title = Column(String)
    document_type = Column(String)
    classification = Column(String)
    owner = Column(String)
    uploaded_by = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    case = relationship("Case", back_populates="documents")
    versions = relationship("DocumentVersion", back_populates="document", order_by="desc(DocumentVersion.version_number)")

class DocumentVersion(Base):
    __tablename__ = "document_versions"
    version_id = Column(String, primary_key=True, index=True)
    document_id = Column(String, ForeignKey("documents.document_id"))
    version_number = Column(Integer)
    file_path = Column(String)
    sha256_hash = Column(String)
    created_by = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    change_description = Column(Text)

    # Relationships
    document = relationship("Document", back_populates="versions")

class CaseAccess(Base):
    """Mapping of which User has access to which Case"""
    __tablename__ = "case_access"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    case_id = Column(String, ForeignKey("cases.case_id"))

class AuditEvent(Base):
    __tablename__ = "audit_events"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    username = Column(String)
    role = Column(String)
    action = Column(String) # VIEW_DOCUMENT, LOGIN, SEARCH, etc.
    document_id = Column(String, nullable=True)
    case_id = Column(String, nullable=True)
    version = Column(Integer, nullable=True)
    result = Column(String) # SUCCESS, ACCESS_DENIED, INTEGRITY_VERIFIED, TAMPER_DETECTED
    ip_address = Column(String, nullable=True)
