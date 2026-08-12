# ============================================
# SON-IA - Comandos de desarrollo (Docker Compose)
#
# El target `up` inyecta el UID/GID del usuario actual para que el
# contenedor corra con los mismos permisos y los archivos de los
# volúmenes montados (ej: __pycache__) no queden como root.
# Esto hace que funcione igual en cualquier máquina Linux.
# ============================================

.PHONY: up down logs rebuild ps tunnel

# Levanta los servicios en background usando el UID/GID del usuario
up:
	UID=$(shell id -u) GID=$(shell id -g) docker compose up -d

# Levanta los servicios y reconstruye las imágenes
rebuild:
	UID=$(shell id -u) GID=$(shell id -g) docker compose up -d --build

# Detiene los servicios
down:
	docker compose down

# Muestra logs en tiempo real
logs:
	docker compose logs -f

# Estado de los servicios
ps:
	docker compose ps

# Expone el backend públicamente para que OpenWA pueda llamar al webhook.
# Usa localtunnel (https://loca.lt) - no requiere cuenta ni token.
# La URL generada cambia en cada ejecución; re-registra el webhook si cambia.
tunnel:
	npx --yes localtunnel --port 8000

# Muestra la URL pública del webhook que debe registrarse en OpenWA
webhook-url:
	@echo "1) En otra terminal ejecuta:  make tunnel"
	@echo "2) Copia la URL https://XXXX.loca.lt generada"
	@echo "3) Registra el webhook en OpenWA con:"
	@echo "   POST http://localhost:8000/api/v1/whatsapp/configure-webhook"
	@echo "   body: {\"url\": \"https://XXXX.loca.lt/api/v1/whatsapp/webhook\", \"session_name\": \"7d71ec12-907c-448d-9f3a-a859f5737f3c\"}"
