from .user_controller import user_bp
from .schedule_controller import schedule_bp
from .plan_controller import plan_bp
from .payment_method_controller import payment_method_bp
from .payment_controller import payment_bp
from .location_controller import location_bp
from .location_user_controller import location_user_bp
from .language_controller import language_bp

# Add all blueprints to this list
all_blueprints = [user_bp, schedule_bp, plan_bp, payment_method_bp, payment_bp, location_bp, location_user_bp, language_bp]