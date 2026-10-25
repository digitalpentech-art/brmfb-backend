from django.core.exceptions import ValidationError
from .models import SupportTicket
from apps.audit.services import AuditService


class SupportService:
    @staticmethod
    def create_ticket(customer, category, subject, description, user=None, ip_address=None):
        ticket = SupportTicket.objects.create(
            customer=customer,
            category=category,
            subject=subject,
            description=description,
            status='OPEN'
        )
        AuditService.log_event(
            user=user,
            event_type="SUPPORT_TICKET_CREATED",
            description=f"Support ticket {ticket.id} created for customer {customer.customer_number}.",
            ip_address=ip_address,
            metadata={"ticket_id": str(ticket.id), "category": category}
        )
        return ticket

    @staticmethod
    def update_ticket_status(ticket_id, new_status, staff_user=None):
        try:
            ticket = SupportTicket.objects.get(id=ticket_id)
        except SupportTicket.DoesNotExist:
            raise ValidationError("Support ticket not found.")

        ticket.status = new_status
        if staff_user and staff_user.is_staff:
            ticket.assigned_staff = staff_user
        ticket.save()

        AuditService.log_event(
            user=staff_user,
            event_type="SUPPORT_TICKET_UPDATED",
            description=f"Support ticket {ticket.id} status updated to {new_status}.",
            metadata={"ticket_id": str(ticket.id), "status": new_status}
        )
        return ticket
