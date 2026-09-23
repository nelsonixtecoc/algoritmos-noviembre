# Tareas por Integrante - RPG Estilo Zelda

## Asignación de Roles (6 Integrantes)

| # | Integrante | Rol | Módulos Responsables | Archivos Clave |
|---|------------|-----|----------------------|----------------|
| 1 | **Integrante 1** | Líder Técnico / Core | Game loop, State machine, Camera, Events, Build | `main.py`, `config.py`, `core/game.py`, `core/camera.py`, `core/events.py`, `core/save_load.py` |
| 2 | **Integrante 2** | Jugador & Combate | Player, Input, Movimiento, Ataque, Proyectiles, Sistema de combate | `entities/player.py`, `entities/projectile.py`, `systems/combat.py`, `entities/entity.py` (base) |
| 3 | **Integrante 3** | Enemigos & IA | Enemy base, 3 tipos enemigos, Pathfinding, Boss final | `entities/enemy.py`, `entities/enemies/walker.py`, `entities/enemies/shooter.py`, `entities/enemies/charger.py`, `entities/boss.py`, `systems/pathfinding.py` |
| 4 | **Integrante 4** | Mundo & Niveles | Tilemap, Room, Dungeon, Puertas/Llaves, Level data | `world/tilemap.py`, `world/room.py`, `world/dungeon.py`, `world/level_data/` |
| 5 | **Integrante 5** | UI & UX | HUD, Menús, Game Over, Victory, Pause, Sonidos | `ui/hud.py`, `ui/menus.py`, `ui/dialogue.py`, integración `assets/sounds/` |
| 6 | **Integrante 6** | Assets & QA | Sprites, Animaciones, Sonidos, Testing, Bug tracking, Docs | `assets/` (organizado), `utils/animation.py`, `utils/debug.py`, README, testing manual |

---

## Desglose Detallado por Integrante

### 🎯 Integrante 1 - Líder Técnico / Core
**Semana 1:**
- [ ] `main.py` - Entry point, inicialización pygame, bucle principal
- [ ] `config.py` - Constantes: WIDTH, HEIGHT, FPS, TILE_SIZE, COLORS, LAYERS
- [ ] `core/game.py` - Clase Game, StateMachine (MENU, PLAYING, PAUSED, GAME_OVER, VICTORY)
- [ ] `core/camera.py` - Cámara que sigue al jugador, límites de mundo
- [ ] `core/events.py` - Event bus simple (publish/subscribe para colisiones, daño, pickups)
- [ ] Setup repo: `.gitignore`, `requirements.txt`, README inicial

**Semana 2-3:**
- [ ] `core/save_load.py` - Guardado/carga JSON (pos jugador, vidas, monedas, llaves, habitación actual)
- [ ] Integración continua: mergear PRs, resolver conflictos, builds
- [ ] Code review de todos los PRs

**Semana 4:**
- [ ] Build final con PyInstaller
- [ ] Documentación técnica final

---

### ⚔️ Integrante 2 - Jugador & Combate
**Semana 1:**
- [ ] `entities/entity.py` - Clase base: pos (Vector2), rect, sprite, hp, alive, update(dt), draw(surface)
- [ ] `entities/player.py` - Hereda Entity: input (WASD/arrows), movimiento 8 dirs, colisiones con walls
- [ ] Animaciones: idle, walk, attack, hurt, death (usar `utils/animation.py`)

**Semana 2:**
- [ ] Ataque espada: hitbox frontal, cooldown, animación
- [ ] Invulnerabilidad temporal (flash + sin daño 1s tras golpe)
- [ ] `entities/projectile.py` - Base para flechas/bolas (velocidad, daño, lifetime, owner)
- [ ] `systems/combat.py` - Funciones: `apply_damage(attacker, target, amount, knockback)`, `check_sword_hit()`

**Semana 3:**
- [ ] Stats: HP max, HP actual, ataque, defensa, velocidad
- [ ] Pickups: corazón (cura 1 HP), moneda (+1 rupia)
- [ ] Knockback al recibir daño

**Semana 4:**
- [ ] Balanceo: valores en `config.py`
- [ ] Testing de edge cases (paredes, esquinas, ataque diagonal)

---

### 👹 Integrante 3 - Enemigos & IA
**Semana 1:**
- [ ] `entities/enemy.py` - Clase base Enemy: patrol_points, state (IDLE, PATROL, CHASE, ATTACK), target
- [ ] `systems/pathfinding.py` - A* simple (grid-based) para persecución

**Semana 2:**
- [ ] `entities/enemies/walker.py` - Camina en patrón, persigue si ve jugador
- [ ] `entities/enemies/shooter.py` - Dispara proyectiles cada X seg, mantiene distancia
- [ ] `entities/enemies/charger.py` - Carga en línea recta tras wind-up, stun al chocar pared

**Semana 3:**
- [ ] `entities/boss.py` - Máquina de estados: FASE_1 → FASE_2 → FASE_3
  - Fase 1: Invoca walkers + dispara patrón radial
  - Fase 2: Carga rápida + área de efecto
  - Fase 3: Proyectiles teleguiados + velocidad aumentada
- [ ] Arena boss: room especial sin puertas hasta victoria

