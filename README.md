
### General
- This project's objective is to develop a set of browser automation tooling
- Its end user is non technical users, but the tools should be usable via CLI commands using the uv package manager as well as via python scripts, to be excecuted using uv as well (uv run ...)
- The main() script should be on src/autoBilanceo/__init__.py

### Overview of the application flow - browser automation
- Navigate to [Afip auth web](https://auth.afip.gob.ar/contribuyente_/login.xhtml)
- Authenticate
- Navigate to [Mis servicios](https://portalcf.cloud.afip.gob.ar/portal/app/mis-servicios)
- Find the `Comprobantes en línea` service
- Complete a form with invoice data and then send the form (POST request)
- This process will be repeated n times (less than 200 times) asynchronously
- The data needed to fill the invoice form each time will be either on a csv file or a google sheet in the form of an n * m matrix where n is going to be each invoice issuer and m is going to be the different fields needed to complete the invoice form, the auth data will be included on those m columns


