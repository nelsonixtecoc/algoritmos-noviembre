# Tareas por Integrante - Wave Defense (Scope Reducido ~2000 líneas)

> **⚠️ CAMBIOS RECENTES (Noviembre 2026):**
> - Se eliminó el **sistema de partículas** (`systems/particles.py`, constantes `PARTICLE_*`, `LAYER_PARTICLES`).
> - Se eliminaron los **sonidos (SFX)** (`shoot_sound`, `reload_sound`, `empty_sound` en armas). Solo se deja música de fondo opcional para agregar después.
> - En su lugar, al terminar cada oleada aparece el estado **"Fin de la Oleada" (`WAVE_END`)** durante 3 segundos antes de pasar a la siguiente oleada.

## Asignación de Roles (6 Integrantes)

| # | Integrante | Rol | Módulos Responsables | Archivos Clave |
|---|------------|-----|----------------------|----------------|
| 1 | **Nelson** | Líder Técnico / Core | Game loop, State machine, EventBus, Save/Load, Build, Code Review | `main.py`, `config.py`, `core/game.py`, `core/events.py`, `core/save_load.py`, `utils/helpers.py` |
| 2 | **Fabiola** | Player & Weapons System | Player, Input, Armas (Strategy - 3 armas), Proyectiles, Sistema Combate | `entities/player.py`, `entities/weapons/*.py`, `entities/projectile.py`, `systems/combat.py`, `entities/entity.py` |
| 3 | **Lilian** | Enemies & Wave System | Enemigos (3 tipos), WaveManager (10 oleadas), Spawning data-driven | `entities/enemies/*.py`, `systems/wave_manager.py`, `config/waves.json` |
| 4 | **Zebedeo** | Barriers & Pickups | Barreras fijas (4 posiciones, HP, draw), Screen Shake, Sistema de Pickups | `entities/barrier.py`, `entities/pickup.py` |
| 5 | **Aron** | UI & Menus | HUD, Menús, Highscores, Game Over/Victoria input | `ui/hud.py`, `ui/menus.py`, `ui/game_over.py`, `systems/save_load.py` |
| 6 | **Leslie** | Assets & QA Lead | Sprites, Animaciones, Música de fondo (opcional), Testing, Bug Tracking, Docs, Video Demo | `assets/`, `utils/animation.py`, README, checklist QA |

---

## Desglose Detallado por Integrante

### 🎯 Integrante 1 - Nelson (Líder Técnico / Core)

**Semana 1:**
- [ ] `main.py` - Entry point, init pygame, instancia Game, bucle principal
- [ ] `config.py` - Constantes: WIDTH, HEIGHT, FPS, COLORS, LAYERS, BALANCE (velocidad player, daño base, etc.)
- [ ] `core/game.py` - Clase Game, StateMachine (MENU, PLAYING, WAVE_END, PAUSED, GAME_OVER, VICTORY), transiciones
- [ ] `core/events.py` - EventBus: subscribe, publish, process (colisiones, daño, muerte, pickup, wave_complete)
- [ ] `core/save_load.py` - JSON: highscores (top 5), stats totales, unlocks
- [ ] `utils/helpers.py` - clamp, lerp, angle_to, distance, load_spritesheet, random_spawn_point
- [ ] Setup repo: `.gitignore`, `requirements.txt` (pygame-ce), README inicial, pre-commit (ruff + black)

**Semana 2-3:**
- [ ] Integración continua: mergear PRs, resolver conflictos, builds semanales
- [ ] Code review de todos los PRs (mínimo 1 aprobación)
- [ ] Ajustar `config.py` tras playtests (balanceo)

**Semana 4-5:**
- [ ] Build final con PyInstaller (--onefile --noconsole --add-data assets)
- [ ] Documentación técnica final: arquitectura, patrones usados, decisiones
- [ ] Preparar material defensa oral: diagrama flujo game loop + event bus

---

### ⚔️ Integrante 2 - Fabiola (Player & Weapons System)

