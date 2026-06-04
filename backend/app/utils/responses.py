"""Standardized API JSON responses."""
from flask import jsonify


def api_success(data=None, message: str = "Operation successful", status: int = 200):
    payload = {
        "success": True,
        "message": message,
        "data": data if data is not None else {},
    }
    return jsonify(payload), status


def api_error(message: str, status: int = 400):
    return jsonify({"success": False, "message": message}), status
