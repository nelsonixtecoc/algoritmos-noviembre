# Reglas de Trabajo en Equipo - Wave Defense

## 1. Control de Versiones (Git)

### Branching Strategy
```
main (protegido, solo PRs)
  ├─ develop (opcional, integra features estables)
  ├─ feature/player-movement
  ├─ feature/weapon-system
  ├─ feature/enemy-basic
  ├─ feature/wave-manager
  ├─ feature/barriers
  ├─ feature/particles
  ├─ feature/upgrade-shop
  ├─ feature/boss-wave5
  ├─ feature/boss-wave10
  ├─ feature/ui-hud
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
- [ ] Probado en 640×480
- [ ] Actualiza docs si cambia API pública
- [ ] No rompe features existentes

## Screenshots / Video
(Opcional pero recomendado para UI/visuals)

## Issues relacionados
Closes #123
```

### Code Review
- **Mínimo 1 aprobación** requerida para merge
- **Owner de `core/`** (Nelson) revisa TODO lo que toque `core/`, `entities/entity.py`, `config.py`
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

from config import PLAYER_SPEED, PLAYER_HP
from entities.entity import Entity
from utils.animation import Animation

if TYPE_CHECKING:
    from systems.wave_manager import WaveManager


class Player(Entity):
    """Jugador controlado por el usuario."""

    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y)
        self._speed: float = PLAYER_SPEED
        self._hp: int = PLAYER_HP
        self._max_hp: int = PLAYER_HP
        self._invulnerable_timer: float = 0.0
        self._current_weapon_index: int = 0
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
1. **Solo Leslie (Integrante 6) modifica `assets/` directamente**
2. **Placeholders día 1:** Rectángulos de colores con nombre final
   ```
   assets/sprites/player/idle.png           # 32x32 azul
   assets/sprites/enemies/basic/idle.png    # 32x32 rojo
   assets/sprites/weapons/pistol.png        # 16x16 amarillo
   assets/sprites/barrier/barrier_1.png     # 40x40 gris
   assets/sprites/ui/heart_full.png         # 16x16 rojo
   ```
3. **Naming:** `categoria/nombre_estado[_direccion]_frame.png`
   - `player/idle.png`, `player/walk_down_1.png`, `player/shoot.png`
   - `enemies/basic/walk_1.png`, `enemies/tank/idle.png`
   - `weapons/pistol.png`, `weapons/shotgun.png`
   - `barrier/barrier_1.png` ... `barrier_4.png`
   - `particles/spark.png`, `particles/smoke.png`
4. **Formato:** PNG (sprites), OGG/WAV (sonidos), TTF (fuentes)
5. **Tamaño:** Múltiplos de 16px (16, 32, 48, 64)

### Spritesheets vs Archivos Individuales
- **Inicio:** Archivos individuales (más fácil iterar)
- **Optimización:** Spritesheet + `utils/animation.py` en Semana 3-4 si tiempo

---

## 4. Comunicación y Sincronización

### Daily Standup (15 min máx)
**Formato:** Cada integrante responde:
1. ¿Qué completé ayer?
2. ¿Qué hago hoy?
3. ¿Bloqueos? (necesito ayuda de X, espero asset Y, duda técnica Z)

**Horario fijo:** Ej. 19:00 todos los días (ajustar a disponibilidad real)

### Weekly Retrospective (Viernes 30 min - coinciden con Demo)
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
3. Si > 1 día → escalar a Nelson (Líder Técnico) para redistribuir o pair programming

---

## 5. Testing y Calidad

### Testing Manual (Obligatorio)
- Cada feature probada por **otro integrante** (no el autor)
- Checklist por PR (ver PR template)
- **Regression testing** semanal: juega 15 min build actual vs anterior (viernes)

### Definición de "Done" (DoD)
Una tarea/issue está **Done** cuando:
- [ ] Código en `main` via PR aprobado
- [ ] `ruff check .` pasa (0 warnings)
- [ ] `black --check .` pasa
- [ ] Funciona en resolución base (640×480)
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
| `config.py` | Nelson | Todos (solo leer/añadir constantes) |
| `entities/entity.py` | Nelson + Fabiola | Nelson, Fabiola, Lilian, Zebedeo (coordinar) |
| `core/game.py` | Nelson | Solo Nelson |
| `core/events.py` | Nelson | Todos (solo emitir/escuchar eventos) |
| `core/save_load.py` | Nelson | Nelson + Aron (highscores) |