**Semana 1:**
- [ ] `entities/entity.py` - Clase base: pos (Vector2), vel, rect, hp, max_hp, alive, sprite, animation, update(dt), draw(surface, camera_offset)
- [ ] `entities/player.py` - Hereda Entity: input WASD (8 dirs), límites pantalla, switch arma (teclas 1-3), invulnerabilidad 1s (flash), hp=3, oro=0
- [ ] `entities/weapons/weapon.py` - Abstract base: cooldown, damage, spread, projectile_class, fire(pos, angle) → devuelve lista Projectile

**Semana 2:**
- [ ] `entities/weapons/pistol.py` - 1 bala, cooldown 300ms, daño 10, spread 0°
- [ ] `entities/weapons/shotgun.py` - 5 perdigones, cooldown 800ms, daño 6 c/u, spread ±15°
- [ ] `entities/weapons/rifle.py` - 1 bala rápida, cooldown 150ms, daño 8, spread 0°, perfora 1 enemigo
- [ ] `entities/projectile.py` - Base: pos, vel, damage, owner, lifetime, pierce, explode_on_death, update(dt), draw()
- [ ] `systems/combat.py` - `apply_damage(attacker, target, amount, knockback)`, `check_projectile_collisions(projectiles, enemies)`, `check_player_enemy_collision(player, enemies)`

**Semana 3:**
- [ ] Stats player: damage_mult, cooldown_mult, speed_mult, max_hp (modificables por upgrades)
- [ ] Knockback al recibir daño + invulnerabilidad flash
- [ ] Pickup oro al matar (EventBus: ENEMY_KILLED → Player.add_gold)

**Semana 4:**
- [ ] Balanceo: valores finales en `config.py`
- [ ] Testing edge cases: esquinas, disparo diagonal, cambio arma mid-cooldown

---

### 👹 Integrante 3 - Lilian (Enemies & Wave System)

**Semana 1:**
- [ ] `entities/enemies/enemy.py` - Base Enemy: target (base o player), state (IDLE, CHASE, ATTACK), speed, hp, damage, gold_value, update(dt), simple_pathfinding (vector directo evitando barreras básico)
- [ ] `entities/enemies/basic.py` - Standard: hp 30, speed 80, damage 1, gold 10
- [ ] `entities/enemies/tank.py` - HP 120, speed 40, damage 2, gold 25, resist knockback 50%
- [ ] `entities/enemies/speedy.py` - HP 15, speed 180, damage 1, gold 15, dodge chance 10%

**Semana 2:**
- [ ] `systems/wave_manager.py` - Lee `config/waves.json`, spawnea oleadas, timer entre oleadas, contador enemigos vivos, evento WAVE_COMPLETE
- [ ] `config/waves.json` - Oleadas 1-10: tipos, count, hp_mult, spawn_interval
- [ ] Integración WaveManager → Game.playing: spawnea en bordes pantalla (top/bottom/left/right aleatorio)

**Semana 3:**
- [ ] Tuning dificultad: HP, daño, timings por oleada en `waves.json`
- [ ] Death animations + drop oro (EventBus)

**Semana 4:**
- [ ] Testing visual: claridad feedback, no spam partículas

---

### 🧱 Integrante 4 - Zebedeo (Barriers & Pickups)

**Semana 1:**
- [x] `entities/barrier.py` - Sprite con HP (max 200), rect, draw_health_bar(), take_damage() — **solo 4 posiciones fijas** (usa `default_positions()`)
- [x] Enemigos priorizan barreras si en rango → atacan → si destruida, van a player/base
- [x] `entities/pickup.py` - Clase base `Pickup` (pos, rect, collides, apply, draw), `HealthPickup` (cura hasta max_hp) y `SpeedPickup` (sube velocidad) — **ya iniciado**

