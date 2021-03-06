"""Stores approve statuses."""


class ApprovalStatus():
    """Base class for approve statuses."""
    @classmethod
    def get_message_confirm(cls, req_type: str, reason: str):
        """Gets the string for asking to confirm the approval."""

    @classmethod
    def get_message_processing(cls, req_type: str):
        """Gets the string for processing approval."""

    @classmethod
    def get_message_complete(cls, req_type: str, reason: str):
        """Gets the string for completing the approval process."""

    @classmethod
    def get_message_complete_dump_logs(cls, req_type: str, reason: str):
        """Gets the string for completing the approval process. Sent in dump logs."""

    @classmethod
    def get_message_complete_dm(cls, req_type: str, reason: str):
        """Gets the string for completing the approval process. Sent in DMs."""


class Approve(ApprovalStatus):
    """Approved request."""
    @classmethod
    def get_message_confirm(cls, req_type: str, reason: str):
        return f"Are you sure you want to approve this {req_type} request?\n"

    @classmethod
    def get_message_processing(cls, req_type: str):
        return f"Approving {req_type} request..."

    @classmethod
    def get_message_complete(cls, req_type: str, reason: str):
        return f"{req_type.capitalize()} request approved!\n"

    @classmethod
    def get_message_complete_dump_logs(cls, req_type: str, reason: str):
        return f"This {req_type} request has been approved!\n"

    @classmethod
    def get_message_complete_dm(cls, req_type: str, reason: str):
        return f"Your {req_type} request has been approved!\n"


class Decline(ApprovalStatus):
    """Declined request."""
    @classmethod
    def get_message_confirm(cls, req_type: str, reason: str):
        return (
            f"Are you sure you want to decline this {req_type} request with the following reason:\n"
            f"`{reason}`?\n"
        )

    @classmethod
    def get_message_processing(cls, req_type: str):
        return f"Declining {req_type} request..."

    @classmethod
    def get_message_complete(cls, req_type: str, reason: str):
        return (
            f"{req_type.capitalize()} request declined for the following reason:\n"
            f"`{reason}`\n"
        )

    @classmethod
    def get_message_complete_dump_logs(cls, req_type: str, reason: str):
        return (
            f"This {req_type} request has been declined for the following reason:\n"
            f"`{reason}`\n"
        )

    @classmethod
    def get_message_complete_dm(cls, req_type: str, reason: str):
        return (
            f"Your {req_type} request has been declined for the following reason:\n"
            f"`{reason}`\n"
        )
