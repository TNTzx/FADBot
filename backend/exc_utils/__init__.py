"""Exception utilities."""


from .custom_exc import \
    CustomExc, \
        ExitFunction, FailedCmd

from .cooldown_handle import reset_cooldown

from .error_info import \
    ErrorPlace, \
    ErrorSender, \
        SendFailed, SendFailedCmd, SendWarn, \
        ErrorSenderPredetermined, \
            SendCancel, SendTimeout
