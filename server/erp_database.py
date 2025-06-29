#!/usr/bin/env python3
"""
ERP Database MCP Server
Provides tools for interacting with the ERP-X-DB MySQL database
"""

import asyncio
import json
import mysql.connector
from typing import Any, Dict, List, Optional
from datetime import datetime, date
from mcp.server.fastmcp import FastMCP

# Initialize the server
server = FastMCP("erp-database-server")

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "ERP-X-DB",
    "port": 3306,
    "autocommit": True,
}

def get_db_connection():
    """Get database connection"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as e:
        raise Exception(f"Error connecting to the database: {e}")

@server.tool()
async def get_employee_info(employee_id: Optional[int] = None, email: Optional[str] = None) -> str:
    """Get employee information by ID or email
    
    Args:
        employee_id: Employee ID (optional)
        email: Employee email (optional)
    
    Returns: Employee information in JSON format
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        if employee_id:
            query = """
                SELECT e.*, ecd.employee_number, ecd.branch_id, ecd.department_id, 
                       ecd.designation_id, ecd.company_join_date, ecd.status,
                       b.name as branch_name, d.name as department_name, des.name as designation_name
                FROM employees e
                LEFT JOIN employee_company_details ecd ON e.id = ecd.employee_id
                LEFT JOIN branches b ON ecd.branch_id = b.id
                LEFT JOIN department d ON ecd.department_id = d.id
                LEFT JOIN designation des ON ecd.designation_id = des.id
                WHERE e.id = %s AND e.deleted_at IS NULL
            """
            cursor.execute(query, (employee_id,))
        elif email:
            query = """
                SELECT e.*, ecd.employee_number, ecd.branch_id, ecd.department_id, 
                       ecd.designation_id, ecd.company_join_date, ecd.status,
                       b.name as branch_name, d.name as department_name, des.name as designation_name
                FROM employees e
                LEFT JOIN employee_company_details ecd ON e.id = ecd.employee_id
                LEFT JOIN branch b ON ecd.branch_id = b.id
                LEFT JOIN department d ON ecd.department_id = d.id
                LEFT JOIN designation des ON ecd.designation_id = des.id
                WHERE e.email = %s AND e.deleted_at IS NULL
            """
            cursor.execute(query, (email,))
        else:
            return "Please provide either employee_id or email"
        
        employee = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if employee:
            # Convert datetime objects to strings for JSON serialization
            for key, value in employee.items():
                if isinstance(value, (datetime, date)):
                    employee[key] = value.isoformat()
            
            return json.dumps(employee, indent=2, default=str)
        else:
            return "Employee not found"
            
    except Exception as e:
        return f"Error: {str(e)}"

@server.tool()
async def search_employees(name: Optional[str] = None, department: Optional[str] = None, status: Optional[str] = None) -> str:
    """Search employees by name, department, or status
    
    Args:
        name: Employee name (partial match)
        department: Department name
        status: Employee status
    
    Returns: List of matching employees
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT e.id, e.name, e.email, e.phone, ecd.employee_number, 
                   ecd.status, d.name as department_name, des.name as designation_name
            FROM employees e
            LEFT JOIN employee_company_details ecd ON e.id = ecd.employee_id
            LEFT JOIN department d ON ecd.department_id = d.id
            LEFT JOIN designation des ON ecd.designation_id = des.id
            WHERE e.deleted_at IS NULL
        """
        params = []
        
        if name:
            query += " AND e.name LIKE %s"
            params.append(f"%{name}%")
        
        if department:
            query += " AND d.name LIKE %s"
            params.append(f"%{department}%")
        
        if status:
            query += " AND ecd.status = %s"
            params.append(status)
        
        query += " ORDER BY e.name LIMIT 50"
        
        cursor.execute(query, params)
        employees = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if employees:
            # Convert datetime objects to strings
            for employee in employees:
                for key, value in employee.items():
                    if isinstance(value, (datetime, date)):
                        employee[key] = value.isoformat()
            
            return json.dumps(employees, indent=2, default=str)
        else:
            return "No employees found matching the criteria"
            
    except Exception as e:
        return f"Error: {str(e)}"

