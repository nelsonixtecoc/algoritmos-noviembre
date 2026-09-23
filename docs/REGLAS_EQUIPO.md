# Reglas de Trabajo en Equipo - RPG Estilo Zelda

## 1. Control de Versiones (Git)

### Branching Strategy
```
main (protegido, solo PRs)
  ├─ develop (opcional, integra features estables)
  ├─ feature/player-movement
  ├─ feature/enemy-ai
  ├─ feature/dungeon-system
  ├─ feature/boss-fight
  ├─ feature/ui-menus
  ├─ fix/collision-corner-case
  └─ docs/update-readme
```

### Reglas de Oro
1. **NUNCA push directo a `main`** — siempre Pull Request
2. **Ramas cortas** — máx 3 días de vida, 1 feature por rama
3. **Commits atómicos** — 1 cambio lógico = 1 commit
4. **Mensajes Conventional Commits:**
   ```
   feat: add player dash ability
   fix: enemy shooter not rotating to face player
   refactor: extract combat logic to systems/combat.py
   docs: update API docs for Entity class
   style: format with black
   test: add collision test cases
   ```

### Pull Request Template
```markdown
## Descripción
Breve explicación del cambio.

## Tipo
- [ ] Feature
- [ ] Bug fix
- [ ] Refactor
- [ ] Docs
- [ ] Style

## Cómo testear
1. Pasos para reproducir/verificar
2. Qué se espera ver

## Checklist
- [ ] Código formateado (`black .` / `ruff check .`)
- [ ] Sin warnings lint
- [ ] Probado en 640×480 y 960×720
- [ ] Actualiza docs si cambia API pública
- [ ] No rompe tests existentes

## Screenshots / Video
(Opcional pero recomendado para UI/visuals)

## Issues relacionados
Closes #123
```

### Code Review
- **Mínimo 1 aprobación** requerida para merge
- **Owner de `core/`** (Integrante 1) revisa TODO lo que toque `core/`, `entities/entity.py`, `config.py`
- **Tiempo máximo review:** 24h laborables
- **Comentarios:** Constructivos, específicos, con sugerencia de código si aplica

---

## 2. Convenciones de Código

### Python Style
- **Formateador:** `black` (line-length 100)
- **Linter:** `ruff` (reemplaza flake8 + isort + más)
- **Type hints:** Obligatorios en funciones públicas y métodos de clases públicas
- **Naming:**
  - `snake_case`: variables, funciones, métodos, módulos
  - `PascalCase`: clases, enums, exceptions
  - `UPPER_SNAKE_CASE`: constantes en `config.py`
  - `_leading_underscore`: "privado" interno del módulo
- **Imports:** Orden: stdlib → third-party → local; absolutos preferidos

### Ejemplo Mínimo
```python
# entities/player.py
from __future__ import annotations
from typing import TYPE_CHECKING

import pygame

from core.config import TILE_SIZE, PLAYER_SPEED
from entities.entity import Entity
from utils.animation import Animation

if TYPE_CHECKING:
    from world.room import Room


class Player(Entity):
    """Jugador controlado por el usuario."""

    def __init__(self, x: float, y: float, room: Room) -> None:
        super().__init__(x, y, room)
        self._speed: float = PLAYER_SPEED
        self._hp: int = 3
        self._max_hp: int = 3
        self._invulnerable_timer: float = 0.0
        self._attack_cooldown: float = 0.0
        self._setup_animations()

    def update(self, dt: float) -> None:
        self._handle_input()
        self._move(dt)
        self._update_timers(dt)
        super().update(dt)

    def take_damage(self, amount: int, knockback: pygame.Vector2) -> None:
        if self._invulnerable_timer > 0:
            return
        self._hp -= amount
        self._invulnerable_timer = 1.0
        self.velocity += knockback
```

### Documentación
- **Docstrings** en clases y métodos públicos (Google style o NumPy)
- **README.md** en raíz: cómo instalar, correr, controles, build
- **Architecture Decision Records (ADR)** para decisiones grandes (formato markdown en `docs/adr/`)

---

## 3. Estructura de Archivos y Assets

### Assets - Reglas Críticas
1. **Solo Integrante 6 modifica `assets/` directamente**
2. **Placeholders día 1:** Rectángulos de colores con nombre final
   ```
   assets/sprites/player/idle.png          # 16x16 rojo
   assets/sprites/enemies/walker/idle.png  # 16x16 verde
   assets/sprites/tiles/wall.png           # 16x16 gris
   ```
3. **Naming:** `categoria/nombre_estado[_direccion]_frame.png`
   - `player/walk_down_1.png`, `player/attack_up_3.png`
   - `enemies/walker/idle_1.png`
   - `tiles/ground_grass.png`
