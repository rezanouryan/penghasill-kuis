import os

# Application settings
APP_NAME = "DB Quiz"
APP_SYSTEM_ERROR_SUBJECT_LINE = APP_NAME + " system error"

# Flask settings
CSRF_ENABLED = True

# Flask-SQLAlchemy settings
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Flask-User settings
USER_APP_NAME = APP_NAME
USER_ENABLE_CHANGE_PASSWORD = True  # Allow users to change their password
USER_ENABLE_CHANGE_USERNAME = False  # Allow users to change their username
USER_ENABLE_CONFIRM_EMAIL = True  # Force users to confirm their email
USER_ENABLE_FORGOT_PASSWORD = True  # Allow users to reset their passwords
USER_ENABLE_EMAIL = False  # Register with Email
USER_ENABLE_REGISTRATION = True  # Allow new users to register
USER_REQUIRE_RETYPE_PASSWORD = True  # Prompt for `retype password` in:
USER_ENABLE_USERNAME = True  # Register and Login with username
USER_UNAUTHENTICATED_ENDPOINT  = 'auth_bp.login'
USER_UNAUTHORIZED_ENDPOINT  = 'auth_bp.login'              
# USER_AFTER_LOGIN_ENDPOINT = 'main.member_page'
USER_AFTER_LOGOUT_ENDPOINT = 'auth_bp.login'



USER_CHANGE_PASSWORD_URL      = '/auth/change-password'
USER_CHANGE_USERNAME_URL      = '/auth/change-username'
USER_CONFIRM_EMAIL_URL        = '/auth/confirm-email/<token>'
USER_EMAIL_ACTION_URL         = '/auth/email/<id>/<action>'     # v0.5.1 and up
USER_FORGOT_PASSWORD_URL      = '/auth/forgot-password'
USER_INVITE_URL               = '/auth/invite'                  # v0.6.2 and up
USER_LOGIN_URL                = '/auth/login'
USER_LOGOUT_URL               = '/auth/logout'
USER_MANAGE_EMAILS_URL        = '/auth/manage-emails'
USER_REGISTER_URL             = '/auth/signup'
USER_RESEND_CONFIRM_EMAIL_URL = '/auth/resend-confirm-email'    # v0.5.0 and up
USER_RESET_PASSWORD_URL       = '/auth/reset-password/<token>'