### Event Bus (Desacoplamiento) - ÚNICA forma cross-module
Usar `core/events.py` para comunicación entre módulos:
```python
# En player.py - emitir
from core.events import event_bus, EventType
event_bus.publish(EventType.ENEMY_KILLED, {"gold": 10, "pos": enemy.pos})

# En wave_manager.py - escuchar
event_bus.subscribe(EventType.WAVE_COMPLETE, self.on_wave_complete)

# En particles.py - escuchar
event_bus.subscribe(EventType.ENEMY_DIED, self.spawn_death_particles)
```
**Eventos definidos (enum `EventType` en `core/events.py`):**
- `PLAYER_DAMAGED`, `PLAYER_DIED`, `PLAYER_SHOOT`, `WEAPON_SWITCHED`
- `ENEMY_SPAWNED`, `ENEMY_DIED`, `ENEMY_REACHED_BASE`
- `BARRIER_DAMAGED`, `BARRIER_DESTROYED`, `BARRIER_REPAIRED`
- `PICKUP_SPAWNED`, `PICKUP_COLLECTED`
- `WAVE_STARTED`, `WAVE_COMPLETED`, `BOSS_SPAWNED`, `BOSS_PHASE_CHANGE`
- `UPGRADE_PURCHASED`, `GOLD_CHANGED`
- `GAME_OVER`, `VICTORY`, `STATE_CHANGED`

### Dependencias Permitidas (Direccionales - NO circulares)
```
core/           →  nadie (base)
entities/       →  core/
systems/        →  core/, entities/
ui/             →  core/, entities/, systems/
utils/          →  nadie (helpers puros)
config/         →  nadie (solo JSON data)
```
**Regla:** No imports circulares. Si necesitas, refactoriza a `systems/` o usa `core/events.py`.

---

## 7. Gestión de Tiempo y Scope

### Timeboxing
- **Tasks en tablero:** Estimadas en horas (1h, 2h, 4h, 8h)
- **Si tarea > 8h:** Dividir en subtareas
- **Si tarea toma 2x estimado:** Parar, reevaluar en daily, pedir ayuda o simplificar

### Scope Freeze (FECHAS INMOVIBLES)
- **H1 (Fin Semana 2 - 19 Oct):** Freeze de **nuevas mecánicas core** (player, armas, enemigos básicos, oleadas)
- **H2 (Fin Semana 3 - 26 Oct):** Freeze de **nuevos sistemas** (barreras, power-ups, partículas, upgrade shop)
- **H3 (Fin Semana 4 - 2 Nov):** Freeze de **contenido nuevo** (solo balanceo, pulido, bugs)
- **Nuevas ideas:** → Backlog "Post-Entrega" / "v1.1" en GitHub Projects

### Priorización (MoSCoW) - Wave Defense
| Prioridad | Qué incluye |
|-----------|-------------|
| **Must Have** | Player movimiento+armas, 6 enemigos, 2 bosses, oleadas 1-15, barreras, power-ups, upgrade shop, 3 vidas, game over/victory, highscores, HUD, menús, partículas básicas, build .exe |
| **Should Have** | Screen shake, flash daño, 2ª arena, stats screen post-partida, dificultad ajustable |
| **Could Have** | Trail partículas por arma, shaders simples, secret wave, cheat codes debug |
| **Won't Have** | Multiplayer, inventory, crafting, skill tree, diálogo NPCs, save mid-run, online leaderboard |

---

## 8. Roles y Responsabilidades (Resumen - Wave Defense)

