"""Shared helpers so every "delete" view in the project follows the same
GET-shows-confirmation / POST-performs-delete pattern (Priority 1, issue #11:
destructive actions must never happen on a bare GET request)."""
from django.shortcuts import render, redirect


def confirm_and_delete(request, obj, redirect_url_name, cancel_url, message=None, success_message='Deleted successfully.', delete_fn=None):
    """Call from a delete view. On GET, shows a confirmation page. On POST,
    deletes the object and redirects. `obj` may be None (already gone).
    Pass `delete_fn` when the actual delete must happen on a related object
    (e.g. deleting the linked User account instead of the Student row)."""
    from django.contrib import messages as django_messages

    if obj is None:
        django_messages.info(request, 'That item no longer exists.')
        return redirect(redirect_url_name)

    if request.method == 'POST':
        (delete_fn or obj.delete)()
        django_messages.success(request, success_message)
        return redirect(redirect_url_name)

    return render(request, 'generic_confirm_delete.html', {
        'object_label': str(obj),
        'cancel_url': cancel_url,
        'message': message,
    })
