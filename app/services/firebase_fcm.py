# import os
# from typing import Dict, Any
# import firebase_admin
# from firebase_admin import messaging, credentials
# from dotenv import load_dotenv
# import logging
# from datetime import datetime

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# load_dotenv()

# class FCMNotificationService:
#     def __init__(self):
#         # Path to your Firebase service account JSON (modern FCM uses this instead of legacy keys)
#         self.service_account_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
        
#         if not self.service_account_path:
#             logger.critical("FIREBASE_CREDENTIALS_PATH environment variable not set")
#             raise RuntimeError("FCM service initialization failed - missing service account key")

#         try:
#             # Initialize Firebase Admin SDK
#             cred = credentials.Certificate(self.service_account_path)
#             firebase_admin.initialize_app(cred)
#             logger.info("FCM (HTTP v1) service initialized successfully")
#             self.service_available = True
#         except Exception as e:
#             logger.critical(f"FCM initialization failed: {str(e)}")
#             self.service_available = False

#     def _prepare_notification_payload(
#         self,
#         task_id: str,
#         task_name: str,
#         manager_name: str
#     ) -> Dict[str, Any]:
#         """Constructs standardized notification payload"""
#         return {
#             "type": "task_assignment",
#             "task_id": task_id,
#             "task_name": task_name,
#             "manager_name": manager_name,
#             "timestamp": datetime.utcnow().isoformat(),
#             "click_action": "FLUTTER_NOTIFICATION_CLICK"
#         }

#     def send_task_notification(
#         self,
#         token: str,
#         task_id: str,
#         task_name: str,
#         manager_name: str,
#         max_retries: int = 2
#     ) -> bool:
#         """
#         Modern FCM notification sender with retry logic.
        
#         Args:
#             token: Device registration token (FCM)
#             task_id: Unique task identifier
#             task_name: Human-readable task name
#             manager_name: Name of assigning manager
#             max_retries: Number of send attempts (default: 2)
            
#         Returns:
#             bool: True if successful, False if failed
#         """
#         if not self.service_available:
#             logger.error("FCM service unavailable - notifications disabled")
#             return False

#         if not token or not isinstance(token, str):
#             logger.error(f"Invalid FCM token: {token}")
#             return False

#         payload = self._prepare_notification_payload(task_id, task_name, manager_name)
        
#         # Modern FCM message structure
#         message = messaging.Message(
#             notification=messaging.Notification(
#                 title=f"New Task: {task_name}",
#                 body=f"Assigned by {manager_name}",
#             ),
#             data=payload,  # Custom data payload
#             token=token,
#             android=messaging.AndroidConfig(priority="high"),
#             apns=messaging.APNSConfig(
#                 headers={"apns-priority": "10"},  # High priority for iOS
#                 payload=messaging.APNSPayload(
#                     aps=messaging.Aps(badge=1, sound="default")
#                 )
#             )
#         )

#         for attempt in range(1, max_retries + 1):
#             try:
#                 response = messaging.send(message)
#                 logger.info(f"Notification sent successfully (message_id: {response})")
#                 return True
#             except messaging.UnregisteredError:
#                 logger.error(f"Invalid FCM token - removing: {token[:6]}...")
#                 return False
#             except Exception as e:
#                 logger.error(f"Attempt {attempt}/{max_retries} failed: {str(e)}")
#                 if attempt == max_retries:
#                     logger.error(f"All {max_retries} attempts failed for task {task_id}")
#                     return False

#         return False

# # Initialize service with health check
# try:
#     fcm_service = FCMNotificationService()
#     if not fcm_service.service_available:
#         logger.error("FCM Service is in degraded state")
# except Exception as e:
#     logger.critical(f"Critical FCM Service failure: {str(e)}")
#     fcm_service = None


# def send_fcm_notification_wrapper(
#     token: str,
#     task_id: str,
#     task_name: str,
#     manager_name: str
# ) -> bool:
   
#     if not fcm_service or not fcm_service.service_available:
#         logger.error("FCM service unavailable - notification not sent")
#         return False

#     try:
#         success = fcm_service.send_task_notification(
#             token=token,
#             task_id=task_id,
#             task_name=task_name,
#             manager_name=manager_name
#         )
        
#         if success:
#             logger.info(f"Successfully sent notification for task {task_id}")
#         else:
#             logger.error(f"Failed to send notification for task {task_id}")
            
#         return success
        
#     except Exception as e:
#         logger.error(f"Error sending notification: {str(e)}", exc_info=True)
#         return False


