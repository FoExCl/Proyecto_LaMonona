# replit.md

## Overview

LaMonona is a Django-based employee management system for a business called "Ely Baby". The application provides user authentication, employee management functionality, and administrative controls. It features a role-based access system with different permissions for administrators and regular employees, along with a responsive web interface using Bootstrap styling.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Bootstrap 5 for responsive UI components and styling
- **Template Engine**: Django's built-in template system with template inheritance
- **Styling**: Custom CSS with pink/rose color scheme (#be185d primary color)
- **JavaScript Libraries**: jQuery, DataTables for enhanced table functionality, FontAwesome for icons
- **Layout Pattern**: Base template with sidebar navigation for authenticated users

### Backend Architecture
- **Framework**: Django 5.1.1 with MVT (Model-View-Template) pattern
- **Apps Structure**: Modular design with separate Django apps:
  - `Task`: Core employee and user management
  - Additional apps referenced but not included: `InventarioApp`, `CajaApp`, `VentasApp`, `GraficosApp`
- **Authentication**: Django's built-in authentication system with custom user forms
- **Authorization**: Role-based access control (administrators vs regular employees)
- **Forms**: Django forms with Bootstrap styling using crispy_forms and crispy_bootstrap5

### Data Storage Solutions
- **Database**: Django ORM with models for:
  - Employee management (Empleados)
  - Products (Productos)
  - Branches (Sucursales)
  - Cash registers (Cajas)
  - Sales (Ventas)
  - User authentication tables (AuthUser, AuthGroup, etc.)
- **Models**: Uses both managed Django models and unmanaged models for existing database tables

### Authentication and Authorization
- **Login System**: Custom authentication views with form validation
- **User Management**: Employee creation with role assignment (vendedor/administrador)
- **Password Management**: Django's built-in password reset functionality
- **Permission Control**: Staff-level permissions for administrative functions
- **Session Management**: Django's session framework for maintaining user state

## External Dependencies

### Python Packages
- **django**: Web framework
- **django-bootstrap5**: Bootstrap integration for Django
- **django-crispy-forms**: Enhanced form rendering
- **crispy-bootstrap5**: Bootstrap 5 support for crispy forms

### Frontend Libraries
- **Bootstrap 5**: CSS framework for responsive design
- **jQuery**: JavaScript library for DOM manipulation
- **DataTables**: Advanced table functionality with sorting, filtering, and export capabilities
- **FontAwesome**: Icon library
- **PDFMake**: PDF generation for export functionality

### Static Assets
- **External Images**: GitHub-hosted logo and branding images
- **CDN Resources**: Bootstrap, jQuery, DataTables, and other libraries served from CDNs

### Development Tools
- **Django Admin**: Administrative interface for database management
- **Debug Mode**: Enabled for development with DEBUG=True
- **Static Files**: Django's static file handling system