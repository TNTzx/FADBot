"""Exception utilities."""


from .custom_exc import \
    CustomExc, \
        ExitFunction, FailedCmd

from .cooldown_handle import reset_cooldown

from .error_info import \
    ErrorInfo, \
        SendFailedCmd, SendWarn, \
    ErrorSendInfo, \
    send_error, \
    error_handle, \
        cancel_command, timeout_command