**Semana 4:**
- [ ] Tuning dificultad: HP, daño, timings por fase
- [ ] Death animation + drop llave jefe

---

### 🗺️ Integrante 4 - Mundo & Niveles
**Semana 1:**
- [ ] Decidir formato: **Tiled (.tmx + pytmx)** o **CSV casero**
- [ ] `world/tilemap.py` - Carga mapa, render por capas, colisión `walls` layer
- [ ] `world/level_data/` - Crear 4-6 habitaciones (archivos .tmx o .csv)

**Semana 2:**
- [ ] `world/room.py` - Clase Room: enemies[], pickups[], doors[], triggers[], spawn_point
- [ ] Sistema de transiciones: puerta → fade out → carga room destino → fade in

**Semana 3:**
- [ ] `world/dungeon.py` - Grafo de habitaciones, llaves/puertas, progresión lineal/ramificada
- [ ] Llaves: `pickup.key` → `inventory.add_key()` → `door.try_open()`
- [ ] Spawn points por habitación (player, enemigos)

**Semana 4:**
- [ ] Polish: decoración, variedad visual, testing flujo completo
- [ ] Minimapa opcional (HUD)

---

### 🖥️ Integrante 5 - UI & UX
**Semana 1:**
- [ ] `ui/hud.py` - Corazones (3 sprites: full/half/empty), contador monedas, llaves
- [ ] Fuente pixel art cargada desde `assets/fonts/`

**Semana 2:**
- [ ] `ui/menus.py` - MainMenu (Jugar, Controles, Salir), PauseMenu (Continuar, Reiniciar, Salir)
- [ ] `ui/game_over.py` - Pantalla Game Over + botón "Volver a empezar"
- [ ] `ui/victory.py` - Pantalla victoria + tiempo + stats

**Semana 3:**
- [ ] Integración sonidos: `assets/sounds/` (sfxr/bfxr)
  - jump, hit, enemy_death, coin, key, door_open, sword_swing, boss_hit
- [ ] Música loop (1-2 tracks libres)
- [ ] `ui/dialogue.py` - Sistema texto simple (opcional, para tutorial)

**Semana 4:**
- [ ] Polish: transiciones fade, screen shake al daño, particle effects simples
- [ ] Testing UX: legibilidad, flujo menús, controles intuitivos

---

### 🎨 Integrante 6 - Assets & QA
**Semana 1 (continuo):**
- [ ] Estructura `assets/`:
  ```
  assets/
  ├── sprites/
  │   ├── player/     # idle.png, walk_1-4.png, attack_1-3.png, hurt.png
  │   ├── enemies/    # walker/, shooter/, charger/, boss/
  │   ├── tiles/      # ground.png, wall.png, door.png, chest.png
  │   └── ui/         # heart_full.png, heart_empty.png, coin.png, key.png
  ├── sounds/         # .wav/.ogg (sfx + music)
  └── fonts/          # .ttf pixel art
  ```
- [ ] Placeholders día 1: rectángulos de colores para TODOS los sprites (permite trabajar al resto)

**Semana 2-3:**
- [ ] Sprites finales progresivos (prioridad: player → enemigos básicos → tiles → boss → UI)
- [ ] `utils/animation.py` - Clase Animation: frames, duration, loop, flip
- [ ] Sonidos generados con sfxr/bfxr + música libre (opengameart/itch.io)

**Semana 4 (QA intensivo):**
- [ ] Testing manual completo: checklist de 50+ casos
- [ ] Bug tracking: GitHub Issues con labels (bug/critical, bug/minor, feature)
- [ ] Regression testing tras cada merge
- [ ] README final: controles, cómo jugar, créditos, build instructions
- [ ] Video/demo gameplay 2 min para entrega

---

## Matriz de Dependencias Críticas (¡Leer antes de empezar!)

| Módulo | Requiere antes | Bloquea a |
|--------|----------------|-----------|
| `core/game.py` | `config.py` | Todos |
| `entities/entity.py` | `config.py` | Player, Enemy, Projectile, Pickup |
| `entities/player.py` | `entity.py`, `core/camera.py` | Combate, HUD, Mundo |
| `world/tilemap.py` | `config.py`, `assets/sprites/tiles/` | Room, Dungeon, Player colisiones |
| `systems/combat.py` | `entity.py`, `player.py`, `enemy.py` | Player ataque, Enemigos reciben daño |
| `ui/hud.py` | `player.stats` | - |
| `entities/boss.py` | `enemy.py`, `pathfinding.py`, `combat.py` | Dungeon (boss room) |

**Regla de oro:** Si tu módulo está en "Bloquea a", prioriza terminarlo. Si está en "Requiere antes", avisa al dueño cuando lo necesites.

---

## Checklist de Entrega por Integrante (Definición de "Done")

- [ ] Código en `main` via PR aprobado (1+ review)
- [ ] Sin warnings `ruff` / `flake8` / `mypy` (si config)
- [ ] Funciona en 640×480 y 960×720
- [ ] Probado con placeholders Y assets finales
- [ ] Documentado en README o docstrings públicas
- [ ] Commits atómicos y mensajes claros (`feat:`, `fix:`, `refactor:`)