**Semana 2:**
- [x] Spawneo de pickups al matar enemigos (integrar con WaveManager / EventBus ENEMY_DIED)
- [x] Colisión player ↔ pickup y aplicación de efectos en game loop
- [x] Tiempo de vida / auto-desaparición de pickups no recogidos

**Semana 3:**
- [x] Screen shake en: player hit, wave complete

**Semana 4:**
- [x] Testing visual: claridad feedback (barreras y pickups)

  **Notas de prueba (2026-10-26, resolución 640×480):**

  - Los pickups de vida (verde) y velocidad (rojo) aparecen al morir enemigos.
  - Se recogen al tocarlos y aplican su efecto.
  - Desaparecen solos a los 10 segundos.
  - El screen shake se ve al completar una oleada y al recibir daño.
  - Pendiente: sprites finales de speed.png y repair.png (hoy son rectángulos).

---

### 🖥️ Integrante 5 - Aron (UI, Upgrades & Menus)

**Semana 1:**
- [ ] `ui/hud.py` - 3 corazones (sprites full/half/empty), ronda (wave 1/10), enemigos vivos, oro, icono arma actual (1-3) + cooldown bar
- [ ] Fuente pixel art cargada desde `assets/fonts/`

**Semana 2:**
- [ ] `ui/menus.py` - MainMenu (Jugar, Controles, Highscores, Salir), PauseMenu (Continuar, Reiniciar, Menú Principal, Salir)
- [ ] `ui/game_over.py` - Pantalla Game Over/Victoria compartida + input nombre (máx 12 chars, solo alfanumérico) → save highscore → volver a menú

**Semana 3:**
- [ ] Menús pulidos: transiciones fade in/out entre estados
- [ ] Highscores: top 5 persistente, muestra en MainMenu y Game Over

**Semana 4:**
- [ ] Polish: transiciones fade in/out entre estados
- [ ] Highscores: top 5 persistente, muestra en MainMenu y Game Over
- [ ] Testing UX: legibilidad, navegación teclado/mouse, controles intuitivos

---

### 🎨 Integrante 6 - Leslie (Assets & QA Lead)

**Semana 1 (continuo):**
- [ ] Estructura `assets/`:
  ```
  assets/
  ├── sprites/
  │   ├── player/        # idle.png, walk_1-4.png, shoot.png, hurt.png (3 armas)
  │   ├── enemies/       # basic/, tank/, speedy/
  │   ├── weapons/       # pistol.png, shotgun.png, rifle.png, projectiles/
  │   ├── barrier/       # barrier_1-4.png, barrier_destroyed.png
  │   ├── ui/            # heart_full.png, heart_empty.png, coin.png
  │   └── particles/     # spark.png, smoke.png
  ├── sounds/
  │   └── sfx/           # .wav/.ogg (shoot, hit, kill, coin, upgrade, wave, hurt)
  └── fonts/             # .ttf pixel art (ej. PressStart2P, Pixeloid)
  ```
- [ ] Placeholders día 1: rectángulos colores para TODOS sprites (permite trabajar al resto)

**Semana 2-3:**
- [ ] Sprites finales progresivos (prioridad: player → enemigos básicos → armas/proyectiles → barreras → UI → partículas)
- [ ] `utils/animation.py` - Clase Animation: frames (list[Surface]), duration, loop, flip_h, flip_v, get_frame(dt)
- [ ] Sonidos generados con sfxr/bfxr + música libre (opengameart/itch.io)

**Semana 4 (QA intensivo):**
- [ ] Testing manual completo: checklist 30+ casos (ver abajo)
- [ ] Bug tracking: GitHub Issues con labels (bug/critical, bug/minor, feature, balance)
- [ ] Regression testing tras cada merge
- [ ] README final: controles, cómo jugar, arquitectura, patrones, créditos, build instructions
- [ ] Video/demo gameplay 2 min para entrega (OBS, 60 FPS)

**Semana 5:**
- [ ] Pre-defensa: cada integrante ensaya explicar su módulo (3-5 min)
- [ ] Checklist final: 0 bugs críticos, build funciona en PC limpio, docs completas

