from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from app.repositories.appointment_repository import IAppointmentRepository
from app.repositories.barbershop_repository import IBarberShopRepository
from app.repositories.customer_repository import ICustomerRepository
from app.repositories.barber_repository import IBarberRepository
from app.repositories.service_repository import IServiceRepository
from app.repositories.barbershop_schedule_repository import IBarberShopScheduleRepository
from app.repositories.barber_schedule_repository import IBarberScheduleRepository
from app.repositories.audit_log_repository import IAuditLogRepository
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate
from app.models.appointment import Appointment as AppointmentModel
from fastapi import HTTPException

from app.core.audit_middleware import get_current_user_info


class AppointmentService:
    def __init__(
        self,
        appointment_repo: IAppointmentRepository,
        barbershop_repo: IBarberShopRepository,
        customer_repo: ICustomerRepository,
        barber_repo: IBarberRepository,
        service_repo: IServiceRepository,
        barbershop_schedule_repo: IBarberShopScheduleRepository = None,
        barber_schedule_repo: IBarberScheduleRepository = None,
        audit_repo: IAuditLogRepository = None,
        request_info: Optional[Dict[str, str]] = None,
    ):
        self.appointment_repo = appointment_repo
        self.barbershop_repo = barbershop_repo
        self.customer_repo = customer_repo
        self.barber_repo = barber_repo
        self.service_repo = service_repo
        self.barbershop_schedule_repo = barbershop_schedule_repo
        self.barber_schedule_repo = barber_schedule_repo
        self.audit_repo = audit_repo
        self.request_info = request_info or {}

    def create_appointment(self, appointment_in: AppointmentCreate) -> AppointmentModel:
        barbershop = self.barbershop_repo.get_by_id(appointment_in.barbershop_id)
        if not barbershop:
            raise HTTPException(status_code=404, detail="Barbershop not found")

        customer = self.customer_repo.get_by_id(appointment_in.customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")

        barber = self.barber_repo.get_by_id(appointment_in.barber_id)
        if not barber:
            raise HTTPException(status_code=404, detail="Barber not found")

        service = self.service_repo.get_by_id(appointment_in.service_id)
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")

        if barber.barbershop_id != appointment_in.barbershop_id:
            raise HTTPException(
                status_code=400, detail="Barber does not belong to this barbershop"
            )

        if service.barbershop_id != appointment_in.barbershop_id:
            raise HTTPException(
                status_code=400, detail="Service does not belong to this barbershop"
            )

        # Validate barber is active
        if not barber.is_active:
            raise HTTPException(status_code=400, detail="Barber is not active")

        # Extract appointment details
        appointment_date = appointment_in.scheduled_date.date()
        appointment_time = appointment_in.scheduled_time
        service_duration = service.duration_minutes

        # Calculate end time
        end_time = self._add_minutes_to_time(appointment_time, service_duration)

        # Validate barber availability
        self._validate_barber_availability(
            barber, appointment_date, appointment_time, end_time
        )

        # Validate barbershop opening hours
        self._validate_barbershop_hours(
            appointment_in.barbershop_id, appointment_date, appointment_time, end_time
        )

        # Validate no conflicting appointments
        self._validate_no_conflicts(
            appointment_in.barber_id,
            appointment_date,
            appointment_time,
            end_time,
        )

        # Validate appointment time constraints
        self._validate_appointment_time_constraints(
            appointment_in.scheduled_date, appointment_time
        )

        # Create the appointment
        appointment = self.appointment_repo.create(appointment_in)

        # Log audit
        self._log_create(
            entity_type="appointment",
            entity_id=appointment.id,
            new_values={
                "barbershop_id": appointment.barbershop_id,
                "customer_id": appointment.customer_id,
                "barber_id": appointment.barber_id,
                "service_id": appointment.service_id,
                "scheduled_date": appointment.scheduled_date.isoformat() if appointment.scheduled_date else None,
                "scheduled_time": appointment.scheduled_time,
                "status": appointment.status,
                "total_price": appointment.total_price,
            },
            description=f"Created appointment for customer {customer.name} with barber {barber.name}",
        )

        return appointment

    def get_appointment(self, appointment_id: int) -> AppointmentModel:
        appointment = self.appointment_repo.get_by_id(appointment_id)
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        # Log view audit
        self._log_view(
            entity_type="appointment",
            entity_id=appointment_id,
        )
        
        return appointment

    def get_barbershop_appointments(
        self, barbershop_id: int, status: str = None
    ) -> List[AppointmentModel]:
        barbershop = self.barbershop_repo.get_by_id(barbershop_id)
        if not barbershop:
            raise HTTPException(status_code=404, detail="Barbershop not found")

        if status:
            return self.appointment_repo.get_by_barbershop_and_status(
                barbershop_id, status
            )
        return self.appointment_repo.get_by_barbershop(barbershop_id)

    def get_customer_appointments(self, customer_id: int) -> List[AppointmentModel]:
        customer = self.customer_repo.get_by_id(customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        return self.appointment_repo.get_by_customer(customer_id)

    def get_barber_appointments(self, barber_id: int) -> List[AppointmentModel]:
        barber = self.barber_repo.get_by_id(barber_id)
        if not barber:
            raise HTTPException(status_code=404, detail="Barber not found")
        return self.appointment_repo.get_by_barber(barber_id)

    def update_appointment(
        self, appointment_id: int, appointment_in: AppointmentUpdate
    ) -> AppointmentModel:
        appointment = self.appointment_repo.get_by_id(appointment_id)
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")

        # Store old values for audit
        old_values = {
            "status": appointment.status,
            "notes": appointment.notes,
        }

        if appointment_in.status:
            valid_statuses = [
                "pending",
                "confirmed",
                "in_progress",
                "completed",
                "cancelled",
                "no_show",
            ]
            if appointment_in.status not in valid_statuses:
                raise HTTPException(status_code=400, detail="Invalid status")

        updated = self.appointment_repo.update(appointment_id, appointment_in)

        # Log audit
        new_values = {
            "status": updated.status,
            "notes": updated.notes,
        }
        self._log_update(
            entity_type="appointment",
            entity_id=appointment_id,
            old_values=old_values,
            new_values=new_values,
            description=f"Updated appointment {appointment_id}",
        )

        return updated

    def delete_appointment(self, appointment_id: int) -> bool:
        appointment = self.appointment_repo.get_by_id(appointment_id)
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")

        # Store old values for audit
        old_values = {
            "barbershop_id": appointment.barbershop_id,
            "customer_id": appointment.customer_id,
            "barber_id": appointment.barber_id,
            "service_id": appointment.service_id,
            "scheduled_date": appointment.scheduled_date.isoformat() if appointment.scheduled_date else None,
            "scheduled_time": appointment.scheduled_time,
            "status": appointment.status,
            "total_price": appointment.total_price,
        }

        result = self.appointment_repo.delete(appointment_id)

        # Log audit
        self._log_delete(
            entity_type="appointment",
            entity_id=appointment_id,
            old_values=old_values,
            description=f"Deleted appointment {appointment_id}",
        )

        return result

    def _add_minutes_to_time(self, time_str: str, minutes: int) -> str:
        """Add minutes to a time string in HH:MM format."""
        time_obj = datetime.strptime(time_str, "%H:%M")
        new_time = time_obj + timedelta(minutes=minutes)
        return new_time.strftime("%H:%M")

    def _validate_barber_availability(
        self, barber, appointment_date, start_time: str, end_time: str
    ):
        """Validate if barber works on the given day and time."""
        day_of_week = appointment_date.strftime("%A").lower()

        # Check if barber works on this day (using working_days field)
        if barber.working_days:
            working_days_lower = [d.lower() for d in barber.working_days]
            if day_of_week not in working_days_lower:
                raise HTTPException(
                    status_code=400,
                    detail=f"Barber does not work on {day_of_week.capitalize()}"
                )

        # Check working hours (using structured working_hours field)
        if barber.working_hours and barber.working_hours.get("enabled"):
            slots = barber.working_hours.get("slots", [])
            time_valid = False
            for slot in slots:
                slot_start = slot.get("start_time")
                slot_end = slot.get("end_time")
                if slot_start and slot_end:
                    if start_time >= slot_start and end_time <= slot_end:
                        time_valid = True
                        break
            if not time_valid:
                raise HTTPException(
                    status_code=400,
                    detail="Appointment time is outside barber's working hours"
                )

        # Also check barber_schedules table if repository is available
        if self.barber_schedule_repo:
            day_number = appointment_date.weekday()  # 0=Monday, 6=Sunday
            schedule = self.barber_schedule_repo.get_by_barber_and_day(
                barber.id, day_number
            )
            if schedule and not schedule.is_available:
                raise HTTPException(
                    status_code=400,
                    detail="Barber is not available at this time"
                )
            if schedule:
                if start_time < schedule.start_time or end_time > schedule.end_time:
                    raise HTTPException(
                        status_code=400,
                        detail="Appointment time is outside barber's schedule"
                    )

    def _validate_barbershop_hours(
        self, barbershop_id: int, appointment_date, start_time: str, end_time: str
    ):
        """Validate if barbershop is open on the given day and time."""
        if not self.barbershop_schedule_repo:
            return  # Skip validation if repository not available

        schedule = self.barbershop_schedule_repo.get_by_barbershop(barbershop_id)
        if not schedule:
            return  # No schedule defined, skip validation

        day_of_week = appointment_date.strftime("%A").lower()
        day_schedule = getattr(schedule, day_of_week, None)

        if not day_schedule:
            raise HTTPException(
                status_code=400,
                detail=f"Barbershop is closed on {day_of_week.capitalize()}"
            )

        if not day_schedule.get("enabled", False):
            raise HTTPException(
                status_code=400,
                detail=f"Barbershop is closed on {day_of_week.capitalize()}"
            )

        shop_start = day_schedule.get("start_time")
        shop_end = day_schedule.get("end_time")

        if not shop_start or not shop_end:
            raise HTTPException(
                status_code=400,
                detail=f"Barbershop schedule not defined for {day_of_week.capitalize()}"
            )

        if start_time < shop_start or end_time > shop_end:
            raise HTTPException(
                status_code=400,
                detail="Appointment time is outside barbershop opening hours"
            )

        # Check if during break time
        break_start = day_schedule.get("break_start")
        break_end = day_schedule.get("break_end")
        if break_start and break_end:
            if not (end_time <= break_start or start_time >= break_end):
                raise HTTPException(
                    status_code=400,
                    detail="Appointment overlaps with barbershop break time"
                )

    def _validate_no_conflicts(
        self, barber_id: int, appointment_date, start_time: str, end_time: str, exclude_id: int = None
    ):
        """Validate no conflicting appointments exist."""
        has_conflict = self.appointment_repo.has_conflicting_appointment(
            barber_id=barber_id,
            date=appointment_date,
            start_time=start_time,
            end_time=end_time,
            exclude_id=exclude_id,
        )
        if has_conflict:
            raise HTTPException(
                status_code=400,
                detail="Barber already has an appointment at this time"
            )

    def _validate_appointment_time_constraints(
        self, scheduled_date: datetime, scheduled_time: str
    ):
        """Validate appointment time constraints.
        
        - Minimum advance notice: 1 hour
        - Maximum advance notice: 30 days
        """
        # Combine date and time into a single datetime
        time_obj = datetime.strptime(scheduled_time, "%H:%M").time()
        appointment_datetime = datetime.combine(scheduled_date.date(), time_obj)
        
        now = datetime.now()
        
        # Check minimum advance notice (1 hour)
        min_advance_time = now + timedelta(hours=1)
        if appointment_datetime < min_advance_time:
            raise HTTPException(
                status_code=400,
                detail="Appointments must be scheduled at least 1 hour in advance"
            )
        
        # Check maximum advance notice (30 days)
        max_advance_time = now + timedelta(days=30)
        if appointment_datetime > max_advance_time:
            raise HTTPException(
                status_code=400,
                detail="Appointments cannot be scheduled more than 30 days in advance"
            )

    # Audit logging methods
    def _log_create(
        self,
        entity_type: str,
        entity_id: int,
        new_values: Dict[str, Any],
        description: Optional[str] = None,
    ):
        """Log CREATE operation."""
        if not self.audit_repo:
            return

        user_id, user_email = get_current_user_info()
        
        from app.schemas.audit_log import AuditLogCreate
        audit_data = AuditLogCreate(
            action="CREATE",
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            user_email=user_email,
            new_values=new_values,
            description=description or f"Created {entity_type} with id {entity_id}",
            **self.request_info,
        )
        self.audit_repo.create(audit_data)

    def _log_update(
        self,
        entity_type: str,
        entity_id: int,
        old_values: Dict[str, Any],
        new_values: Dict[str, Any],
        description: Optional[str] = None,
    ):
        """Log UPDATE operation."""
        if not self.audit_repo:
            return

        user_id, user_email = get_current_user_info()
        changes = self._calculate_changes(old_values, new_values)
        
        from app.schemas.audit_log import AuditLogCreate
        audit_data = AuditLogCreate(
            action="UPDATE",
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            user_email=user_email,
            old_values=old_values,
            new_values=new_values,
            changes=changes,
            description=description or f"Updated {entity_type} with id {entity_id}",
            **self.request_info,
        )
        self.audit_repo.create(audit_data)

    def _log_delete(
        self,
        entity_type: str,
        entity_id: int,
        old_values: Dict[str, Any],
        description: Optional[str] = None,
    ):
        """Log DELETE operation."""
        if not self.audit_repo:
            return

        user_id, user_email = get_current_user_info()
        
        from app.schemas.audit_log import AuditLogCreate
        audit_data = AuditLogCreate(
            action="DELETE",
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            user_email=user_email,
            old_values=old_values,
            description=description or f"Deleted {entity_type} with id {entity_id}",
            **self.request_info,
        )
        self.audit_repo.create(audit_data)

    def _log_view(
        self,
        entity_type: str,
        entity_id: int,
    ):
        """Log VIEW operation."""
        if not self.audit_repo:
            return

        user_id, user_email = get_current_user_info()
        
        from app.schemas.audit_log import AuditLogCreate
        audit_data = AuditLogCreate(
            action="VIEW",
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            user_email=user_email,
            description=f"Viewed {entity_type} with id {entity_id}",
            **self.request_info,
        )
        self.audit_repo.create(audit_data)

    def _calculate_changes(
        self, old_values: Dict[str, Any], new_values: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """Calculate the differences between old and new values."""
        changes = {}
        all_keys = set(old_values.keys()) | set(new_values.keys())
        
        for key in all_keys:
            old_val = old_values.get(key)
            new_val = new_values.get(key)
            
            if old_val != new_val:
                changes[key] = {
                    "old": old_val,
                    "new": new_val,
                }
        
        return changes
