# Frontend - Fase 2

Interfaz funcional local para los módulos base: inicio de sesión, roles, CRUD de usuarios y CRUD de zonas de góndola.

## Ejecución local

```powershell
cd frontend
python -m http.server 8766
```

Abrir `http://localhost:8766`.

## Cuentas de demostración

| Rol | Correo | Contraseña |
|---|---|---|
| Administrador técnico | `admin@vision.local` | `Admin2026!` |
| Supervisor | `supervisor@vision.local` | `Supervisor2026!` |
| Reponedor | `reponedor@vision.local` | `Reponedor2026!` |

Los datos y sesión se mantienen en `localStorage` y `sessionStorage` para demostrar el frontend. La autenticación real se conectará posteriormente a FastAPI, PostgreSQL y JWT.
