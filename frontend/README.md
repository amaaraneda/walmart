# Frontend - Fase 2

Interfaz local para los módulos base y el análisis visual beta de góndolas. En Análisis visual el checkpoint YOLO aportado por un compañero es el predeterminado; el YOLO26n anterior sigue disponible para comparación. Se muestra una **estimación experimental de ocupación frontal por nivel** cuando la imagen permite inferir niveles y ancho útil; no es inventario físico ni una medición validada. Un detector de huecos separado puede mostrar cajas rojas candidatas. La alerta automática del 30 % permanece desactivada y las fotos sin límites coherentes se muestran como «no evaluable». Los pesos son locales y están excluidos de Git. La cámara se retiró de esta etapa. Ver [protocolo de etiquetado](../docs/PROTOCOLO_ETIQUETADO_GONDOLAS.md), [auditoría del nuevo dataset de vacíos](../docs/DATASET_VACIOS_V1.md) y [experimento de huecos](../docs/EXPERIMENTO_HUECOS.md).

## Ejecución local

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.app:app --reload --host 127.0.0.1 --port 8000
```

Abrir `http://localhost:8000`. Para preparar el modelo, consulta [MVP_GONDOLAS.md](../MVP_GONDOLAS.md).

## Cuentas de demostración

| Rol | Correo | Contraseña |
|---|---|---|
| Administrador técnico | `admin@vision.local` | `Admin2026!` |
| Supervisor | `supervisor@vision.local` | `Supervisor2026!` |
| Reponedor | `reponedor@vision.local` | `Reponedor2026!` |

Los datos y sesión se mantienen en `localStorage` y `sessionStorage` para demostrar el frontend. **No es autenticación segura ni controla el acceso a la API.** No uses estas cuentas en producción.
