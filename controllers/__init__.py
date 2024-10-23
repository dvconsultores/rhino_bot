from .user_controller import user_bp
from .schedule_controller import schedule_bp

# Add all blueprints to this list
all_blueprints = [user_bp, schedule_bp]