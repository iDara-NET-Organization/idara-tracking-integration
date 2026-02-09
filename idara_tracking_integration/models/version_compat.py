# -*- coding: utf-8 -*-
"""
Version Compatibility Layer for Odoo 15-19
===========================================

This module ensures compatibility across different Odoo versions.
"""

from odoo import release


def get_odoo_version():
    """Get major Odoo version number"""
    version = release.version_info[0]
    return int(version) if isinstance(version, str) else version


def is_odoo_15_or_lower():
    """Check if running on Odoo 15 or lower"""
    return get_odoo_version() <= 15


def is_odoo_16_or_higher():
    """Check if running on Odoo 16 or higher"""
    return get_odoo_version() >= 16


def is_odoo_17_or_higher():
    """Check if running on Odoo 17 or higher"""
    return get_odoo_version() >= 17


def is_odoo_18_or_higher():
    """Check if running on Odoo 18 or higher"""
    return get_odoo_version() >= 18


def is_odoo_19_or_higher():
    """Check if running on Odoo 19 or higher"""
    return get_odoo_version() >= 19


def get_company_field():
    """
    Get correct company field definition based on Odoo version
    In Odoo 17+, default lambda functions need to be updated
    """
    from odoo import fields
    
    if is_odoo_17_or_higher():
        # Odoo 17+ uses different context access
        return fields.Many2one(
            'res.company',
            string='Company',
            default=lambda self: self.env.company.id
        )
    else:
        # Odoo 15-16
        return fields.Many2one(
            'res.company',
            string='Company',
            default=lambda self: self.env.company
        )


def safe_json_response(data):
    """
    Create JSON response compatible with all Odoo versions
    """
    from odoo.http import request
    import json
    
    if is_odoo_17_or_higher():
        # Odoo 17+ might have different JSON handling
        return request.make_json_response(data)
    else:
        # Odoo 15-16
        return data


def get_request_env():
    """
    Get request environment in a version-compatible way
    """
    from odoo.http import request
    return request.env


def render_template(template_name, values):
    """
    Render template in a version-compatible way
    """
    from odoo.http import request
    return request.render(template_name, values)
