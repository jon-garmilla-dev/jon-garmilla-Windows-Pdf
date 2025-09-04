# Payroll Management System

Desktop application for automated payroll processing and email distribution.

## Overview

Processes employee payrolls from PDF documents and sends them via email. Features a step-by-step workflow with data validation, error handling, and reporting.

## Features

### Core Functionality
- **Multi-step Workflow**: Four-stage process with sequential navigation security
- **PDF Processing**: Extract individual payrolls from master PDF documents
- **Email Distribution**: Automated email sending with robust retry logic
- **Data Validation**: Comprehensive employee data verification and mapping
- **Encrypted Storage**: Secure password storage with optional encryption

### User Interface
- Windows-style interface
- Real-time progress tracking
- Error reporting with recommendations
- Context-sensitive tooltips
- Cross-platform support (Windows, macOS, Linux)

### Reporting
- Excel reports with formatting
- Success/error statistics
- Audit trail with timestamps

### Technical Features
- SMTP with retry logic
- PDF encryption
- Audio notifications
- Customizable templates
- Automatic logging

## Technology Stack

- **Python 3.9+**: Core application framework
- **Tkinter**: GUI framework with professional styling
- **PyMuPDF (fitz)**: PDF processing and manipulation
- **pikepdf**: PDF encryption capabilities
- **pandas**: Data processing and CSV/Excel handling
- **openpyxl**: Excel report generation with formatting
- **cryptography**: Secure password encryption (optional)
- **smtplib**: Email sending with SSL/TLS support

## Installation

### Prerequisites

Ensure Python 3.9 or higher is installed on your system.

### Dependencies

Install required packages:

```bash
pip install -r requirements.txt
```

### System-Specific Requirements

#### Linux
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk python3-pil python3-pil.imagetk

# For enhanced audio support
sudo apt-get install pulseaudio-utils alsa-utils
```

#### Windows
No additional system packages required. All dependencies are included with Python or pip packages.

#### macOS
No additional system packages required. Audio feedback uses built-in system sounds.

## Quick Start

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd payroll-system
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python sistema_nominas/main.py
   ```

4. **First-time setup**:
   - Configure email credentials in Settings
   - Set up SMTP server details
   - Choose output folder preferences

## Application Workflow

### Step 1: File Selection
- Select master PDF containing all payrolls
- Choose employee data file (CSV or Excel)
- Map data columns to required fields (NIF, Name, Last Name, Email)
- Preview data to verify correct mapping

### Step 2: Data Verification
- Review extracted employee information
- Validate NIF matches between PDF and data file
- Identify and resolve data inconsistencies
- Preview individual payroll pages

### Step 3: Email Distribution
- Send encrypted payroll PDFs to employees
- Monitor real-time sending progress
- Handle errors with automatic retry logic
- Track successful and failed deliveries

### Step 4: Process Completion
- Review comprehensive statistics
- Access generated reports and files
- Open output folders for manual review
- Start new processing cycle if needed

## Configuration

### Email Settings
- **SMTP Server**: Configure your email provider's SMTP settings
- **Authentication**: Support for standard and app-specific passwords
- **Templates**: Customize email subject and body templates
- **Security**: Optional password encryption for enhanced security

### File Formats
- **PDF Passwords**: Set master passwords for enhanced security
- **Filename Templates**: Customize output filename patterns
- **Output Organization**: Automatic folder structure with date-based organization

### Advanced Options
- **Retry Logic**: Configurable retry attempts and delays
- **Batch Processing**: Adjust batch sizes and timing
- **Logging Levels**: Control log detail and retention
- **Sound Notifications**: Enable/disable audio feedback

## Output Structure

The application creates organized output folders:

```
nominas_YYYY_MM/
├── pdfs_enviados/          # Successfully sent payrolls (encrypted)
├── pdfs_pendientes/        # Unprocessed payrolls (unencrypted)
├── master_pdf_copy.pdf     # Copy of original PDF
├── reporte_envio_*.xlsx    # Comprehensive Excel report
└── resumen_proceso.txt     # Quick summary report
```

## Troubleshooting

### Common Issues

**Application won't start**:
- Run `python sistema_nominas/diagnostico.py` for system diagnostics
- Verify all dependencies are installed
- Check Python version compatibility

**Email sending fails**:
- Verify SMTP settings and credentials
- Check firewall and antivirus settings
- Ensure app-specific passwords are used for Gmail/Outlook

**PDF processing errors**:
- Verify PDF is not password-protected
- Check NIF format in employee data
- Ensure employee data file is properly formatted

**Linux-specific issues**:
- Install tkinter: `sudo apt-get install python3-tk`
- Install PIL support: `sudo apt-get install python3-pil.imagetk`
- Check audio system for sound notifications

### Diagnostic Tools

Run the built-in diagnostic script:
```bash
python sistema_nominas/diagnostico.py
```

This will check:
- Python version compatibility
- Required library availability
- System-specific components
- Audio system functionality

## Security Considerations

- **Password Storage**: Uses cryptographic encryption when available
- **PDF Security**: Individual payrolls are encrypted with employee NIFs
- **Email Security**: Supports SSL/TLS encrypted SMTP connections
- **Data Handling**: Temporary files are automatically cleaned up
- **Access Control**: Sequential workflow prevents unauthorized access to later steps

## Project Structure

```
sistema_nominas/
├── main.py                 # Application entry point
├── logic/                  # Business logic modules
│   ├── settings.py         # Configuration management
│   ├── security.py         # Encryption and security
│   ├── file_handler.py     # PDF and data file processing
│   ├── email_sender.py     # Email distribution logic
│   ├── email_reports.py    # Report generation
│   └── ...
├── ui/                     # User interface modules
│   ├── main_window.py      # Main application window
│   ├── paso1.py           # Step 1: File selection
│   ├── paso2.py           # Step 2: Data verification
│   ├── paso3.py           # Step 3: Email sending
│   └── ...
├── utils/                  # Utility modules
│   ├── logger.py          # Logging system
│   └── sound_manager.py   # Audio notifications
└── diagnostico.py         # System diagnostic tool
```


## License

This software is proprietary and intended for internal business use only.