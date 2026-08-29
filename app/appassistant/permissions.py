from rest_framework.permissions import BasePermission


class HasDocumentViewPermission(BasePermission):
    """
    Level-1 Assistant gate: reuse apptransactions.view_document.
    Authorize before any tool or data access.
    """

    message = 'You do not have permission to use JobRhythm Assistant for documents.'

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return user.has_perm('apptransactions.view_document')
