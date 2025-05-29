#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import uuid
import json
import os
from datetime import datetime

logger = logging.getLogger(__name__)


class Project:
    """Represents a project in the data acquisition system."""

    def __init__(self, name="", description="", project_id=None):
        self.project_id = project_id or str(uuid.uuid4())
        self.name = name
        self.description = description
        self.devices = []
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at

    def add_device(self, device):
        """Add a device to the project."""
        self.devices.append(device)
        self.updated_at = datetime.now().isoformat()
        return True

    def remove_device(self, device_id):
        """Remove a device from the project by ID."""
        for i, device in enumerate(self.devices):
            if device.device_id == device_id:
                del self.devices[i]
                self.updated_at = datetime.now().isoformat()
                return True
        return False

    def get_device(self, device_id):
        """Get a device by its ID."""
        for device in self.devices:
            if device.device_id == device_id:
                return device
        return None

    def to_dict(self):
        """Convert project to a dictionary."""
        return {
            "project_id": self.project_id,
            "name": self.name,
            "description": self.description,
            "devices": [device.to_dict() for device in self.devices],
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data):
        """Create a project from a dictionary."""
        from frontend.models.device_model import Device

        project = cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            project_id=data.get("project_id")
        )
        project.created_at = data.get("created_at", project.created_at)
        project.updated_at = data.get("updated_at", project.updated_at)

        # Add devices
        for device_data in data.get("devices", []):
            device = Device.from_dict(device_data)
            project.devices.append(device)

        return project


class ProjectManager:
    """Manages projects in the system."""

    def __init__(self, projects_dir="projects"):
        self.projects_dir = projects_dir
        self.projects = []
        self.current_project = None

        # Ensure projects directory exists
        os.makedirs(self.projects_dir, exist_ok=True)

    def create_project(self, name, description=""):
        """Create a new project."""
        project = Project(name=name, description=description)
        self.projects.append(project)
        self.current_project = project
        return project

    def load_projects(self):
        """Load all projects from the projects directory."""
        self.projects = []

        if not os.path.exists(self.projects_dir):
            os.makedirs(self.projects_dir)
            return

        for filename in os.listdir(self.projects_dir):
            if filename.endswith(".json"):
                try:
                    project_path = os.path.join(self.projects_dir, filename)
                    with open(project_path, 'r', encoding='utf-8') as f:
                        project_data = json.load(f)
                        project = Project.from_dict(project_data)
                        self.projects.append(project)
                except Exception as e:
                    logger.error(f"Error loading project from {filename}: {str(e)}")

    def save_project(self, project):
        """Save a project to disk."""
        if not os.path.exists(self.projects_dir):
            os.makedirs(self.projects_dir)

        project_path = os.path.join(self.projects_dir, f"{project.project_id}.json")
        fccs_data_cache_path = os.path.join("...", "fccs")
        if not os.path.exists(fccs_data_cache_path):
            os.makedirs(fccs_data_cache_path)
        fms_data_cache_path = os.path.join("...", "fms")
        if not os.path.exists(fms_data_cache_path):
            os.makedirs(fms_data_cache_path)
        # 新增点表文件写入（S7）
        for device in project.get('devices'):
            if device.get('device_type').startwith("S7"):
                if project.get('device').get('name') == 'fccs':
                    s7_cache = os.path.join(fccs_data_cache_path, 'S7_cache')
                    if not os.path.exists(s7_cache):
                        os.makedirs(s7_cache)
                    var_table = []
                    variable = project.get('device').get('variables')
                    for var in variable:
                        var_name = var.get('name')
                        var_type = var.get('data_type')
                        var_db = var.get('address').split('.')[2:]
                        var_offset = '.'.join(var.get('address').split('.')[1:])
                        var_table.append([var_name, var_type, var_db, var_offset])
                else:
                    s7_cache = os.path.join(fms_data_cache_path, 'S7_cache')
                    if not os.path.exists(s7_cache):
                        os.makedirs(s7_cache)
                    var_table = []
                    variable = project.get('device').get('variables')
                    for var in variable:
                        var_name = var.get('name')
                        var_type = var.get('data_type')
                        var_db = var.get('address').split('.')[2:]
                        var_offset = '.'.join(var.get('address').split('.')[1:])
                        var_table.append([var_name, var_type, var_db, var_offset])
            pass

        try:
            with open(project_path, 'w', encoding='utf-8') as f:
                json.dump(project.to_dict(), f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving project {project.name}: {str(e)}")
            return False

    def delete_project(self, project_id):
        """Delete a project."""
        for i, project in enumerate(self.projects):
            if project.project_id == project_id:
                # Remove from memory
                del self.projects[i]

                # Remove from disk
                project_path = os.path.join(self.projects_dir, f"{project_id}.json")
                if os.path.exists(project_path):
                    try:
                        os.remove(project_path)
                    except Exception as e:
                        logger.error(f"Error deleting project file {project_path}: {str(e)}")

                # Reset current project if it was deleted
                if self.current_project and self.current_project.project_id == project_id:
                    self.current_project = None if not self.projects else self.projects[0]

                return True
        return False

    def get_project(self, project_id):
        """Get a project by its ID."""
        for project in self.projects:
            if project.project_id == project_id:
                return project
        return None

    def set_current_project(self, project_id):
        """Set the current active project."""
        project = self.get_project(project_id)
        if project:
            self.current_project = project
            return True
        return False
