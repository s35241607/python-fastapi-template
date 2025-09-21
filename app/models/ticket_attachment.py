from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from app.config import settings
from app.models.base import Base


class TicketAttachment(Base):
    __tablename__ = "ticket_attachments"
    __table_args__ = {"schema": settings.db_schema}

    id = Column(BigInteger, primary_key=True)
    ticket_id = Column(BigInteger, ForeignKey("ticket.tickets.id", ondelete="CASCADE"))
    file_name = Column(String(255))  # 原始檔名
    file_path = Column(String(500))  # MinIO 中的檔案路徑
    bucket_name = Column(String(100))  # MinIO 儲存桶名稱
    file_size = Column(BigInteger)
    mime_type = Column(String(100))
    is_image = Column(Boolean, default=False)  # 是否為圖片檔案
    
    # 圖片相關欄位 (如果是圖片)
    image_width = Column(BigInteger)
    image_height = Column(BigInteger)
    
    # 檔案用途 (attachment: 一般附件, inline_image: 內嵌圖片)
    usage_type = Column(String(50), default="attachment")
    
    # 檔案描述或備註
    description = Column(Text)
    
    # 檔案狀態 (uploading: 上傳中, completed: 完成, failed: 失敗)
    status = Column(String(20), default="completed")
    
    # MinIO URL (快取用，可定期重新生成)
    file_url = Column(Text)
    url_expires_at = Column(DateTime(timezone=True))
    
    created_by = Column(BigInteger)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_by = Column(BigInteger)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_by = Column(BigInteger)
    deleted_at = Column(DateTime(timezone=True))

    ticket = relationship("Ticket", back_populates="attachments")