| Rol | Quién | Decisiones Finales En |
|-----|-------|----------------------|
| **Tech Lead / Core** | Nelson | Arquitectura, `core/`, `config.py`, `utils/helpers.py`, merge strategy, build, scope freeze, code review owner |
| **Player & Weapons** | Fabiola | `entities/player.py`, `entities/weapons/`, `entities/projectile.py`, `systems/combat.py`, `entities/entity.py` (base), feel controles |
| **Enemies & Waves** | Lilian | `entities/enemies/`, `entities/boss.py`, `systems/wave_manager.py`, `config/waves.json`, IA, spawning, balanceo oleadas |
| **Barriers, Pickups & Particles** | Zebedeo | `entities/barrier.py`, `entities/pickup.py`, `systems/particles.py`, `utils/debug.py`, object pooling, screen shake, visual feedback |
| **UI, Upgrades & Menus** | Aron | `ui/hud.py`, `ui/menus.py`, `ui/upgrade_ui.py`, `systems/upgrade_shop.py`, `config/upgrades.json`, `core/save_load.py` (highscores), sonidos integración |
| **Assets & QA Lead** | Leslie | `assets/`, `utils/animation.py`, testing manual, bug tracking, README, video demo, placeholders → finales |

**Decisiones técnicas compartidas** (requieren consenso 4/6):
- Cambiar motor/stack (no aplicar)
- Cambiar resolución base (640×480)
- Añadir dependencia externa nueva (solo stdlib + pygame-ce)
- Cambiar patrón arquitectura (EventBus, StateMachine, etc.)

---

## 9. Herramientas Recomendadas

### Desarrollo
- **Editor:** VS Code + extensiones (Python, Pylance, Ruff, Black Formatter, GitLens)
- **Terminal:** Windows Terminal / PowerShell 7+
- **Git:** GitHub Desktop (visual) o CLI

### Debugging
- `python -m debugpy --listen 5678 --wait-for-client main.py` + VS Code Debug
- `utils/debug.py`: `DEBUG = True` → muestra hitboxes, FPS, entity counts, wave info

### Assets
- **Sprites:** Aseprite (pago), LibreSprite (gratis), Piskel (web)
- **Sonidos:** sfxr/bfxr (web), Audacity (editar)
- **Música:** Bosca Ceoil, BeepBox, o assets libres (OpenGameArt, itch.io)

### Testing
- Checklist manual en GitHub Projects / Notion / Excel
- Grabadora: OBS Studio (video demo final 2 min)

---

## 10. Checklist de Inicio (Día 1 - 6 Oct - Marcar todo)

- [ ] Repo creado y clonado por todos
- [ ] `.gitignore`, `requirements.txt` (pygame-ce), `README.md` básicos
- [ ] `ruff` + `black` configurados y pasando (`ruff check .`, `black --check .`)
- [ ] `main.py` corre ventana 640×480 60 FPS
- [ ] `config.py` con constantes base (WIDTH, HEIGHT, FPS, PLAYER_SPEED, PLAYER_HP, etc.)
- [ ] Tablero GitHub Projects creado con columnas: Backlog, Todo, In Progress, Review, Done
- [ ] Issues creados para H0 (Setup) asignados a cada integrante
- [ ] Daily standup horario acordado y puesto en calendarios
- [ ] Discord/Slack canales creados (#general, #code-review, #assets, #bugs)
- [ ] Leslie sube placeholders a `assets/sprites/`, `assets/sounds/`, `assets/fonts/`
- [ ] Convención commits acordada y documentada en este archivo
- [ ] PR template en `.github/pull_request_template.md`

---

## 11. Contactos de Emergencia

| Situación | Acción |
|-----------|--------|
| Repo roto (main no compila) | @Nelson immediately, revert último merge si necesario |
| Pérdida de trabajo local | `git stash`, `git reflog`, preguntar a compañero si tiene copia |
| Asset crítico faltante 2 días antes | Placeholder programado + issue `bug/critical` |
| Integrante enfermo/ausente > 3 días | Redistribuir sus tareas "Must Have" entre resto, cortar "Could Have" |
| Merge conflict infernal | Pair programming: autor + Nelson resuelven juntos en llamada |

---

## 12. Firmado por el equipo (compromiso verbal en daily H0)

- Nelson (Core): ________________
- Fabiola (Player/Weapons): ________________
- Lilian (Enemies/Waves): ________________
- Zebedeo (Barriers/Particles): ________________
- Aron (UI/Upgrades): ________________
- Leslie (Assets/QA): ________________

**Fecha:** ________________