---

## Matriz de Dependencias Críticas (¡Leer antes de empezar!)

| Módulo | Requiere antes | Bloquea a | Semana objetivo |
|--------|----------------|-----------|-----------------|
| `config.py` | — | Todos | 1 |
| `core/events.py` | `config.py` | Player, Enemies, Combat, Particles, WaveManager | 1 |
| `core/game.py` | `events.py`, `config.py` | Todos | 1 |
| `entities/entity.py` | `config.py`, `events.py` | Player, Enemy, Projectile, Barrier | 1 |
| `entities/player.py` | `entity.py`, `weapons/weapon.py` | Combat, HUD, Upgrades | 1-2 |
| `entities/weapons/weapon.py` + 3 armas | `entity.py`, `projectile.py` | Player, Combat | 2 |
| `entities/projectile.py` | `entity.py` | Weapons, Combat | 2 |
| `entities/enemies/enemy.py` | `entity.py` | Todos enemigos, WaveManager | 1-2 |
| `systems/wave_manager.py` | `enemies/`, `config/waves.json` | Game loop playing | 2 |
| `systems/combat.py` | `player.py`, `enemies/`, `projectile.py` | — | 2 |
| `entities/barrier.py` | `entity.py` | Enemies (target) | 2 |
| `core/save_load.py` | `config.py` | Highscores, Game Over | 4 |
| `ui/menus.py` + `ui/game_over.py` | `save_load.py` | — | 4 |

**Regla de oro:** Si tu módulo está en "Bloquea a", prioriza terminarlo. Si está en "Requiere antes", avisa al dueño cuando lo necesites.

---

## Checklist de Entrega por Integrante (Definición de "Done")

- [ ] Código en `main` via PR aprobado (1+ review)
- [ ] Sin warnings `ruff` / `flake8` / `mypy` (si config)
- [ ] Funciona en 640×480
- [ ] Probado con placeholders Y assets finales
- [ ] Documentado en README o docstrings públicas
- [ ] Commits atómicos y mensajes claros (`feat:`, `fix:`, `refactor:`)
- [ ] **Puede explicar su módulo en 3-5 min** (diagrama + código clave + bug resuelto)

---

## Checklist QA (Leslie - Semana 4-5)

### Funcionalidad Core
- [ ] Menú → Jugar → Playing → Pause → Continuar funciona
- [ ] Player: movimiento 8 dirs, límites, switch 3 armas, disparo, cooldown
- [ ] 3 vidas: pierde 1 al tocar enemigo, invulnerabilidad 1s, Game Over en 0
- [ ] Oleadas 1-10: spawnean correctamente, contador enemigos vivos baja al matar
- [ ] Wave 5: Boss aparece, 3 fases funcionan, weak point vulnerable
- [ ] Enemigos: 3 tipos (Basic, Tank, Speedy) + 1 Boss, comportamientos distintos, mueren, dan oro
- [ ] Barreras: 4 fijas, enemigos las atacan, HP visible
- [ ] Highscores: guarda top 5, input nombre Game Over/Victoria, muestra en menú
- [ ] Victoria: oleada 10 completada → pantalla victoria (reusa Game Over) → highscore

### Visual / Audio
- [ ] Assets finales integrados (no placeholders)
- [ ] Screen shake en hits y muertes
- [ ] Animaciones fluidas (player, enemigos, boss)
- [ ] Música de fondo (opcional, integrar si hay tiempo)
- [ ] HUD legible: vidas, ronda (1/10), oro, arma (1-3), cooldown, enemigos

### Técnico
- [ ] 60 FPS estables (sin drops >5 frames)
- [ ] Sin memory leaks
- [ ] Build .exe funciona en PC sin Python
- [ ] Git history limpio (commits atómicos, mensajes claros)

### Documentación
- [ ] README completo
- [ ] Diagrama arquitectura (draw.io / papel foto)
- [ ] Video 2 min gameplay