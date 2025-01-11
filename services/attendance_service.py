from models.attendance import Attendance
from models.coaches import Coach
from models.locations import Locations
from models.users import User
from db import db

class AttendanceService:

    @staticmethod
    def create_attendance(data):
        """
        Create a new attendance record.
        
        :param data: Dictionary containing 'coach_id', 'location_id', 'user_id', and 'date'.
        :return: The created Attendance object or None if an error occurs.
        """
        try:
            # Extract data fields
            coach_id = data.get('coach_id')
            location_id = data.get('location_id')
            user_id = data.get('user_id')
            date = data.get('date')

            # Ensure related entities exist
            if not Coach.query.get(coach_id):
                return {"error": "Coach not found"}, 404
            if not Location.query.get(location_id):
                return {"error": "Location not found"}, 404
            if not User.query.get(user_id):
                return {"error": "User not found"}, 404

            # Create a new Attendance record
            new_attendance = Attendance(
                coach_id=coach_id,
                location_id=location_id,
                user_id=user_id,
                date=date
            )
            db.session.add(new_attendance)
            db.session.commit()
            return new_attendance
        except Exception as e:
            print(f"Error creating attendance: {e}")
            db.session.rollback()
            return None

    @staticmethod
    def get_attendance_by_id(attendance_id):
        """
        Retrieve an attendance record by its ID.

        :param attendance_id: The ID of the attendance record.
        :return: The Attendance object or None if not found.
        """
        return Attendance.query.get(attendance_id)

    @staticmethod
    def list_all_attendances():
        """
        List all attendance records.

        :return: A list of all Attendance objects.
        """
        return Attendance.query.all()

    @staticmethod
    def update_attendance(attendance_id, data):
        """
        Update an existing attendance record.

        :param attendance_id: The ID of the attendance record to update.
        :param data: Dictionary containing fields to update.
        :return: The updated Attendance object or None if not found.
        """
        try:
            attendance = Attendance.query.get(attendance_id)
            if not attendance:
                return {"error": "Attendance not found"}, 404

            # Update fields
            for key, value in data.items():
                if hasattr(attendance, key):
                    setattr(attendance, key, value)

            db.session.commit()
            return attendance
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

    @staticmethod
    def delete_attendance(attendance_id):
        """
        Delete an attendance record by its ID.

        :param attendance_id: The ID of the attendance record to delete.
        :return: The deleted Attendance object or None if not found.
        """
        try:
            attendance = Attendance.query.get(attendance_id)
            if not attendance:
                return {"error": "Attendance not found"}, 404

            db.session.delete(attendance)
            db.session.commit()
            return attendance
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500
