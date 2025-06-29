#!/usr/bin/env python3
"""
ERP API MCP Server
Provides tools for interacting with Laravel Sanctum-protected ERP APIs
"""

import asyncio
import json
import httpx
from typing import Any, Dict, List, Optional
from datetime import datetime, date
from mcp.server.fastmcp import FastMCP

# Initialize the server
server = FastMCP("erp-api-server")

# API Configuration
API_CONFIG = {
    "base_url": "http://localhost:8000/api",  # Adjust this to your Laravel API URL
    "auth_endpoint": "/auth/login",  # Adjust if your login endpoint is different
    "token": None,
    "headers": {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
}

class ERPAPIClient:
    def __init__(self):
        self.base_url = API_CONFIG["base_url"]
        self.auth_endpoint = API_CONFIG["auth_endpoint"]
        self.token = None
        self.headers = API_CONFIG["headers"].copy()
    
    async def authenticate(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate with Laravel Sanctum"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}{self.auth_endpoint}",
                    json={"email": email, "password": password},
                    headers=self.headers,
                    timeout=30.0
                )
                
                response_data = response.json()
                
                # Handle different response formats based on your Laravel setup
                if response.status_code == 200:
                    # Check if the response has a success flag
                    if response_data.get("success", False):
                        # Extract token from response
                        token = response_data.get("data", {}).get("token") or \
                               response_data.get("token") or \
                               response_data.get("access_token")
                        
                        if token:
                            self.token = token
                            self.headers["Authorization"] = f"Bearer {token}"
                            return {
                                "success": True,
                                "message": "Authentication successful",
                                "user": response_data.get("data", {}).get("user", {})
                            }
                        else:
                            return {
                                "success": False,
                                "message": "No token found in response",
                                "response": response_data
                            }
                    else:
                        # Handle error response
                        error_message = response_data.get("message", "Authentication failed")
                        return {
                            "success": False,
                            "message": error_message,
                            "response": response_data
                        }
                else:
                    # Handle non-200 status codes
                    error_message = response_data.get("message", f"HTTP {response.status_code}")
                    return {
                        "success": False,
                        "message": error_message,
                        "response": response_data
                    }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Authentication error: {str(e)}",
                "response": None
            }
    
    async def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make authenticated API request"""
        if not self.token:
            return {"error": "Not authenticated. Please authenticate first."}
        
        try:
            async with httpx.AsyncClient() as client:
                url = f"{self.base_url}{endpoint}"
                
                if method.upper() == "GET":
                    response = await client.get(url, headers=self.headers, timeout=30.0)
                elif method.upper() == "POST":
                    response = await client.post(url, json=data, headers=self.headers, timeout=30.0)
                elif method.upper() == "PUT":
                    response = await client.put(url, json=data, headers=self.headers, timeout=30.0)
                elif method.upper() == "DELETE":
                    response = await client.delete(url, headers=self.headers, timeout=30.0)
                else:
                    return {"error": f"Unsupported HTTP method: {method}"}
                
                response_data = response.json()
                
                if response.status_code in [200, 201]:
                    return response_data
                else:
                    return {
                        "error": f"API request failed with status {response.status_code}",
                        "message": response_data.get("message", "Unknown error"),
                        "response": response_data
                    }
                    
        except Exception as e:
            return {"error": f"Request error: {str(e)}"}

# Global API client instance
api_client = ERPAPIClient()

@server.tool()
async def authenticate_user(email: str, password: str) -> str:
    """Authenticate with the ERP API using email and password
    
    Args:
        email: User email
        password: User password
    
    Returns: Authentication status with detailed response
    """
    result = await api_client.authenticate(email, password)
    
    if result["success"]:
        user_info = result.get("user", {})
        user_name = user_info.get("name", "User")
        company_name = user_info.get("company", {}).get("name", "Unknown Company")
        
        return f"""Authentication successful! 
