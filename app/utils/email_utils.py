import logging
from dataclasses import dataclass
from email.message import EmailMessage

import aiosmtplib

from app.config import settings

# 取得 logger 實例，通常以模組名稱命名
logger = logging.getLogger(__name__)


class EmailSenderError(Exception):
    pass


# ----------------------------------------------------
# A. 定義資料結構與邏輯 (DTO)
# ----------------------------------------------------


@dataclass
class EmailContext:
    """
    將郵件內容打包，並包含測試模式的處理邏輯。
    """

    to: list[str]
    subject: str
    body_html: str
    cc: list[str] = []
    bcc: list[str] = []
    body_plain: str | None = None

    def apply_test_mode_if_needed(self) -> None:
        """
        如果開啟測試模式，直接修改此物件內部的數據。
        """
        if not settings.MAIL_TEST_MODE:
            return

        # 1. 準備警示訊息
        info_html = (
            f"<div style='background-color:#fff3cd; color:#856404; padding:15px; "
            f"border:1px solid #ffeeba; margin-bottom:20px; font-family:sans-serif;'>"
            f"<strong>⚠️ [測試模式攔截]</strong><br>"
            f"Original To: {', '.join(self.to)}<br>"
            f"Original Cc: {', '.join(self.cc or [])}<br>"
            f"Original Bcc: {', '.join(self.bcc or [])}</div><hr>"
        )

        info_plain = (
            f"[測試模式攔截] 原本收件人:\nTo: {', '.join(self.to)}\n"
            f"Cc: {', '.join(self.cc or [])}\nBcc: {', '.join(self.bcc or [])}\n"
            f"----------------------------------------\n"
        )

        # 2. 修改內容 (注入警示)
        self.body_html = info_html + self.body_html

        if self.body_plain:
            self.body_plain = info_plain + self.body_plain
        else:
            self.body_plain = info_plain + "(Original content was HTML only)"

        # 3. 替換收件人 (清空 CC/BCC)
        self.to = settings.SYSTEM_OWNER_EMAIL
        self.cc = []
        self.bcc = []


# ----------------------------------------------------
# B. 核心發送邏輯
# ----------------------------------------------------


async def _send_smtp(message: EmailMessage, recipients: list[str]) -> bool:
    """
    使用 aiosmtplib 發送郵件，錯誤時記錄日誌並返回 False。

    :param message: 構造好的 EmailMessage 物件
    :param recipients: 郵件的實際收件人列表 (To, Cc, Bcc 的集合)
    :return: 成功發送返回 True, 失敗返回 False
    """
    # 確保收件人列表非空，避免不必要的 SMTP 連線
    if not recipients:
        logger.warning(f"發送郵件被跳過: 收件人列表為空 (Subject: {message.get('Subject')})")
        return False

    try:
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            use_tls=settings.SMTP_TLS,
            recipients=recipients,
            timeout=30.0,
        )
        # 成功發送
        logger.info(f"郵件發送成功: Subject='{message.get('Subject')}', Recipients={len(recipients)}")
        return True

    except aiosmtplib.SMTPException as e:
        # 處理 SMTP 協定相關的錯誤 (如認證失敗、收件人被拒絕等)
        logger.error(
            f"發送郵件失敗 (SMTP Error): Subject='{message.get('Subject')}', Recipients={recipients}, Error={e}",
            exc_info=True,  # 記錄完整的 Traceback
        )
        return False

    except Exception as e:
        # 處理其他未預期錯誤 (如連線超時、DNS 解析失敗、IO 錯誤等)
        logger.critical(
            f"發送郵件失敗 (Critical/Unexpected Error): Subject='{message.get('Subject')}', Error={e.__class__.__name__}: {e}",
            exc_info=True,  # 記錄完整的 Traceback
        )
        return False


# ----------------------------------------------------
# C. 公共介面
# ----------------------------------------------------


async def send_email(
    recipients_to: list[str],
    subject: str,
    body_html: str,
    body_plain: str | None = None,
    recipients_cc: list[str] | None = None,
    recipients_bcc: list[str] | None = None,
) -> bool:
    # 1. 打包參數 (建立 Context 物件)
    ctx = EmailContext(
        to=recipients_to,
        subject=subject,
        body_html=body_html,
        body_plain=body_plain,
        cc=recipients_cc or [],
        bcc=recipients_bcc or [],
    )

    # 2. 應用商業規則 (一句話搞定，不用傳來傳去)
    ctx.apply_test_mode_if_needed()

    # 3. 構建郵件 (從 ctx 取值)
    message = EmailMessage()
    message["From"] = settings.MAIL_FROM
    message["To"] = ", ".join(ctx.to)
    message["Subject"] = ctx.subject

    if ctx.cc:
        message["Cc"] = ", ".join(ctx.cc)

    # 內容設定
    fallback_plain = ctx.body_plain or "此郵件需要 HTML 閱讀器才能完整顯示內容。"
    message.set_content(fallback_plain, subtype="plain")
    message.add_alternative(ctx.body_html, subtype="html")

    # 4. 執行發送
    # Envelope Recipients 包含 To + Cc + Bcc
    all_recipients = ctx.to + ctx.cc + ctx.bcc
    return await _send_smtp(message, all_recipients)
