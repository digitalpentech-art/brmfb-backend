from django.urls import path
from .views import SupportTicketListCreateView, SupportTicketStatusUpdateView

urlpatterns = [
    path('tickets/', SupportTicketListCreateView.as_view(), name='support-ticket-list-create'),
    path('tickets/<uuid:ticket_id>/status/', SupportTicketStatusUpdateView.as_view(), name='support-ticket-status-update'),
]
