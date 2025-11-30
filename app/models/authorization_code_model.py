from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from app.db.database import Base

class AuthorizationCode(Base):
    __tablename__ = "authorization_codes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    client_id = Column(String, index=True, nullable=False)
    code_challenge = Column(String, nullable=False)
    code_challenge_method = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    redirect_uri = Column(String, nullable=False)
