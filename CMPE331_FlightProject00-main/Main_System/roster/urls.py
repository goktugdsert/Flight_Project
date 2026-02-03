from django.urls import path
from .views import FlightListView, RosterCreateView, AvailableCrewView, PilotListView, CabinCrewListView, AssignSeatView, UpdatePilotRosterView, SaveRosterDatabaseView, SavedRostersListView, OpenNoSQLRosterView, GetRosterView, DashboardStatsView, DeleteNoSQLRosterView

urlpatterns = [
    path('flights/', FlightListView.as_view(), name='flight-list'),
    path('create-roster/', RosterCreateView.as_view(), name='create-roster'),
    path('available-crew/', AvailableCrewView.as_view(), name='available-crew'),
    path('pilots/', PilotListView.as_view(), name='pilot-list'),
    path('roster/create/', RosterCreateView.as_view(), name='roster-create'),
    path('attendants/', CabinCrewListView.as_view(), name='attendant-list'),
    path('roster/assign-seat/', AssignSeatView.as_view(), name='assign-seat'),
    path('roster/update-pilots/', UpdatePilotRosterView.as_view(), name='update-pilots'),
    path('roster/save-selection/', SaveRosterDatabaseView.as_view(), name='save-roster-selection'),
    path('roster/list-saved/', SavedRostersListView.as_view(), name='list-saved-rosters'),
    path('roster/open-nosql/<str:filename>/', OpenNoSQLRosterView.as_view(), name='open-nosql-roster'),
    path('roster/detail/<str:flight_number>/', GetRosterView.as_view(), name='get-roster-detail'),
    path('roster/dashboard-stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('roster/delete-nosql/<str:filename>/', DeleteNoSQLRosterView.as_view(), name='delete-nosql-roster'),
]