Welcome, {user_name} from {company_name}.
You can now use other API tools to interact with the ERP system."""
    else:
        error_msg = result.get("message", "Authentication failed")
        return f"Authentication failed: {error_msg}"

@server.tool()
async def get_employees(page: Optional[int] = 1, per_page: Optional[int] = 15) -> str:
    """Get list of employees
    
    Args:
        page: Page number (default: 1)
        per_page: Items per page (default: 15)
    
    Returns: List of employees
    """
    endpoint = f"/humanresource/employees?page={page}&per_page={per_page}"
    result = await api_client.make_request("GET", endpoint)
    return json.dumps(result, indent=2)

@server.tool()
async def get_employee_by_id(employee_id: int) -> str:
    """Get employee by ID
    
    Args:
        employee_id: Employee ID
    
    Returns: Employee details
    """
    endpoint = f"/humanresource/employees/{employee_id}"
    result = await api_client.make_request("GET", endpoint)
    return json.dumps(result, indent=2)

@server.tool()
async def get_employee_summary() -> str:
    """Get employee summary statistics
    
    Returns: Employee summary data
    """
    endpoint = "/humanresource/employees/summary"
    result = await api_client.make_request("GET", endpoint)
    return json.dumps(result, indent=2)

@server.tool()
async def get_departments(page: Optional[int] = 1, per_page: Optional[int] = 15) -> str:
    """Get list of departments
    
    Args:
        page: Page number (default: 1)
        per_page: Items per page (default: 15)
    
    Returns: List of departments
    """
    endpoint = f"/humanresource/departments?page={page}&per_page={per_page}"
    result = await api_client.make_request("GET", endpoint)
    return json.dumps(result, indent=2)

@server.tool()
async def get_department_by_id(department_id: int) -> str:
    """Get department by ID
    
    Args:
        department_id: Department ID
    
    Returns: Department details
    """
    endpoint = f"/humanresource/departments/{department_id}"
    result = await api_client.make_request("GET", endpoint)
    return json.dumps(result, indent=2)

@server.tool()
async def get_branches(page: Optional[int] = 1, per_page: Optional[int] = 15) -> str:
    """Get list of branches
    
    Args:
        page: Page number (default: 1)
        per_page: Items per page (default: 15)
    
    Returns: List of branches
    """
    endpoint = f"/humanresource/branches?page={page}&per_page={per_page}"
    result = await api_client.make_request("GET", endpoint)
    return json.dumps(result, indent=2)

@server.tool()
async def get_branch_by_id(branch_id: int) -> str:
    """Get branch by ID
    
    Args:
        branch_id: Branch ID
    
    Returns: Branch details
    """
    endpoint = f"/humanresource/branches/{branch_id}"
    result = await api_client.make_request("GET", endpoint)
    return json.dumps(result, indent=2)

@server.tool()
async def get_attendances(page: Optional[int] = 1, per_page: Optional[int] = 15) -> str:
    """Get list of attendance records
    
    Args:
        page: Page number (default: 1)
        per_page: Items per page (default: 15)
    
    Returns: List of attendance records
    """
    endpoint = f"/humanresource/attendances?page={page}&per_page={per_page}"
    result = await api_client.make_request("GET", endpoint)
    return json.dumps(result, indent=2)

@server.tool()
async def get_attendance_by_employee(employee_id: int) -> str:
    """Get attendance records for a specific employee
    
    Args:
        employee_id: Employee ID
    
    Returns: Employee attendance records
    """
    endpoint = f"/humanresource/attendances/employee/{employee_id}"
    result = await api_client.make_request("GET", endpoint)
    return json.dumps(result, indent=2)

@server.tool()
async def get_attendance_summary() -> str:
    """Get attendance summary statistics
    
    Returns: Attendance summary data
    """
    endpoint = "/humanresource/attendances/summary"
    result = await api_client.make_request("GET", endpoint)
    return json.dumps(result, indent=2)

@server.tool()
async def check_in_employee(employee_id: int, location: Optional[str] = None) -> str:
    """Check in an employee
    
    Args:
        employee_id: Employee ID
        location: Optional location data
    
    Returns: Check-in result
    """
    data = {"employee_id": employee_id}
    if location:
        data["location"] = location
    
    endpoint = "/humanresource/attendances/check-in"
    result = await api_client.make_request("POST", endpoint, data)
    return json.dumps(result, indent=2)

@server.tool()
async def check_out_employee(employee_id: int) -> str:
    """Check out an employee
    
    Args:
        employee_id: Employee ID
    
    Returns: Check-out result
    """
    data = {"employee_id": employee_id}
    endpoint = "/humanresource/attendances/check-out"
    result = await api_client.make_request("POST", endpoint, data)
    return json.dumps(result, indent=2)

@server.tool()
async def get_performance_cycles(page: Optional[int] = 1, per_page: Optional[int] = 15) -> str:
    """Get list of performance cycles
    
    Args:
        page: Page number (default: 1)
        per_page: Items per page (default: 15)
    
    Returns: List of performance cycles
    """
    endpoint = f"/humanresource/performance-cycles?page={page}&per_page={per_page}"
    result = await api_client.make_request("GET", endpoint)
    return json.dumps(result, indent=2)

@server.tool()
async def get_current_active_cycle() -> str:
    """Get current active performance cycle
    
    Returns: Current active cycle details
    """
    endpoint = "/humanresource/performance-cycles/current-active"
    result = await api_client.make_request("GET", endpoint)
    return json.dumps(result, indent=2)

@server.tool()
async def get_employee_performances(page: Optional[int] = 1, per_page: Optional[int] = 15) -> str:
    """Get list of employee performances
    
    Args:
        page: Page number (default: 1)
        per_page: Items per page (default: 15)
    
    Returns: List of employee performances
    """
    endpoint = f"/humanresource/employee-performances?page={page}&per_page={per_page}"
    result = await api_client.make_request("GET", endpoint)
    return json.dumps(result, indent=2)

@server.tool()
async def get_employee_performance_by_id(performance_id: int) -> str:
    """Get employee performance by ID
    
    Args:
        performance_id: Performance ID
    
    Returns: Employee performance details
    """
    endpoint = f"/humanresource/employee-performances/{performance_id}"
    result = await api_client.make_request("GET", endpoint)
    return json.dumps(result, indent=2)

@server.tool()
async def get_goal_trackings(page: Optional[int] = 1, per_page: Optional[int] = 15) -> str:
    """Get list of goal trackings
    
    Args:
        page: Page number (default: 1)
        per_page: Items per page (default: 15)
    
    Returns: List of goal trackings
    """
    endpoint = f"/humanresource/goal-trackings?page={page}&per_page={per_page}"
    result = await api_client.make_request("GET", endpoint)
    return json.dumps(result, indent=2)

@server.tool()
async def get_goal_tracking_by_id(goal_id: int) -> str:
    """Get goal tracking by ID
    
    Args:
        goal_id: Goal tracking ID
    
    Returns: Goal tracking details
    """
    endpoint = f"/humanresource/goal-trackings/{goal_id}"
    result = await api_client.make_request("GET", endpoint)
    return json.dumps(result, indent=2)

@server.tool()
async def get_appraisals(page: Optional[int] = 1, per_page: Optional[int] = 15) -> str:
    """Get list of appraisals
    
    Args:
        page: Page number (default: 1)
        per_page: Items per page (default: 15)
    
    Returns: List of appraisals
    """
    endpoint = f"/humanresource/appraisals?page={page}&per_page={per_page}"
    result = await api_client.make_request("GET", endpoint)
    return json.dumps(result, indent=2)

@server.tool()
async def get_appraisal_by_id(appraisal_id: int) -> str:
    """Get appraisal by ID
    
    Args:
        appraisal_id: Appraisal ID
    
    Returns: Appraisal details
    """
    endpoint = f"/humanresource/appraisals/{appraisal_id}"
    result = await api_client.make_request("GET", endpoint)
    return json.dumps(result, indent=2)

@server.tool()
async def get_kpi_management(page: Optional[int] = 1, per_page: Optional[int] = 15) -> str:
    """Get list of KPI management records
    
    Args:
        page: Page number (default: 1)
        per_page: Items per page (default: 15)
    
    Returns: List of KPI management records
    """
    endpoint = f"/humanresource/kpi-management?page={page}&per_page={per_page}"
    result = await api_client.make_request("GET", endpoint)
    return json.dumps(result, indent=2)

@server.tool()
async def get_kpi_by_department(department_id: int) -> str:
    """Get KPIs by department
    
    Args:
        department_id: Department ID
    
    Returns: Department KPIs
    """
    endpoint = f"/humanresource/kpi-management/department/{department_id}"
    result = await api_client.make_request("GET", endpoint)
    return json.dumps(result, indent=2)

@server.tool()
async def get_lookup_configs(category: Optional[str] = None, page: Optional[int] = 1, per_page: Optional[int] = 15) -> str:
    """Get lookup configurations
    
    Args:
        category: Category filter (optional)
        page: Page number (default: 1)
        per_page: Items per page (default: 15)
    
    Returns: List of lookup configurations
    """
    if category:
        endpoint = f"/humanresource/lookup-configs/category/{category}?page={page}&per_page={per_page}"
    else:
        endpoint = f"/humanresource/lookup-configs?page={page}&per_page={per_page}"
    
    result = await api_client.make_request("GET", endpoint)
    return json.dumps(result, indent=2)

@server.tool()
async def get_status_configs(page: Optional[int] = 1, per_page: Optional[int] = 15) -> str:
    """Get status configurations
    
    Args:
        page: Page number (default: 1)
        per_page: Items per page (default: 15)
    
    Returns: List of status configurations
    """
    endpoint = f"/humanresource/status-configs?page={page}&per_page={per_page}"
    result = await api_client.make_request("GET", endpoint)
    return json.dumps(result, indent=2)

@server.tool()
async def create_employee(employee_data: str) -> str:
    """Create a new employee
    
    Args:
        employee_data: JSON string containing employee data
    
    Returns: Created employee details
    """
    try:
        data = json.loads(employee_data)
        endpoint = "/humanresource/employees"
        result = await api_client.make_request("POST", endpoint, data)
        return json.dumps(result, indent=2)
    except json.JSONDecodeError:
        return "Error: Invalid JSON format for employee_data"

@server.tool()
async def update_employee(employee_id: int, employee_data: str) -> str:
    """Update an existing employee
    
    Args:
        employee_id: Employee ID
        employee_data: JSON string containing updated employee data
    
    Returns: Updated employee details
    """
    try:
        data = json.loads(employee_data)
        endpoint = f"/humanresource/employees/{employee_id}"
        result = await api_client.make_request("PUT", endpoint, data)
        return json.dumps(result, indent=2)
    except json.JSONDecodeError:
        return "Error: Invalid JSON format for employee_data"

@server.tool()
async def delete_employee(employee_id: int) -> str:
    """Delete an employee
    
    Args:
        employee_id: Employee ID
    
    Returns: Deletion result
    """
    endpoint = f"/humanresource/employees/{employee_id}"
    result = await api_client.make_request("DELETE", endpoint)
    return json.dumps(result, indent=2)

@server.tool()
async def get_employee_bank_details(employee_id: int) -> str:
    """Get employee bank details
    
    Args:
        employee_id: Employee ID
    
    Returns: Employee bank details
    """
    endpoint = f"/humanresource/employees/{employee_id}/bank-details"
    result = await api_client.make_request("GET", endpoint)
    return json.dumps(result, indent=2)

@server.tool()
async def get_employee_company_details(employee_id: int) -> str:
    """Get employee company details
    
    Args:
        employee_id: Employee ID
    
    Returns: Employee company details
    """
    endpoint = f"/humanresource/employees/{employee_id}/company-details"
    result = await api_client.make_request("GET", endpoint)
    return json.dumps(result, indent=2)

if __name__ == "__main__":
    asyncio.run(server.run()) 