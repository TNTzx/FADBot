"""Contains stuff for responding to a message or view interaction."""


from .detection import \
    wait_for_message, wait_for_message_view, wait_for_view, \
    DetectionOutputTypes, \
    send_error

from .detection_checks import check_interaction, check_message
