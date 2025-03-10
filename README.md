### General
- This project's objective is to develop a set of browser automation tooling
- Its end user is non technical users, but the tools should be usable via CLI commands using the uv package manager as well as via python scripts, to be excecuted using uv as well (uv run ...)
- The main() script should be on src/autoBilanceo/__init__.py

### Implementation Progress

#### 1. Authentication Module
We've implemented secure browser automation for AFIP authentication with the following features:
- Anti-detection measures
- Human-like interaction patterns
- Geolocation spoofing (Córdoba, Argentina)
- Secure credential management via environment variables

##### System Requirements
Before running the automation, ensure you have the necessary dependencies:
```bash
# Install system dependencies
sudo apt-get install libnss3 libnspr4 libasound2t64

# Install browser binaries
uv run playwright install
```

##### Environment Setup
Create a `.env` file in your project root:

### Overview of the application flow - browser automation
- Navigate to [Afip auth web](https://auth.afip.gob.ar/contribuyente_/login.xhtml)
- Authenticate
- Navigate to [Mis servicios](https://portalcf.cloud.afip.gob.ar/portal/app/mis-servicios)
- Find the `Comprobantes en línea` service
- Complete a form with invoice data and then send the form (POST request)
- This process will be repeated n times (less than 200 times) asynchronously
- The data needed to fill the invoice form each time will be either on a csv file or a google sheet in the form of an n * m matrix where n is going to be each invoice issuer and m is going to be the different fields needed to complete the invoice form, the auth data will be included on those m columns

##### Testing
Two main test scripts are provided:
1. `test_auth`: Tests authentication only
```bash
uv run test_auth
```

2. `test_auth_plus_navigation`: Tests full navigation flow
```bash
uv run test_service_comprobantes
```

#### Security Features

1. **Browser Anti-Detection**:
   - Custom user agent rotation
   - Viewport randomization
   - Geolocation spoofing (Córdoba)
   - Timezone and locale configuration
   - Disabled automation flags

2. **Human-like Interaction**:
   ```python
   await asyncio.sleep(random.uniform(0.5, 1))  # Random delays
   await element.type(char, delay=random.uniform(100, 300))  # Natural typing
   ```

3. **Verification Systems**:
   - CUIT verification at login
   - CUIT re-verification at service entry
   - Page structure verification
   - Service-specific element checks

#### Next Steps in Development
- [ ] Implement invoice form automation
- [ ] Add CSV/Google Sheets integration
- [ ] Implement concurrent processing
- [ ] Add proper logging system
- [ ] Implement error recovery mechanisms

### Overview of the application flow - browser automation
- ✓ Navigate to [Afip auth web](https://auth.afip.gob.ar/contribuyente_/login.xhtml)
- ✓ Authenticate
- ✓ Navigate to [Mis servicios](https://portalcf.cloud.afip.gob.ar/portal/app/mis-servicios)
- ✓ Find the `Comprobantes en línea` service
- [ ] Complete a form with invoice data and then send the form (POST request)
- [ ] This process will be repeated n times (less than 200 times) asynchronously
- [ ] The data needed to fill the invoice form each time will be either on a csv file or a google sheet

### Error Handling
The system includes comprehensive error handling:
- Authentication failures
- Navigation timeouts
- CUIT mismatches
- Service availability issues
- Page structure changes

### Development Guidelines
1. Always maintain human-like interaction patterns
2. Verify CUIT at critical steps
3. Use verbose logging during development
4. Keep service-specific code in dedicated modules
5. Follow the existing modular architecture


