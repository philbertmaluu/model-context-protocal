#!/usr/bin/env python3
"""
Configuration file for ERP API Server
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
API_CONFIG = {
    "base_url": os.getenv("ERP_API_BASE_URL", "http://localhost:8000/api"),
    "auth_endpoint": os.getenv("ERP_AUTH_ENDPOINT", "/auth/login"),
    "default_email": os.getenv("ERP_DEFAULT_EMAIL", ""),
    "default_password": os.getenv("ERP_DEFAULT_PASSWORD", ""),
    "timeout": int(os.getenv("ERP_API_TIMEOUT", "30")),
    "max_retries": int(os.getenv("ERP_MAX_RETRIES", "3")),
}

# Default headers for API requests
DEFAULT_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "ERP-MCP-Client/1.0",
}

# Common API endpoints
ENDPOINTS = {
    # Authentication
    "login": "/auth/login",
    "logout": "/auth/logout",
    "refresh": "/auth/refresh",
    
    # Human Resources
    "employees": "/humanresource/employees",
    "departments": "/humanresource/departments",
    "branches": "/humanresource/branches",
    "attendances": "/humanresource/attendances",
    "performance_cycles": "/humanresource/performance-cycles",
    "employee_performances": "/humanresource/employee-performances",
    "goal_trackings": "/humanresource/goal-trackings",
    "appraisals": "/humanresource/appraisals",
    "kpi_management": "/humanresource/kpi-management",
    "lookup_configs": "/humanresource/lookup-configs",
    "status_configs": "/humanresource/status-configs",
    
    # Employee specific endpoints
    "employee_bank_details": "/humanresource/employees/{id}/bank-details",
    "employee_company_details": "/humanresource/employees/{id}/company-details",
    
    # Attendance specific endpoints
    "check_in": "/humanresource/attendances/check-in",
    "check_out": "/humanresource/attendances/check-out",
    "attendance_summary": "/humanresource/attendances/summary",
    "employee_attendance": "/humanresource/attendances/employee/{id}",
    
    # Performance specific endpoints
    "current_active_cycle": "/humanresource/performance-cycles/current-active",
}

# Response status codes
STATUS_CODES = {
    "success": [200, 201],
    "client_error": [400, 401, 403, 404, 422],
    "server_error": [500, 502, 503, 504],
}

# Common error messages
ERROR_MESSAGES = {
    "not_authenticated": "Not authenticated. Please authenticate first.",
    "invalid_credentials": "Invalid email or password.",
    "token_expired": "Authentication token has expired.",
    "permission_denied": "You don't have permission to access this resource.",
    "resource_not_found": "The requested resource was not found.",
    "validation_error": "Validation error occurred.",
    "server_error": "Internal server error occurred.",
    "network_error": "Network error occurred. Please check your connection.",
}

# Pagination defaults
PAGINATION = {
    "default_page": 1,
    "default_per_page": 15,
    "max_per_page": 100,
}

# Cache settings (for future implementation)
CACHE = {
    "enabled": os.getenv("ERP_CACHE_ENABLED", "false").lower() == "true",
    "ttl": int(os.getenv("ERP_CACHE_TTL", "300")),  # 5 minutes
    "max_size": int(os.getenv("ERP_CACHE_MAX_SIZE", "1000")),
} 