4. **Formato:** PNG (sprites), OGG/WAV (sonidos), TTF (fuentes)
5. **Tamaño:** Múltiplos de 16px (16, 32, 48, 64)

### Spritesheets vs Archivos Individuales
- **Inicios:** Archivos individuales (más fácil iterar)
- **Optimización:** Spritesheet + `utils/animation.py` al final si tiempo

---

## 4. Comunicación y Sincronización

### Daily Standup (15 min máx)
**Formato:** Cada integrante responde:
1. ¿Qué completé ayer?
2. ¿Qué hago hoy?
3. ¿Bloqueos? (necesito ayuda de X, espero asset Y, duda técnica Z)

**Horario fijo:** Ej. 19:00 todos los días (ajustar a disponibilidad real)

### Weekly Retrospective (Viernes 30 min)
**Formato:** Start / Stop / Continue
- **Start:** Qué deberíamos empezar a hacer
- **Stop:** Qué no funciona y debemos dejar
- **Continue:** Qué funciona bien

**Output:** 1-2 action items concretos para siguiente semana

### Canales de Comunicación
| Canal | Propósito |
|-------|-----------|
| Discord/Slack #general | Anuncios, dudas rápidas, coordinación |
| Discord/Slack #code-review | Links a PRs, pedir reviews |
| Discord/Slack #assets | Requests de assets, entrega de sprites/sonidos |
| Discord/Slack #bugs | Bug reports urgentes, crashes |
| GitHub Issues | Tareas planificadas, bugs no urgentes, features |
| GitHub PRs | Code review técnico |

### Escalación de Bloqueos
1. Preguntar en #general / daily
2. Si > 4h sin resolver → issue GitHub con label `blocked` + @mencionar a quien puede ayudar
3. Si > 1 día → escalar a Integrante 1 (Líder Técnico) para redistribuir o pair programming

---

## 5. Testing y Calidad

### Testing Manual (Obligatorio)
- Cada feature probada por **otro integrante** (no el autor)
- Checklist por PR (ver PR template)
- **Regression testing** semanal: juega 15 min build actual vs anterior

### Definición de "Done" (DoD)
Una tarea/issue está **Done** cuando:
- [ ] Código en `main` via PR aprobado
- [ ] `ruff check .` pasa (0 warnings)
- [ ] `black --check .` pasa
- [ ] Funciona en resolución base (640×480) y escalada (960×720)
- [ ] Probado con placeholders Y assets finales (si disponibles)
- [ ] Docstrings en clases/métodos públicos nuevos
- [ ] Actualiza `CHANGELOG.md` si feature user-facing
- [ ] Commits limpios (squash si necesario antes de merge)

### Bug Tracking
- **Critical:** Crash, data loss, game unplayable → fix inmediato, bloquea release
- **Major:** Feature rota, balance roto, visual glitch obvio → fix esta semana
- **Minor:** Cosmético, edge case raro, mejora UX → backlog, fix si tiempo
- **Labels:** `bug/critical`, `bug/major`, `bug/minor`, `feat`, `docs`, `tech-debt`

---

## 6. Arquitectura - Reglas de Módulos

### Interfaces Compartidas (No tocar sin avisar)
| Archivo | Owner | Quién puede tocar |
|---------|-------|-------------------|
| `config.py` | Integrante 1 | Todos (solo leer/añadir constantes) |
| `entities/entity.py` | Integrante 1 + 2 | Integrante 1, 2, 3 (coordinar) |
| `core/game.py` | Integrante 1 | Solo Integrante 1 |
| `core/events.py` | Integrante 1 | Todos (solo emitir/escuchar eventos) |
| `world/tilemap.py` | Integrante 4 | Integrante 4 + 1 |

### Event Bus (Desacoplamiento)
Usar `core/events.py` para comunicación cross-module:
```python
# En player.py - emitir
from core.events import event_bus, EventType
event_bus.publish(EventType.PLAYER_ATTACKED, {"damage": 1, "pos": self.pos})

# En enemy.py - escuchar
event_bus.subscribe(EventType.PLAYER_ATTACKED, self.on_player_attacked)
```
**Eventos definidos:** `PLAYER_ATTACKED`, `ENEMY_DIED`, `PICKUP_COLLECTED`, `ROOM_CHANGED`, `GAME_OVER`, `VICTORY`

### Dependencias Permitidas (Direccionales)
```
core/           →  nadie (base)
entities/       →  core/
world/          →  core/, entities/
systems/        →  core/, entities/, world/
ui/             →  core/, entities/, systems/
utils/          →  nadie (helpers puros)
```
**Regla:** No imports circulares. Si necesitas, refactoriza a `systems/` o `core/events.py`.

---

## 7. Gestión de Tiempo y Scope

