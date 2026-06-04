"""Register API blueprints."""


def register_blueprints(flask_app):
    from app.routes.admin_routes import admin_bp
    from app.routes.auth_routes import auth_bp
    from app.routes.health_routes import health_bp
    from app.routes.monitoring_routes import monitoring_bp
    from app.routes.notification_routes import notification_bp
    from app.routes.report_routes import report_bp
    from app.routes.scan_routes import scan_bp

    flask_app.register_blueprint(health_bp)
    flask_app.register_blueprint(auth_bp)
    flask_app.register_blueprint(scan_bp)
    flask_app.register_blueprint(report_bp)
    flask_app.register_blueprint(monitoring_bp)
    flask_app.register_blueprint(notification_bp)
    flask_app.register_blueprint(admin_bp)