@server.tool()
async def get_company_info(company_id: Optional[int] = None) -> str:
    """Get company information
    
    Args:
        company_id: Company ID (optional, returns all companies if not provided)
    
    Returns: Company information
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        if company_id:
            query = "SELECT * FROM companies WHERE id = %s AND deleted_at IS NULL"
            cursor.execute(query, (company_id,))
            company = cursor.fetchone()
            
            if company:
                for key, value in company.items():
                    if isinstance(value, (datetime, date)):
                        company[key] = value.isoformat()
                return json.dumps(company, indent=2, default=str)
            else:
                return "Company not found"
        else:
            query = "SELECT id, name, legal_name, industry, type, size, founded_year, email, phone FROM companies WHERE deleted_at IS NULL"
            cursor.execute(query)
            companies = cursor.fetchall()
            
            for company in companies:
                for key, value in company.items():
                    if isinstance(value, (datetime, date)):
                        company[key] = value.isoformat()
            
            return json.dumps(companies, indent=2, default=str)
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        return f"Error: {str(e)}"

@server.tool()
async def get_department_employees(department_id: int) -> str:
    """Get all employees in a specific department
    
    Args:
        department_id: Department ID
    
    Returns: List of employees in the department
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT e.id, e.name, e.email, e.phone, ecd.employee_number, 
                   ecd.company_join_date, ecd.status, des.name as designation_name
            FROM employees e
            JOIN employee_company_details ecd ON e.id = ecd.employee_id
            LEFT JOIN designations des ON ecd.designation_id = des.id
            WHERE ecd.department_id = %s AND e.deleted_at IS NULL
            ORDER BY e.name
        """
        
        cursor.execute(query, (department_id,))
        employees = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if employees:
            for employee in employees:
                for key, value in employee.items():
                    if isinstance(value, (datetime, date)):
                        employee[key] = value.isoformat()
            
            return json.dumps(employees, indent=2, default=str)
        else:
            return "No employees found in this department"
        
    except Exception as e:
        return f"Error: {str(e)}"

@server.tool()
async def get_employee_attendance(employee_id: int, start_date: str, end_date: str) -> str:
    """Get employee attendance records for a date range
    
    Args:
        employee_id: Employee ID
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
    
    Returns: Attendance records
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT date, status, clock_in, clock_out, late, early_leaving, overtime
            FROM attendance
            WHERE employee_id = %s AND date BETWEEN %s AND %s
            ORDER BY date DESC
        """
        
        cursor.execute(query, (employee_id, start_date, end_date))
        attendance = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if attendance:
            for record in attendance:
                for key, value in record.items():
                    if isinstance(value, (datetime, date)):
                        record[key] = value.isoformat()
            
            return json.dumps(attendance, indent=2, default=str)
        else:
            return "No attendance records found for the specified period"
        
    except Exception as e:
        return f"Error: {str(e)}"

@server.tool()
async def get_employee_leave_history(employee_id: int) -> str:
    """Get employee leave history
    
    Args:
        employee_id: Employee ID
    
    Returns: Leave history
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT l.*, lt.name as leave_type_name
            FROM leave l
            LEFT JOIN leave_type lt ON l.leave_type_id = lt.id
            WHERE l.employee_id = %s
            ORDER BY l.applied_on DESC
        """
        
        cursor.execute(query, (employee_id,))
        leaves = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if leaves:
            for leave in leaves:
                for key, value in leave.items():
                    if isinstance(value, (datetime, date)):
                        leave[key] = value.isoformat()
            
            return json.dumps(leaves, indent=2, default=str)
        else:
            return "No leave records found for this employee"
        
    except Exception as e:
        return f"Error: {str(e)}"

@server.tool()
async def get_departments() -> str:
    """Get all departments with their branches
    
    Returns: List of departments
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT d.*, b.name as branch_name, c.name as company_name
            FROM department d
            LEFT JOIN branch b ON d.branch_id = b.id
            LEFT JOIN companies c ON b.company_id = c.id
            WHERE d.deleted_at IS NULL
            ORDER BY c.name, b.name, d.name
        """
        
        cursor.execute(query)
        departments = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if departments:
            for dept in departments:
                for key, value in dept.items():
                    if isinstance(value, (datetime, date)):
                        dept[key] = value.isoformat()
            
            return json.dumps(departments, indent=2, default=str)
        else:
            return "No departments found"
        
    except Exception as e:
        return f"Error: {str(e)}"

@server.tool()
async def get_performance_cycles() -> str:
    """Get active performance cycles
    
    Returns: List of performance cycles
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT pc.*, lc.lookup_value as category_name, sc.status_name
            FROM performance_cycles pc
            LEFT JOIN lookup_config lc ON pc.category_id = lc.id
            LEFT JOIN status_config sc ON pc.status_id = sc.id
            WHERE pc.deleted_at IS NULL
            ORDER BY pc.start_date DESC
        """
        
        cursor.execute(query)
        cycles = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if cycles:
            for cycle in cycles:
                for key, value in cycle.items():
                    if isinstance(value, (datetime, date)):
                        cycle[key] = value.isoformat()
            
            return json.dumps(cycles, indent=2, default=str)
        else:
            return "No performance cycles found"
        
    except Exception as e:
        return f"Error: {str(e)}"

@server.tool()
async def get_employee_performance(employee_id: int, cycle_id: Optional[int] = None) -> str:
    """Get employee performance data
    
    Args:
        employee_id: Employee ID
        cycle_id: Performance cycle ID (optional)
    
    Returns: Performance data
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        if cycle_id:
            query = """
                SELECT ep.*, pc.cycle_name, pt.template_name, sc.status_name
                FROM employee_performance ep
                LEFT JOIN performance_cycles pc ON ep.cycle_id = pc.id
                LEFT JOIN performance_templates pt ON ep.template_id = pt.id
                LEFT JOIN status_config sc ON ep.status_id = sc.id
                WHERE ep.employee_id = %s AND ep.cycle_id = %s
            """
            cursor.execute(query, (employee_id, cycle_id))
        else:
            query = """
                SELECT ep.*, pc.cycle_name, pt.template_name, sc.status_name
                FROM employee_performance ep
                LEFT JOIN performance_cycles pc ON ep.cycle_id = pc.id
                LEFT JOIN performance_templates pt ON ep.template_id = pt.id
                LEFT JOIN status_config sc ON ep.status_id = sc.id
                WHERE ep.employee_id = %s
                ORDER BY pc.start_date DESC
            """
            cursor.execute(query, (employee_id,))
        
        performance = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if performance:
            for perf in performance:
                for key, value in perf.items():
                    if isinstance(value, (datetime, date)):
                        perf[key] = value.isoformat()
            
            return json.dumps(performance, indent=2, default=str)
        else:
            return "No performance data found for this employee"
        
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    asyncio.run(server.run()) 