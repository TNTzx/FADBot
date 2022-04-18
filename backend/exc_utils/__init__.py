"""Exception utilities."""


from .custom_exc import \
    CustomExc, \
        ExitFunction, FailedCmd

from .error_info import \
    send_error_warn, send_error_failed_cmd, send_error_fatal, \
    send_error, \
    error_handle, \
        cancel_command, timeout_command