### Timeboxing
- **Tasks en tablero:** Estimadas en horas (1h, 2h, 4h, 8h)
- **Si tarea > 8h:** Dividir en subtareas
- **Si tarea toma 2x estimado:** Parar, reevaluar en daily, pedir ayuda o simplificar

### Scope Freeze
- **H2 (Fin Semana 2):** Freeze de **nuevas features** (solo bugfixes y pulido)
- **H3 (Fin Semana 3):** Freeze de **cambios de arquitectura** (solo contenido: rooms, enemies, tuning)
- **Nuevas ideas:** → Backlog "Post-Entrega" / "v1.1"

### Priorización (MoSCoW)
| Prioridad | Qué incluye |
|-----------|-------------|
| **Must Have** | Core loop, movimiento, combate, 3 enemigos, boss, 6 rooms, game over, victory |
| **Should Have** | Save/load, HUD completo, sonidos, música, minimapa |
| **Could Have** | Level up/EXP, dialogue system, secret room, particle effects, screen shake |
| **Won't Have** | Multiplayer, inventory complejo, crafting, multiple weapons, skill tree |

---

## 8. Roles y Responsabilidades (Resumen)

| Rol | Quién | Decisiones Finales En |
|-----|-------|----------------------|
| **Tech Lead** | Integrante 1 | Arquitectura, `core/`, merge strategy, build, scope freeze |
| **Player Owner** | Integrante 2 | `entities/player.py`, `systems/combat.py`, feel de controles |
| **Enemy Owner** | Integrante 3 | `entities/enemies/`, `entities/boss.py`, `systems/pathfinding.py`, IA |
| **World Owner** | Integrante 4 | `world/`, level design, progresión, tilemap |
| **UI/UX Owner** | Integrante 5 | `ui/`, menús, HUD, sonidos, juice/feedback |
| **Assets/QA Owner** | Integrante 6 | `assets/`, placeholders → finales, testing, bug tracking, release |

**Decisiones técnicas compartidas** (requieren consenso 4/6):
- Cambiar motor/stack (no aplicar)
- Cambiar resolución base
- Cambiar formato tilemap (CSV ↔ TMX)
- Añadir dependencia externa nueva

---

## 9. Herramientas Recomendadas

### Desarrollo
- **Editor:** VS Code + extensiones (Python, Pylance, Ruff, Black Formatter, GitLens)
- **Terminal:** Windows Terminal / PowerShell 7+
- **Git:** GitHub Desktop (visual) o CLI

### Debugging
- `python -m debugpy --listen 5678 --wait-for-client main.py` + VS Code Debug
- `utils/debug.py`: `DEBUG = True` → muestra hitboxes, FPS, grid, coords

### Assets
- **Sprites:** Aseprite (pago), LibreSprite (gratis), Piskel (web)
- **Tilemap:** Tiled (gratis) + `pytmx`
- **Sonidos:** sfxr/bfxr (web), Audacity (editar)
- **Música:** Bosca Ceoil, BeepBox, o assets libres (OpenGameArt, itch.io)

### Testing
- Checklist manual en Notion/Excel/GitHub Projects
- Grabadora: OBS Studio (video demo final)

---

## 10. Checklist de Inicio (Día 1 - Marcar todo)

- [ ] Repo creado y clonado por todos
- [ ] `.gitignore`, `requirements.txt`, `README.md` básicos
- [ ] `ruff` + `black` configurados y pasando
- [ ] `main.py` corre ventana 640×480 60 FPS
- [ ] `config.py` con constantes base
- [ ] Tablero GitHub Projects creado con columnas
- [ ] Issues creados para H0 (Setup) asignados
- [ ] Daily standup horario acordado
- [ ] Discord/Slack canales creados
- [ ] Integrante 6 sube placeholders a `assets/`
- [ ] Convención commits acordada y documentada
- [ ] PR template en `.github/pull_request_template.md`

---

## 11. Contactos de Emergencia

| Situación | Acción |
|-----------|--------|
| Repo roto (main no compila) | @Integrante 1 immediately, revert último merge si necesario |
| Pérdida de trabajo local | `git stash`, `git reflog`, preguntar a compañero si tiene copia |
| Asset crítico faltante 2 días antes | Placeholder programado + issue `bug/critical` |
| Integrante enfermo/ausente > 3 días | Redistribuir sus tareas "Must Have" entre resto, cortar "Could Have" |
| Merge conflict infernal | Pair programming: autor + Integrante 1 resuelven juntos en llamada |

---

**Firmado por el equipo (compromiso verbal en daily):**

- Integrante 1 (Core): ________________
- Integrante 2 (Player): ________________
- Integrante 3 (Enemies): ________________
- Integrante 4 (World): ________________
- Integrante 5 (UI/UX): ________________
- Integrante 6 (Assets/QA): ________________

**Fecha:** ________________